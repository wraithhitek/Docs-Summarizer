"""Property-based tests for file input functionality."""

from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import json
import tempfile
import os

from src.summarizer import BedrockSummarizer, SummaryResult
from src.config import Config


# Strategy for generating valid content strings
@st.composite
def valid_content(draw):
    """Generate valid non-empty, non-whitespace content."""
    # Generate content with at least one non-whitespace character
    content = draw(st.text(min_size=1, max_size=5000))
    # Ensure it's not all whitespace
    if content.isspace() or not content:
        content = "Valid content " + content
    return content


# Strategy for generating valid Bedrock API responses
@st.composite
def mock_bedrock_response(draw):
    """Generate a mock Bedrock API response."""
    summary_text = draw(st.text(min_size=1, max_size=1000))
    
    response_body = {
        "content": [
            {
                "type": "text",
                "text": summary_text
            }
        ],
        "usage": {
            "input_tokens": draw(st.integers(min_value=1, max_value=10000)),
            "output_tokens": draw(st.integers(min_value=1, max_value=5000))
        }
    }
    
    # Create a mock response object
    mock_response = {
        'body': MagicMock()
    }
    mock_response['body'].read.return_value = json.dumps(response_body).encode('utf-8')
    
    return mock_response, summary_text


# Feature: content-summarizer, Property 4: Input source equivalence
# For any content string, reading it from a file and passing it directly as a string should produce equivalent results
@settings(max_examples=100, deadline=None)
@given(
    content=valid_content(),
    response_data=mock_bedrock_response()
)
def test_input_source_equivalence(content, response_data):
    """
    Feature: content-summarizer, Property 4: Input source equivalence
    Validates: Requirements 1.5
    
    Property: For any content string, reading it from a file and passing it directly 
    as a string should produce equivalent results.
    """
    mock_response, expected_summary = response_data
    
    # Create a config
    config = Config(
        aws_region='us-east-1',
        model_id='anthropic.claude-3-haiku-20240307-v1:0',
        max_tokens=1024,
        temperature=0.5
    )
    
    # Create a temporary file with the content
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Mock the boto3 client and STS client
        with patch('boto3.client') as mock_boto_client:
            # Create mock clients
            mock_bedrock_client = Mock()
            mock_sts_client = Mock()
            
            # Configure boto3.client to return appropriate mocks
            def client_side_effect(service_name, **kwargs):
                if service_name == 'bedrock-runtime':
                    return mock_bedrock_client
                elif service_name == 'sts':
                    return mock_sts_client
                return Mock()
            
            mock_boto_client.side_effect = client_side_effect
            
            # Mock STS get_caller_identity (for credential validation)
            mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
            
            # Mock Bedrock invoke_model to return the same response for both calls
            mock_bedrock_client.invoke_model.return_value = mock_response
            
            # Create summarizer
            summarizer = BedrockSummarizer(config)
            
            # Test 1: Summarize using direct string input
            result_from_string = summarizer.summarize(content)
            
            # Reset the mock to ensure we get the same response again
            mock_response_copy = {
                'body': MagicMock()
            }
            mock_response_copy['body'].read.return_value = mock_response['body'].read.return_value
            mock_bedrock_client.invoke_model.return_value = mock_response_copy
            
            # Test 2: Summarize using file input
            result_from_file = summarizer.summarize_file(tmp_file_path)
            
            # Verify that both results are equivalent
            assert isinstance(result_from_string, SummaryResult), \
                "Result from string should be a SummaryResult"
            assert isinstance(result_from_file, SummaryResult), \
                "Result from file should be a SummaryResult"
            
            # Compare the key fields that should be equivalent
            # The summary text should be identical regardless of input source
            assert result_from_string.summary == result_from_file.summary, \
                "Summary text should be the same regardless of input source"
            
            # The summary length should be the same (it's derived from the summary)
            assert result_from_string.summary_length == result_from_file.summary_length, \
                f"Summary length should be the same: string={result_from_string.summary_length}, file={result_from_file.summary_length}"
            
            # The model used should be the same
            assert result_from_string.model_used == result_from_file.model_used, \
                "Model used should be the same regardless of input source"
            
            # Note: original_length may differ slightly due to line ending normalization
            # when reading from files (e.g., \r\n vs \n on Windows), but this is expected
            # and doesn't affect the quality of the summary. The important thing is that
            # the same semantic content produces the same summary.
            
            # Verify that the API was called twice
            assert mock_bedrock_client.invoke_model.call_count == 2, \
                "invoke_model should be called exactly twice"
            
            # Extract the request bodies from both calls
            call_args_list = mock_bedrock_client.invoke_model.call_args_list
            
            first_call_body = json.loads(call_args_list[0][1]['body'])
            second_call_body = json.loads(call_args_list[1][1]['body'])
            
            # The content sent to the API should be semantically equivalent
            # (after normalization of line endings which happens during file I/O)
            first_content = first_call_body['messages'][0]['content']
            second_content = second_call_body['messages'][0]['content']
            
            # Normalize line endings for comparison since file I/O may normalize them
            first_normalized = first_content.replace('\r\n', '\n').replace('\r', '\n')
            second_normalized = second_content.replace('\r\n', '\n').replace('\r', '\n')
            
            assert first_normalized == second_normalized, \
                "The content sent to the API should be semantically equivalent for both string and file input"
            
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
