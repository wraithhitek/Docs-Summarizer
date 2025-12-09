"""Property-based tests for request building."""

import os
from hypothesis import given, strategies as st, settings
import pytest
import string

from src.config import Config
from src.summarizer import BedrockSummarizer


# Strategy for non-empty, non-whitespace strings
def non_empty_text(min_size=1, max_size=50):
    """Generate non-empty strings that aren't just whitespace."""
    return st.text(
        alphabet=string.ascii_letters + string.digits + '-_.',
        min_size=min_size,
        max_size=max_size
    )


# Feature: content-summarizer, Property 6: Request parameter inclusion
# For any configuration with model parameters (max_tokens, temperature), the built request should include those exact parameter values
@settings(max_examples=100, deadline=None)
@given(
    max_tokens=st.integers(min_value=1, max_value=100000),
    temperature=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    content=st.text(min_size=1, max_size=1000)
)
def test_request_parameter_inclusion(max_tokens, temperature, content):
    """
    Feature: content-summarizer, Property 6: Request parameter inclusion
    Validates: Requirements 3.3, 6.4
    
    Property: For any configuration with model parameters (max_tokens, temperature),
    the built request should include those exact parameter values.
    """
    # Skip whitespace-only content
    if content.isspace():
        return
    
    # Create a config with the generated parameters
    config = Config(
        aws_region='us-east-1',
        model_id='anthropic.claude-3-haiku-20240307-v1:0',
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    # Create a minimal BedrockSummarizer instance without AWS initialization
    # We're only testing request building, not actual API calls
    summarizer = object.__new__(BedrockSummarizer)
    summarizer.config = config
    
    # Build the request
    request = summarizer._build_request(content)
    
    # Verify the request includes the exact parameter values from config
    assert 'max_tokens' in request, "Request must include max_tokens parameter"
    assert request['max_tokens'] == max_tokens, f"Expected max_tokens={max_tokens}, got {request['max_tokens']}"
    
    assert 'temperature' in request, "Request must include temperature parameter"
    assert request['temperature'] == temperature, f"Expected temperature={temperature}, got {request['temperature']}"
    
    # Verify the request follows Claude message API format
    assert 'anthropic_version' in request, "Request must include anthropic_version"
    assert request['anthropic_version'] == "bedrock-2023-05-31"
    
    assert 'messages' in request, "Request must include messages array"
    assert isinstance(request['messages'], list), "messages must be a list"
    assert len(request['messages']) > 0, "messages must not be empty"
    
    # Verify the message structure
    message = request['messages'][0]
    assert 'role' in message, "Message must have a role"
    assert message['role'] == 'user', "Message role should be 'user'"
    assert 'content' in message, "Message must have content"
    assert content in message['content'], "Message content should include the input content"
    
    # Verify parameter types
    assert isinstance(request['max_tokens'], int), "max_tokens must be an integer"
    assert isinstance(request['temperature'], float), "temperature must be a float"
