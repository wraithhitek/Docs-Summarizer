#!/usr/bin/env python3
"""Command-line interface for Content Summarizer.

This CLI provides a simple interface to summarize content using Google Gemini.
Content can be provided directly via --text flag or from a file via --file flag.
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.config import Config, ConfigurationError
from src.summarizer import (
    GeminiSummarizer,
    InvalidContentError,
    AuthenticationError,
    GeminiServiceError,
    ResponseParseError,
    RateLimitError,
    ModelNotAvailableError,
    InvalidRequestError,
    NetworkError,
    FileReadError
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='Summarize articles and blog posts using Google Gemini AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize text directly
  python main.py --text "Your long article text here..."
  
  # Summarize content from a file
  python main.py --file article.txt
  
  # View help
  python main.py --help

Environment Variables:
  GEMINI_API_KEY          Google Gemini API key (required)
  GEMINI_MODEL_ID         Model to use (default: gemini-pro)
  MAX_TOKENS              Maximum tokens for summary (default: 1024)
  TEMPERATURE             Model temperature 0-1 (default: 0.5)
        """
    )
    
    # Create mutually exclusive group for text vs file input
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--text',
        type=str,
        help='Text content to summarize (provide content directly)'
    )
    input_group.add_argument(
        '--file',
        type=str,
        help='Path to file containing content to summarize'
    )
    
    return parser


def display_result(result) -> None:
    """Display the summarization result with metadata.
    
    Args:
        result: SummaryResult object containing summary and metadata
    """
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(result.summary)
    print()
    print("=" * 80)
    print("METADATA")
    print("=" * 80)
    print(f"Original Length:  {result.original_length:,} characters")
    print(f"Summary Length:   {result.summary_length:,} characters")
    print(f"Compression:      {(1 - result.summary_length / result.original_length) * 100:.1f}%")
    print(f"Model Used:       {result.model_used}")
    print(f"Generated:        {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


def display_error(error: Exception) -> None:
    """Display error message in a user-friendly format.
    
    Args:
        error: The exception that occurred
    """
    print("\n" + "=" * 80, file=sys.stderr)
    print("ERROR", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)
    
    # Determine error type and display appropriate message
    if isinstance(error, InvalidContentError):
        print("❌ Invalid Content:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, FileReadError):
        print("❌ File Error:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, AuthenticationError):
        print("❌ Authentication Error:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
        print(file=sys.stderr)
        print("   Please ensure your AWS credentials are configured correctly.", file=sys.stderr)
    elif isinstance(error, ConfigurationError):
        print("❌ Configuration Error:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
        print(file=sys.stderr)
        print("   Please check your environment variables or .env file.", file=sys.stderr)
    elif isinstance(error, RateLimitError):
        print("❌ Rate Limit Exceeded:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, ModelNotAvailableError):
        print("❌ Model Not Available:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, InvalidRequestError):
        print("❌ Invalid Request:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, NetworkError):
        print("❌ Network Error:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, ResponseParseError):
        print("❌ Response Parse Error:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    elif isinstance(error, GeminiServiceError):
        print("❌ Gemini Service Error:", file=sys.stderr)
        print(f"   {str(error)}", file=sys.stderr)
    else:
        print("❌ Unexpected Error:", file=sys.stderr)
        print(f"   {type(error).__name__}: {str(error)}", file=sys.stderr)
    
    print(file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration from environment
        config = Config.from_env()
        
        # Initialize the summarizer
        summarizer = GeminiSummarizer(config)
        
        # Get content based on input method
        if args.text:
            # Direct text input
            content = args.text
        else:
            # File input - let summarizer handle file reading
            content = Path(args.file)
        
        # Perform summarization
        result = summarizer.summarize(content)
        
        # Display results
        display_result(result)
        
        return 0
        
    except (
        InvalidContentError,
        FileReadError,
        AuthenticationError,
        ConfigurationError,
        RateLimitError,
        ModelNotAvailableError,
        InvalidRequestError,
        NetworkError,
        ResponseParseError,
        GeminiServiceError
    ) as e:
        # Handle known errors gracefully
        display_error(e)
        return 1
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        return 130
        
    except Exception as e:
        # Handle unexpected errors
        display_error(e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
