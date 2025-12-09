"""Input validation for Content Summarizer."""


class InvalidContentError(Exception):
    """Raised when input content is invalid or cannot be processed."""
    pass


class ContentValidator:
    """Validates and preprocesses input content for summarization.
    
    Ensures content meets requirements before being sent to the summarization service.
    """
    
    def validate(self, content: str) -> bool:
        """Validate that content is non-empty and not whitespace-only.
        
        Args:
            content: The input content to validate
            
        Returns:
            True if content is valid
            
        Raises:
            InvalidContentError: If content is empty or whitespace-only
        """
        if not content:
            raise InvalidContentError("Content cannot be empty")
        
        if content.isspace():
            raise InvalidContentError("Content cannot be whitespace-only")
        
        return True
    
    def preprocess(self, content: str) -> str:
        """Preprocess content for summarization.
        
        Args:
            content: The input content to preprocess
            
        Returns:
            Preprocessed content ready for summarization
        """
        # Validate first
        self.validate(content)
        
        # Strip leading/trailing whitespace but preserve internal structure
        return content.strip()
