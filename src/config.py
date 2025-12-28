"""Configuration management for Content Summarizer."""

import os
from dataclasses import dataclass
from typing import Optional


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


@dataclass
class Config:
    """Configuration for the Content Summarizer application.
    
    Attributes:
        api_key: Google Gemini API key
        model_id: Gemini model identifier
        max_tokens: Maximum tokens for summary generation
        temperature: Temperature parameter for model (0-1)
    """
    api_key: str
    model_id: str
    max_tokens: int
    temperature: float
    
    def __post_init__(self):
        """Validate configuration parameters after initialization.
        
        Raises:
            ConfigurationError: If any parameter is invalid
        """
        # Validate max_tokens (must be positive integer)
        if not isinstance(self.max_tokens, int):
            raise ConfigurationError(
                f"max_tokens must be an integer, got {type(self.max_tokens).__name__}"
            )
        if self.max_tokens <= 0:
            raise ConfigurationError(
                f"max_tokens must be positive, got: {self.max_tokens}"
            )
        
        # Validate temperature (must be between 0 and 1)
        if not isinstance(self.temperature, (int, float)):
            raise ConfigurationError(
                f"temperature must be a number, got {type(self.temperature).__name__}"
            )
        if not (0 <= self.temperature <= 1):
            raise ConfigurationError(
                f"temperature must be between 0 and 1, got: {self.temperature}"
            )
        
        # Validate model_id (must be non-empty string)
        if not isinstance(self.model_id, str):
            raise ConfigurationError(
                f"model_id must be a string, got {type(self.model_id).__name__}"
            )
        if not self.model_id or not self.model_id.strip():
            raise ConfigurationError("model_id cannot be empty")
        
        # Validate api_key (must be non-empty string)
        if not isinstance(self.api_key, str):
            raise ConfigurationError(
                f"api_key must be a string, got {type(self.api_key).__name__}"
            )
        if not self.api_key or not self.api_key.strip():
            raise ConfigurationError("api_key cannot be empty")
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables.
        
        Returns:
            Config instance with values from environment or defaults
            
        Environment Variables:
            GEMINI_API_KEY: Google Gemini API key (required)
            GEMINI_MODEL_ID: Model ID (default: gemini-pro)
            MAX_TOKENS: Maximum tokens (default: 1024)
            TEMPERATURE: Temperature parameter (default: 0.5)
            
        Raises:
            ConfigurationError: If environment variables contain invalid values
        """
        api_key = os.getenv('GEMINI_API_KEY', '')
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY environment variable is required. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        model_id = os.getenv('GEMINI_MODEL_ID', 'gemini-2.5-flash')
        
        # Load max_tokens with default
        max_tokens_str = os.getenv('MAX_TOKENS', '1024')
        try:
            max_tokens = int(max_tokens_str)
        except ValueError:
            raise ConfigurationError(f"MAX_TOKENS must be an integer, got: {max_tokens_str}")
        
        # Load temperature with default
        temperature_str = os.getenv('TEMPERATURE', '0.5')
        try:
            temperature = float(temperature_str)
        except ValueError:
            raise ConfigurationError(f"TEMPERATURE must be a float, got: {temperature_str}")
        
        # Create Config instance - validation happens in __post_init__
        return cls(
            api_key=api_key,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature
        )
