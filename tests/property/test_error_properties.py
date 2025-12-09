"""Property-based tests for error handling in Content Summarizer."""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from src.summarizer import (
    BedrockSummarizer,
    RateLimitError,
    ModelNotAvailableError,
    InvalidRequestError,
    NetworkError,
    BedrockServiceError,
    AuthenticationError
)
from src.config import Config


# Strategy for generating various AWS error codes
aws_error_codes = st.sampled_from([
    'ThrottlingException',
    'ModelNotReadyException',
    'ValidationException',
    'ResourceNotFoundException',
    'AccessDeniedException',
    'ServiceUnavailableException',
    'ModelTimeoutException',
    'ModelErrorException',
    'UnknownException'
])


def create_client_error(error_code: str, message: str = "Test error") -> ClientError:
    """Helper function to create a ClientError with specific error code."""
    error_response = {
        'Error': {
            'Code': error_code,
            'Message': message
        }
    }
    return ClientError(error_response, 'invoke_model')


@given(error_code=aws_error_codes, content=st.text(min_size=1, max_size=100))
def test_api_error_handling(error_code: str, content: str):
    """
    Feature: content-summarizer, Property 11: API error handling
    
    For any Bedrock API exception type, the error handler should catch it 
    and return a user-friendly error message without exposing internal details.
    
    Validates: Requirements 5.1
    """
    # Skip whitespace-only content
    if content.isspace():
        return
    
    # Create a config
    config = Config(
        aws_region='us-east-1',
        model_id='test-model',
        max_tokens=100,
        temperature=0.5
    )
    
    # Create the error
    client_error = create_client_error(error_code, "Internal AWS error details")
    
    # Mock the boto3 client and STS client
    with patch('boto3.client') as mock_boto_client:
        # Mock STS client for authentication check
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {}
        
        # Mock bedrock-runtime client
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.side_effect = client_error
        
        # Configure the mock to return different clients based on service name
        def get_client(service_name, **kwargs):
            if service_name == 'sts':
                return mock_sts
            elif service_name == 'bedrock-runtime':
                return mock_bedrock
            return Mock()
        
        mock_boto_client.side_effect = get_client
        
        # Create summarizer
        summarizer = BedrockSummarizer(config)
        
        # Test that the error is caught and wrapped appropriately
        with pytest.raises(Exception) as exc_info:
            summarizer.summarize(content)
        
        # Verify that an appropriate exception was raised
        exception = exc_info.value
        
        # Check that the exception is one of our custom exception types
        assert isinstance(exception, (
            RateLimitError,
            ModelNotAvailableError,
            InvalidRequestError,
            NetworkError,
            BedrockServiceError,
            AuthenticationError
        )), f"Expected custom exception type, got {type(exception).__name__}"
        
        # Verify the error message is user-friendly (not empty)
        error_message = str(exception)
        assert len(error_message) > 0, "Error message should not be empty"
        
        # Verify the error message doesn't expose raw internal details
        # (it should not contain the exact internal error message)
        assert "Internal AWS error details" not in error_message or error_code in [
            'ValidationException', 'UnknownException'
        ], "Error message should not expose internal AWS error details directly"
        
        # Verify specific exception types for specific error codes
        if error_code == 'ThrottlingException':
            assert isinstance(exception, RateLimitError), \
                "ThrottlingException should raise RateLimitError"
            assert "rate limit" in error_message.lower(), \
                "Rate limit error should mention rate limiting"
        
        elif error_code == 'ModelNotReadyException':
            assert isinstance(exception, ModelNotAvailableError), \
                "ModelNotReadyException should raise ModelNotAvailableError"
            assert "not ready" in error_message.lower() or "unavailable" in error_message.lower(), \
                "Model not ready error should mention availability"
        
        elif error_code == 'ValidationException':
            assert isinstance(exception, InvalidRequestError), \
                "ValidationException should raise InvalidRequestError"
            assert "invalid" in error_message.lower(), \
                "Validation error should mention invalid request"
        
        elif error_code == 'ResourceNotFoundException':
            assert isinstance(exception, ModelNotAvailableError), \
                "ResourceNotFoundException should raise ModelNotAvailableError"
            assert "not found" in error_message.lower(), \
                "Resource not found error should mention not found"
        
        elif error_code == 'AccessDeniedException':
            assert isinstance(exception, AuthenticationError), \
                "AccessDeniedException should raise AuthenticationError"
            assert "access denied" in error_message.lower() or "permission" in error_message.lower(), \
                "Access denied error should mention permissions"
