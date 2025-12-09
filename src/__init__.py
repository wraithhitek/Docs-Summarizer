"""Content Summarizer - A Python application for summarizing content using Amazon Bedrock."""

__version__ = "0.1.0"

from .config import Config, ConfigurationError
from .validator import ContentValidator, InvalidContentError
from .summarizer import (
    BedrockSummarizer,
    SummaryResult,
    BedrockServiceError,
    AuthenticationError,
    ResponseParseError,
    RateLimitError,
    ModelNotAvailableError,
    InvalidRequestError,
    NetworkError
)

__all__ = [
    'Config',
    'ConfigurationError',
    'ContentValidator',
    'InvalidContentError',
    'BedrockSummarizer',
    'SummaryResult',
    'BedrockServiceError',
    'AuthenticationError',
    'ResponseParseError',
    'RateLimitError',
    'ModelNotAvailableError',
    'InvalidRequestError',
    'NetworkError',
]
