"""Property-based tests for input validation."""

from hypothesis import given, strategies as st, settings
import pytest
import string

from src.validator import ContentValidator, InvalidContentError


# Feature: content-summarizer, Property 1: Non-empty content validation
# For any non-empty string, the validator should accept it as valid input
@settings(max_examples=100)
@given(
    content=st.text(min_size=1)
)
def test_non_empty_content_validation(content):
    """
    Feature: content-summarizer, Property 1: Non-empty content validation
    Validates: Requirements 1.1
    
    Property: For any non-empty string, the validator should accept it as valid input.
    """
    validator = ContentValidator()
    
    # If content is not whitespace-only, it should be valid
    if not content.isspace():
        result = validator.validate(content)
        assert result is True, f"Non-empty, non-whitespace content should be valid: {repr(content)}"
    else:
        # Whitespace-only content should raise InvalidContentError
        with pytest.raises(InvalidContentError, match="whitespace-only"):
            validator.validate(content)


# Feature: content-summarizer, Property 2: Whitespace-only content rejection
# For any string composed entirely of whitespace characters, the validator should reject it as invalid input
@settings(max_examples=100)
@given(
    content=st.text(alphabet=' \t\n\r\f\v', min_size=1)
)
def test_whitespace_only_content_rejection(content):
    """
    Feature: content-summarizer, Property 2: Whitespace-only content rejection
    Validates: Requirements 1.4
    
    Property: For any string composed entirely of whitespace characters (spaces, tabs, newlines),
    the validator should reject it as invalid input.
    """
    validator = ContentValidator()
    
    # All whitespace strings should be rejected
    with pytest.raises(InvalidContentError, match="whitespace-only"):
        validator.validate(content)


# Feature: content-summarizer, Property 3: Large content preservation
# For any string with length greater than 10,000 characters, the content should be processed without truncation
@settings(max_examples=100)
@given(
    # Generate a base string and repeat it to create large content
    base_content=st.text(min_size=100, max_size=500),
    repeat_count=st.integers(min_value=21, max_value=50)
)
def test_large_content_preservation(base_content, repeat_count):
    """
    Feature: content-summarizer, Property 3: Large content preservation
    Validates: Requirements 1.2
    
    Property: For any string with length greater than 10,000 characters, the content should be 
    processed without truncation and the full content should be preserved.
    """
    validator = ContentValidator()
    
    # Create large content by repeating the base content
    content = base_content * repeat_count
    
    # Skip if we didn't actually create large content or if it's whitespace-only
    if len(content) <= 10000 or content.isspace():
        return
    
    # Validate and preprocess the content
    validator.validate(content)
    preprocessed = validator.preprocess(content)
    
    # The preprocessed content should preserve all non-whitespace characters
    # (preprocessing may strip leading/trailing whitespace)
    original_stripped = content.strip()
    
    # Verify no truncation occurred
    assert preprocessed == original_stripped, "Large content should be preserved without truncation"
    assert len(preprocessed) > 10000, "Content length should be greater than 10,000 characters"
