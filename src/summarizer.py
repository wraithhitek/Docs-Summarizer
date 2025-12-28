"""Core Gemini service for content summarization."""

from google import genai
from google.genai import types
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from .config import Config
from .validator import ContentValidator, InvalidContentError


class GeminiServiceError(Exception):
    """Raised when Gemini service encounters an error."""
    pass


class AuthenticationError(Exception):
    """Raised when API authentication fails."""
    pass


class ResponseParseError(Exception):
    """Raised when Gemini response cannot be parsed."""
    pass


class RateLimitError(GeminiServiceError):
    """Raised when API rate limits are exceeded."""
    pass


class ModelNotAvailableError(GeminiServiceError):
    """Raised when the requested model is not available."""
    pass


class InvalidRequestError(GeminiServiceError):
    """Raised when the API request is invalid."""
    pass


class NetworkError(GeminiServiceError):
    """Raised when network connectivity issues occur."""
    pass


class FileReadError(Exception):
    """Raised when a file cannot be read."""
    pass


# Keep BedrockServiceError for backward compatibility
BedrockServiceError = GeminiServiceError


@dataclass
class SummaryResult:
    """Result of a summarization operation.
    
    Attributes:
        summary: The generated summary text
        original_length: Length of the original content in characters
        summary_length: Length of the summary in characters
        model_used: The Gemini model ID that was used
        timestamp: When the summary was generated
    """
    summary: str
    original_length: int
    summary_length: int
    model_used: str
    timestamp: datetime


class GeminiSummarizer:
    """Service for summarizing content using Google Gemini.
    
    This class handles all interactions with the Google Gemini API,
    including request building, API invocation, and response parsing.
    """
    
    def __init__(self, config: Config):
        """Initialize the Gemini summarizer.
        
        Args:
            config: Configuration object with API key and model settings
            
        Raises:
            AuthenticationError: If API key is missing or invalid
            GeminiServiceError: If Gemini client initialization fails
        """
        self.config = config
        self.validator = ContentValidator()
        
        try:
            # Initialize the Gemini client with API key
            # Use v1 API version for stable model access
            self.client = genai.Client(
                api_key=config.api_key,
                http_options=types.HttpOptions(api_version='v1')
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'api' in error_msg and 'key' in error_msg:
                raise AuthenticationError(
                    f"Invalid API key: {str(e)}. "
                    "Please check your GEMINI_API_KEY environment variable."
                )
            raise GeminiServiceError(f"Failed to initialize Gemini client: {str(e)}")
    
    def summarize(self, content: Union[str, Path], style: str = "standard") -> SummaryResult:
        """Summarize the provided content using Google Gemini.
        
        This method orchestrates the full summarization flow:
        1. Loads content from file if a Path is provided
        2. Validates input content
        3. Calls the Gemini API
        4. Parses the response
        5. Returns a SummaryResult with metadata
        
        Args:
            content: The text content to summarize, or a Path to a file containing the content
            
        Returns:
            SummaryResult containing the summary and metadata
            
        Raises:
            FileReadError: If content is a Path and the file cannot be read
            InvalidContentError: If content is empty or whitespace-only
            GeminiServiceError: If the Gemini API call fails
            ResponseParseError: If the response cannot be parsed
        """
        # Load content from file if a Path is provided
        if isinstance(content, (Path, str)) and not isinstance(content, str):
            # It's a Path object
            text_content = self._read_file(content)
        elif isinstance(content, str):
            # Check if it looks like a file path (for backward compatibility)
            # We'll treat it as text content directly
            text_content = content
        else:
            text_content = str(content)
        
        # Step 1: Validate input using ContentValidator
        preprocessed_content = self.validator.preprocess(text_content)
        original_length = len(preprocessed_content)
        
        try:
            # Step 2: Build prompt based on style
            prompt = self._build_prompt(preprocessed_content, style)
            
            # Step 3: Create content for API call
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ]
            
            # Step 4: Configure generation parameters
            generate_config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
            )
            
            # Step 5: Call Gemini API
            response = self.client.models.generate_content(
                model=self.config.model_id,
                contents=contents,
                config=generate_config,
            )
            
            # Step 6: Parse response
            summary_text = self._parse_response(response)
            
            # Step 7: Create and return SummaryResult with metadata
            result = SummaryResult(
                summary=summary_text,
                original_length=original_length,
                summary_length=len(summary_text),
                model_used=self.config.model_id,
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            error_type = type(e).__name__
            
            # Handle specific Gemini API errors
            if 'quota' in error_msg or 'resource_exhausted' in error_msg or '429' in error_msg or 'rate limit' in error_msg:
                raise RateLimitError(
                    f"Rate limit or quota exceeded: {str(e)}. "
                    "Please wait a few moments and try again, or check your API quota."
                )
            elif 'api' in error_msg and 'key' in error_msg:
                raise AuthenticationError(
                    f"API key authentication failed: {str(e)}. "
                    "Please check your GEMINI_API_KEY environment variable."
                )
            elif 'model' in error_msg and ('not found' in error_msg or 'invalid' in error_msg):
                raise ModelNotAvailableError(
                    f"The model '{self.config.model_id}' is not available. "
                    "Please verify the model ID is correct."
                )
            elif 'blocked' in error_msg or 'safety' in error_msg:
                raise InvalidRequestError(
                    f"Content was blocked by safety filters: {str(e)}. "
                    "Please modify your input content."
                )
            elif 'network' in error_msg or 'connection' in error_msg:
                raise NetworkError(
                    f"Network error while communicating with Gemini: {str(e)}. "
                    "Please check your internet connection and try again."
                )
            elif isinstance(e, ResponseParseError):
                raise
            elif isinstance(e, InvalidContentError):
                raise
            else:
                raise GeminiServiceError(
                    f"Unexpected error during summarization: {error_type}: {str(e)}"
                )
    
    def _build_prompt(self, content: str, style: str) -> str:
        """Build a prompt based on the summary style.
        
        Args:
            content: The content to summarize
            style: The summary style to use
            
        Returns:
            Formatted prompt string
        """
        style_prompts = {
            "standard": f"Summarize the following text concisely:\n\n{content}",
            
            "bullet": f"Summarize the following text as bullet points, highlighting the key points:\n\n{content}",
            
            "executive": f"Create an executive summary of the following text, focusing on key insights, decisions, and actionable items suitable for business leaders:\n\n{content}",
            
            "academic": f"Provide an academic-style summary of the following text, including main arguments, methodology (if applicable), and conclusions:\n\n{content}",
            
            "brief": f"Provide a very brief, one-paragraph summary of the following text:\n\n{content}",
            
            "detailed": f"Provide a comprehensive and detailed summary of the following text, covering all major points and supporting details:\n\n{content}",
            
            "social": f"Summarize the following text in a casual, engaging style suitable for social media (keep it concise and interesting):\n\n{content}",
        }
        
        return style_prompts.get(style, style_prompts["standard"])
    
    def _read_file(self, file_path: Path) -> str:
        """Read content from a file with UTF-8 encoding.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            The file content as a string
            
        Raises:
            FileReadError: If the file cannot be read (not found, permission denied, etc.)
        """
        try:
            # Convert to Path object if it's a string
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            # Read file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except FileNotFoundError:
            raise FileReadError(
                f"File not found: {file_path}. Please check the file path and try again."
            )
        except PermissionError:
            raise FileReadError(
                f"Permission denied when reading file: {file_path}. "
                "Please check file permissions."
            )
        except UnicodeDecodeError as e:
            raise FileReadError(
                f"Failed to decode file {file_path} as UTF-8: {str(e)}. "
                "Please ensure the file is encoded in UTF-8."
            )
        except IsADirectoryError:
            raise FileReadError(
                f"Path is a directory, not a file: {file_path}. "
                "Please provide a path to a file."
            )
        except OSError as e:
            raise FileReadError(
                f"Error reading file {file_path}: {str(e)}"
            )
        except Exception as e:
            raise FileReadError(
                f"Unexpected error reading file {file_path}: {type(e).__name__}: {str(e)}"
            )
    
    def summarize_file(self, file_path: Union[str, Path]) -> SummaryResult:
        """Summarize content from a file.
        
        This is a convenience method that reads a file and summarizes its content.
        It produces the same results as calling summarize() with the file content directly.
        
        Args:
            file_path: Path to the file containing content to summarize
            
        Returns:
            SummaryResult containing the summary and metadata
            
        Raises:
            FileReadError: If the file cannot be read
            InvalidContentError: If file content is empty or whitespace-only
            GeminiServiceError: If the Gemini API call fails
            ResponseParseError: If the response cannot be parsed
        """
        # Convert to Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Read file content
        content = self._read_file(file_path)
        
        # Use the regular summarize method
        return self.summarize(content)
    
    def _parse_response(self, response) -> str:
        """Parse a Gemini API response to extract the summary text.
        
        Args:
            response: The response object from Gemini API
            
        Returns:
            The extracted summary text
            
        Raises:
            ResponseParseError: If the response structure is malformed or missing expected fields
        """
        try:
            # Try to get text directly
            if hasattr(response, 'text') and response.text:
                summary_text = response.text
                if isinstance(summary_text, str) and summary_text.strip():
                    return summary_text.strip()
            
            # Try to get from candidates
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    return part.text.strip()
            
            raise ResponseParseError(
                "Response does not contain expected text content. "
                "The response may have been blocked or is in an unexpected format."
            )
            
        except ResponseParseError:
            # Re-raise ResponseParseError as-is
            raise
        except Exception as e:
            # Wrap any unexpected errors
            raise ResponseParseError(
                f"Unexpected error parsing response: {str(e)}"
            )


# Backward compatibility alias
BedrockSummarizer = GeminiSummarizer
