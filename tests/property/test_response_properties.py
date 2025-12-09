"""Property-based tests for response parsing."""

from hypothesis import given, strategies as st, settings
import pytest

from src.summarizer import BedrockSummarizer, ResponseParseError


# Strategy for generating valid Bedrock API response structures
@st.composite
def valid_bedrock_response(draw):
    """Generate a valid Bedrock API response structure.
    
    A valid response has the structure:
    {
        "content": [
            {
                "type": "text",
                "text": "Summary text here..."
            }
        ],
        "usage": {
            "input_tokens": 150,
            "output_tokens": 75
        }
    }
    """
    # Generate the summary text (non-empty string)
    summary_text = draw(st.text(min_size=1, max_size=1000))
    
    # Generate optional additional content items
    num_content_items = draw(st.integers(min_value=1, max_value=5))
    
    content_items = []
    for i in range(num_content_items):
        if i == 0:
            # First item contains the actual summary
            content_items.append({
                "type": "text",
                "text": summary_text
            })
        else:
            # Additional items (if any)
            content_items.append({
                "type": "text",
                "text": draw(st.text(max_size=100))
            })
    
    # Generate usage statistics
    input_tokens = draw(st.integers(min_value=1, max_value=100000))
    output_tokens = draw(st.integers(min_value=1, max_value=10000))
    
    response = {
        "content": content_items,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    }
    
    return response, summary_text


# Feature: content-summarizer, Property 7: Response parsing correctness
# For any valid Bedrock API response structure, the parser should correctly extract the summary text
@settings(max_examples=100, deadline=None)
@given(
    response_data=valid_bedrock_response()
)
def test_response_parsing_correctness(response_data):
    """
    Feature: content-summarizer, Property 7: Response parsing correctness
    Validates: Requirements 3.4
    
    Property: For any valid Bedrock API response structure, the parser should correctly 
    extract the summary text from the response content.
    """
    response, expected_summary = response_data
    
    # Create a minimal BedrockSummarizer instance without AWS initialization
    # We're only testing response parsing, not actual API calls
    summarizer = object.__new__(BedrockSummarizer)
    
    # Parse the response
    extracted_summary = summarizer._parse_response(response)
    
    # Verify the extracted summary matches the expected text
    assert extracted_summary == expected_summary, \
        f"Expected summary '{expected_summary}', but got '{extracted_summary}'"
    
    # Verify the result is a string
    assert isinstance(extracted_summary, str), \
        f"Expected summary to be a string, got {type(extracted_summary).__name__}"
