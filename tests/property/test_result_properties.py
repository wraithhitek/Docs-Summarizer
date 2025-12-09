"""Property-based tests for summarization results."""

from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json
import pytest

from src.summarizer import BedrockSummarizer, SummaryResult
from src.config import Config


# Strategy for generating valid content strings
@st.composite
def valid_content(draw):
    """Generate valid non-empty, non-whitespace content."""
    # Generate content with at least one non-whitespace character
    content = draw(st.text(min_size=1, max_size=10000))
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


# Feature: content-summarizer, Property 8: Result type consistency
# For any successful summarization operation, the result should contain a summary field of type string
@settings(max_examples=100, deadline=None)
@given(
    content=valid_content(),
    response_data=mock_bedrock_response()
)
def test_result_type_consistency(content, response_data):
    """
    Feature: content-summarizer, Property 8: Result type consistency
    Validates: Requirements 4.1
    
    Property: For any successful summarization operation, the result should contain 
    a summary field of type string.
    """
    mock_response, expected_summary = response_data
    
    # Create a config
    config = Config(
        aws_region='us-east-1',
        model_id='anthropic.claude-3-haiku-20240307-v1:0',
        max_tokens=1024,
        temperature=0.5
    )
    
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
        
        # Mock Bedrock invoke_model
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        # Create summarizer and call summarize
        summarizer = BedrockSummarizer(config)
        result = summarizer.summarize(content)
        
        # Verify the result has a summary field
        assert hasattr(result, 'summary'), "Result should have a 'summary' attribute"
        
        # Verify the summary is a string
        assert isinstance(result.summary, str), \
            f"Expected summary to be a string, got {type(result.summary).__name__}"
        
        # Verify the summary matches what was returned by the API
        assert result.summary == expected_summary, \
            f"Expected summary '{expected_summary}', but got '{result.summary}'"




# Feature: content-summarizer, Property 9: Metadata completeness
# For any summarization result, it should include all required metadata fields
@settings(max_examples=100, deadline=None)
@given(
    content=valid_content(),
    response_data=mock_bedrock_response()
)
def test_metadata_completeness(content, response_data):
    """
    Feature: content-summarizer, Property 9: Metadata completeness
    Validates: Requirements 4.3
    
    Property: For any summarization result, it should include all required metadata fields:
    original_length, summary_length, model_used, and timestamp.
    """
    mock_response, expected_summary = response_data
    
    # Create a config
    config = Config(
        aws_region='us-east-1',
        model_id='anthropic.claude-3-haiku-20240307-v1:0',
        max_tokens=1024,
        temperature=0.5
    )
    
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
        
        # Mock Bedrock invoke_model
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        # Create summarizer and call summarize
        summarizer = BedrockSummarizer(config)
        result = summarizer.summarize(content)
        
        # Verify all required metadata fields are present
        assert hasattr(result, 'original_length'), "Result should have 'original_length' field"
        assert hasattr(result, 'summary_length'), "Result should have 'summary_length' field"
        assert hasattr(result, 'model_used'), "Result should have 'model_used' field"
        assert hasattr(result, 'timestamp'), "Result should have 'timestamp' field"
        
        # Verify the types of metadata fields
        assert isinstance(result.original_length, int), \
            f"original_length should be int, got {type(result.original_length).__name__}"
        assert isinstance(result.summary_length, int), \
            f"summary_length should be int, got {type(result.summary_length).__name__}"
        assert isinstance(result.model_used, str), \
            f"model_used should be str, got {type(result.model_used).__name__}"
        assert isinstance(result.timestamp, datetime), \
            f"timestamp should be datetime, got {type(result.timestamp).__name__}"
        
        # Verify the values are sensible
        assert result.original_length > 0, "original_length should be positive"
        assert result.summary_length > 0, "summary_length should be positive"
        assert result.model_used == config.model_id, \
            f"model_used should be '{config.model_id}', got '{result.model_used}'"
        assert result.summary_length == len(expected_summary), \
            f"summary_length should match actual summary length"


# Feature: content-summarizer, Property 10: Result structure consistency
# For any summarization result, the structure should match the SummaryResult dataclass format
@settings(max_examples=100, deadline=None)
@given(
    content=valid_content(),
    response_data=mock_bedrock_response()
)
def test_result_structure(content, response_data):
    """
    Feature: content-summarizer, Property 10: Result structure consistency
    Validates: Requirements 4.4
    
    Property: For any summarization result, the structure should match the SummaryResult 
    dataclass format with proper field types.
    """
    mock_response, expected_summary = response_data
    
    # Create a config
    config = Config(
        aws_region='us-east-1',
        model_id='anthropic.claude-3-haiku-20240307-v1:0',
        max_tokens=1024,
        temperature=0.5
    )
    
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
        
        # Mock Bedrock invoke_model
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        # Create summarizer and call summarize
        summarizer = BedrockSummarizer(config)
        result = summarizer.summarize(content)
        
        # Verify the result is a SummaryResult instance
        assert isinstance(result, SummaryResult), \
            f"Expected result to be SummaryResult, got {type(result).__name__}"
        
        # Verify the structure matches the dataclass definition
        # Check that all expected fields exist with correct types
        assert isinstance(result.summary, str), "summary field should be str"
        assert isinstance(result.original_length, int), "original_length field should be int"
        assert isinstance(result.summary_length, int), "summary_length field should be int"
        assert isinstance(result.model_used, str), "model_used field should be str"
        assert isinstance(result.timestamp, datetime), "timestamp field should be datetime"
        
        # Verify no unexpected fields (dataclass should only have these 5 fields)
        expected_fields = {'summary', 'original_length', 'summary_length', 'model_used', 'timestamp'}
        actual_fields = set(result.__dict__.keys())
        assert actual_fields == expected_fields, \
            f"Result structure mismatch. Expected fields: {expected_fields}, got: {actual_fields}"
