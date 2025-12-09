"""Property-based tests for configuration management."""

import os
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
import string
from unittest.mock import patch, MagicMock

from src.config import Config, ConfigurationError
from src.summarizer import BedrockSummarizer


# Strategy for non-empty, non-whitespace strings
def non_empty_text(min_size=1, max_size=50):
    """Generate non-empty strings that aren't just whitespace."""
    # Use alphanumeric and common punctuation, ensuring at least one non-whitespace char
    return st.text(
        alphabet=string.ascii_letters + string.digits + '-_.',
        min_size=min_size,
        max_size=max_size
    )


# Feature: content-summarizer, Property 13: Configuration loading correctness
# For any valid configuration data (as dict or env vars), the Config class should load all fields correctly with proper type conversion
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    aws_region=non_empty_text(min_size=1, max_size=50),
    model_id=non_empty_text(min_size=1, max_size=100),
    max_tokens=st.integers(min_value=1, max_value=100000),
    temperature=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_config_loading_correctness(aws_region, model_id, max_tokens, temperature):
    """
    Feature: content-summarizer, Property 13: Configuration loading correctness
    Validates: Requirements 6.1
    
    Property: For any valid configuration data, the Config class should load all 
    fields correctly with proper type conversion.
    """
    # Save original environment variables
    original_env = {
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'BEDROCK_MODEL_ID': os.environ.get('BEDROCK_MODEL_ID'),
        'MAX_TOKENS': os.environ.get('MAX_TOKENS'),
        'TEMPERATURE': os.environ.get('TEMPERATURE')
    }
    
    try:
        # Set environment variables with the generated values
        os.environ['AWS_REGION'] = aws_region
        os.environ['BEDROCK_MODEL_ID'] = model_id
        os.environ['MAX_TOKENS'] = str(max_tokens)
        os.environ['TEMPERATURE'] = str(temperature)
        
        # Load configuration from environment
        config = Config.from_env()
        
        # Verify all fields are loaded correctly with proper types
        assert config.aws_region == aws_region
        assert config.model_id == model_id
        assert config.max_tokens == max_tokens
        assert isinstance(config.max_tokens, int)
        assert config.temperature == temperature
        assert isinstance(config.temperature, float)
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


# Feature: content-summarizer, Property 15: Default configuration fallback
# For any missing configuration field, the Config class should provide a sensible default value
@settings(max_examples=100)
@given(
    # Generate a subset of fields to omit (0 to 4 fields can be missing)
    omit_aws_region=st.booleans(),
    omit_model_id=st.booleans(),
    omit_max_tokens=st.booleans(),
    omit_temperature=st.booleans()
)
def test_default_configuration_fallback(omit_aws_region, omit_model_id, omit_max_tokens, omit_temperature):
    """
    Feature: content-summarizer, Property 15: Default configuration fallback
    Validates: Requirements 6.5
    
    Property: For any missing configuration field, the Config class should provide 
    a sensible default value.
    """
    # Save original environment variables
    original_env = {
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'BEDROCK_MODEL_ID': os.environ.get('BEDROCK_MODEL_ID'),
        'MAX_TOKENS': os.environ.get('MAX_TOKENS'),
        'TEMPERATURE': os.environ.get('TEMPERATURE')
    }
    
    try:
        # Clear all config-related environment variables first
        for key in ['AWS_REGION', 'BEDROCK_MODEL_ID', 'MAX_TOKENS', 'TEMPERATURE']:
            os.environ.pop(key, None)
        
        # Set only the fields that should NOT be omitted
        if not omit_aws_region:
            os.environ['AWS_REGION'] = 'us-west-2'
        if not omit_model_id:
            os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-sonnet-20240229-v1:0'
        if not omit_max_tokens:
            os.environ['MAX_TOKENS'] = '2048'
        if not omit_temperature:
            os.environ['TEMPERATURE'] = '0.7'
        
        # Load configuration from environment
        config = Config.from_env()
        
        # Verify that missing fields get default values
        if omit_aws_region:
            assert config.aws_region == 'us-east-1', "Default AWS region should be us-east-1"
        else:
            assert config.aws_region == 'us-west-2'
        
        if omit_model_id:
            assert config.model_id == 'anthropic.claude-3-haiku-20240307-v1:0', "Default model ID should be claude-3-haiku"
        else:
            assert config.model_id == 'anthropic.claude-3-sonnet-20240229-v1:0'
        
        if omit_max_tokens:
            assert config.max_tokens == 1024, "Default max_tokens should be 1024"
        else:
            assert config.max_tokens == 2048
        
        if omit_temperature:
            assert config.temperature == 0.5, "Default temperature should be 0.5"
        else:
            assert config.temperature == 0.7
        
        # Verify all fields have valid types
        assert isinstance(config.aws_region, str)
        assert isinstance(config.model_id, str)
        assert isinstance(config.max_tokens, int)
        assert isinstance(config.temperature, float)
        
        # Verify defaults are sensible (within valid ranges)
        assert config.max_tokens > 0
        assert 0 <= config.temperature <= 1
        assert len(config.aws_region) > 0
        assert len(config.model_id) > 0
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value



# Feature: content-summarizer, Property 14: Model ID application
# For any valid model ID specified in configuration, that exact model ID should be used in the Bedrock API request
@settings(max_examples=100)
@given(
    model_id=non_empty_text(min_size=1, max_size=100)
)
def test_model_id_application(model_id):
    """
    Feature: content-summarizer, Property 14: Model ID application
    Validates: Requirements 6.3
    
    Property: For any valid model ID specified in configuration, that exact model ID 
    should be used in the Bedrock API request.
    """
    # Save original environment variables
    original_env = {
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'BEDROCK_MODEL_ID': os.environ.get('BEDROCK_MODEL_ID'),
        'MAX_TOKENS': os.environ.get('MAX_TOKENS'),
        'TEMPERATURE': os.environ.get('TEMPERATURE')
    }
    
    try:
        # Set environment variables with defaults except for model_id
        os.environ['AWS_REGION'] = 'us-east-1'
        os.environ['BEDROCK_MODEL_ID'] = model_id
        os.environ['MAX_TOKENS'] = '1024'
        os.environ['TEMPERATURE'] = '0.5'
        
        # Load configuration from environment
        config = Config.from_env()
        
        # Verify that the exact model ID is stored in the configuration
        assert config.model_id == model_id, f"Expected model_id to be {model_id}, but got {config.model_id}"
        
        # Verify the model_id is a string (required for API requests)
        assert isinstance(config.model_id, str), "model_id must be a string type"
        
        # Verify the model_id is non-empty (required for valid API requests)
        assert len(config.model_id) > 0, "model_id cannot be empty"
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value



# Feature: content-summarizer, Property 5: Configuration region application
# For any valid AWS region string in configuration, the Bedrock client should be initialized with that region
@settings(max_examples=100)
@given(
    aws_region=st.sampled_from([
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-west-2', 'eu-central-1',
        'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1',
        'ca-central-1', 'sa-east-1'
    ])
)
def test_configuration_region_application(aws_region):
    """
    Feature: content-summarizer, Property 5: Configuration region application
    Validates: Requirements 2.3, 6.2
    
    Property: For any valid AWS region string in configuration, the Bedrock client 
    should be initialized with that region.
    """
    # Save original environment variables
    original_env = {
        'AWS_REGION': os.environ.get('AWS_REGION'),
        'BEDROCK_MODEL_ID': os.environ.get('BEDROCK_MODEL_ID'),
        'MAX_TOKENS': os.environ.get('MAX_TOKENS'),
        'TEMPERATURE': os.environ.get('TEMPERATURE')
    }
    
    try:
        # Set environment variables with the generated region
        os.environ['AWS_REGION'] = aws_region
        os.environ['BEDROCK_MODEL_ID'] = 'anthropic.claude-3-haiku-20240307-v1:0'
        os.environ['MAX_TOKENS'] = '1024'
        os.environ['TEMPERATURE'] = '0.5'
        
        # Load configuration from environment
        config = Config.from_env()
        
        # Verify the region is stored correctly in config
        assert config.aws_region == aws_region, f"Expected aws_region to be {aws_region}, but got {config.aws_region}"
        
        # Mock boto3.client to verify it's called with the correct region
        with patch('src.summarizer.boto3.client') as mock_boto_client:
            # Create mock clients for both bedrock-runtime and sts
            mock_bedrock_client = MagicMock()
            mock_sts_client = MagicMock()
            mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
            
            # Configure the mock to return different clients based on service name
            def client_side_effect(service_name, region_name=None):
                if service_name == 'bedrock-runtime':
                    return mock_bedrock_client
                elif service_name == 'sts':
                    return mock_sts_client
                return MagicMock()
            
            mock_boto_client.side_effect = client_side_effect
            
            # Initialize the BedrockSummarizer with the config
            summarizer = BedrockSummarizer(config)
            
            # Verify boto3.client was called with the correct region for bedrock-runtime
            bedrock_calls = [call for call in mock_boto_client.call_args_list 
                           if call[0][0] == 'bedrock-runtime']
            assert len(bedrock_calls) > 0, "boto3.client should be called for bedrock-runtime"
            
            # Check that the region_name parameter matches our configured region
            bedrock_call = bedrock_calls[0]
            assert bedrock_call[1]['region_name'] == aws_region, \
                f"Expected bedrock-runtime client to be initialized with region {aws_region}, " \
                f"but got {bedrock_call[1].get('region_name')}"
            
            # Also verify sts client was called with the same region
            sts_calls = [call for call in mock_boto_client.call_args_list 
                        if call[0][0] == 'sts']
            assert len(sts_calls) > 0, "boto3.client should be called for sts"
            
            sts_call = sts_calls[0]
            assert sts_call[1]['region_name'] == aws_region, \
                f"Expected sts client to be initialized with region {aws_region}, " \
                f"but got {sts_call[1].get('region_name')}"
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value



# Feature: content-summarizer, Property 12: Invalid parameter rejection
# For any invalid model parameter values (negative max_tokens, temperature outside 0-1 range), validation should reject them before making API calls
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    # Generate one invalid parameter at a time
    invalid_case=st.one_of(
        # Invalid max_tokens cases
        st.tuples(
            st.just('max_tokens'),
            st.integers(max_value=0),  # Invalid: non-positive
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # Valid temperature
            st.just('anthropic.claude-3-haiku'),  # Valid model_id (fixed for speed)
            st.just('us-east-1')  # Valid aws_region (fixed for speed)
        ),
        # Invalid temperature cases (below 0)
        st.tuples(
            st.just('temperature_low'),
            st.integers(min_value=1, max_value=10000),  # Valid max_tokens
            st.floats(min_value=-10.0, max_value=-0.01),  # Invalid: below 0
            st.just('anthropic.claude-3-haiku'),  # Valid model_id (fixed for speed)
            st.just('us-east-1')  # Valid aws_region (fixed for speed)
        ),
        # Invalid temperature cases (above 1)
        st.tuples(
            st.just('temperature_high'),
            st.integers(min_value=1, max_value=10000),  # Valid max_tokens
            st.floats(min_value=1.01, max_value=10.0),  # Invalid: above 1
            st.just('anthropic.claude-3-haiku'),  # Valid model_id (fixed for speed)
            st.just('us-east-1')  # Valid aws_region (fixed for speed)
        ),
        # Invalid model_id cases
        st.tuples(
            st.just('model_id'),
            st.integers(min_value=1, max_value=10000),  # Valid max_tokens
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # Valid temperature
            st.sampled_from(['', '   ', '\t\t', '\n']),  # Invalid: empty or whitespace
            st.just('us-east-1')  # Valid aws_region (fixed for speed)
        ),
        # Invalid aws_region cases
        st.tuples(
            st.just('aws_region'),
            st.integers(min_value=1, max_value=10000),  # Valid max_tokens
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # Valid temperature
            st.just('anthropic.claude-3-haiku'),  # Valid model_id (fixed for speed)
            st.sampled_from(['', '   ', '\t\t', '\n'])  # Invalid: empty or whitespace
        )
    )
)
def test_invalid_parameter_rejection(invalid_case):
    """
    Feature: content-summarizer, Property 12: Invalid parameter rejection
    Validates: Requirements 5.4
    
    Property: For any invalid model parameter values (negative max_tokens, 
    temperature outside 0-1 range, empty model_id/aws_region), validation 
    should reject them before making API calls.
    """
    invalid_param, max_tokens, temperature, model_id, aws_region = invalid_case
    
    # All cases should raise ConfigurationError
    with pytest.raises(ConfigurationError) as exc_info:
        Config(
            aws_region=aws_region,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    # Verify the error message is informative
    error_message = str(exc_info.value)
    assert len(error_message) > 0, "Error message should not be empty"
    
    # Verify the error message mentions the problematic parameter
    if invalid_param == 'max_tokens':
        assert 'max_tokens' in error_message.lower() or 'token' in error_message.lower(), \
            f"Error message should mention max_tokens, got: {error_message}"
    elif invalid_param in ['temperature_low', 'temperature_high']:
        assert 'temperature' in error_message.lower(), \
            f"Error message should mention temperature, got: {error_message}"
    elif invalid_param == 'model_id':
        assert 'model_id' in error_message.lower() or 'model' in error_message.lower(), \
            f"Error message should mention model_id, got: {error_message}"
    elif invalid_param == 'aws_region':
        assert 'region' in error_message.lower(), \
            f"Error message should mention region, got: {error_message}"
