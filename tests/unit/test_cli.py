"""Unit tests for CLI argument parsing and display functions."""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from pathlib import Path

# Import CLI functions and exceptions
from main import create_parser, display_result, display_error, main
from src.summarizer import (
    SummaryResult,
    InvalidContentError,
    AuthenticationError,
    BedrockServiceError,
    ResponseParseError,
    RateLimitError,
    ModelNotAvailableError,
    InvalidRequestError,
    NetworkError,
    FileReadError
)
from src.config import ConfigurationError


class TestArgumentParsing:
    """Tests for CLI argument parsing."""
    
    def test_text_argument_parsing(self):
        """Test that --text flag correctly parses text input."""
        parser = create_parser()
        args = parser.parse_args(['--text', 'Sample article content'])
        
        assert args.text == 'Sample article content'
        assert args.file is None
    
    def test_file_argument_parsing(self):
        """Test that --file flag correctly parses file path."""
        parser = create_parser()
        args = parser.parse_args(['--file', 'article.txt'])
        
        assert args.file == 'article.txt'
        assert args.text is None
    
    def test_mutually_exclusive_arguments(self):
        """Test that --text and --file cannot be used together."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--text', 'content', '--file', 'file.txt'])
    
    def test_no_arguments_fails(self):
        """Test that parser requires at least one argument."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])
    
    def test_help_flag(self):
        """Test that --help flag works."""
        parser = create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(['--help'])
        
        # Help should exit with code 0
        assert exc_info.value.code == 0


class TestTextInputHandling:
    """Tests for text input handling in main function."""
    
    @patch('main.Config.from_env')
    @patch('main.BedrockSummarizer')
    @patch('main.display_result')
    def test_text_input_success(self, mock_display, mock_summarizer_class, mock_config):
        """Test successful text input handling."""
        # Setup mocks
        mock_config.return_value = MagicMock()
        mock_summarizer = MagicMock()
        mock_summarizer_class.return_value = mock_summarizer
        
        mock_result = SummaryResult(
            summary="Test summary",
            original_length=100,
            summary_length=20,
            model_used="test-model",
            timestamp=datetime.now()
        )
        mock_summarizer.summarize.return_value = mock_result
        
        # Run main with text argument
        with patch('sys.argv', ['main.py', '--text', 'Test content']):
            exit_code = main()
        
        # Verify
        assert exit_code == 0
        mock_summarizer.summarize.assert_called_once_with('Test content')
        mock_display.assert_called_once_with(mock_result)
    
    @patch('main.Config.from_env')
    @patch('main.BedrockSummarizer')
    @patch('main.display_error')
    def test_text_input_invalid_content_error(self, mock_display_error, mock_summarizer_class, mock_config):
        """Test handling of invalid content error with text input."""
        # Setup mocks
        mock_config.return_value = MagicMock()
        mock_summarizer = MagicMock()
        mock_summarizer_class.return_value = mock_summarizer
        mock_summarizer.summarize.side_effect = InvalidContentError("Content cannot be empty")
        
        # Run main with text argument
        with patch('sys.argv', ['main.py', '--text', '   ']):
            exit_code = main()
        
        # Verify
        assert exit_code == 1
        assert mock_display_error.called
        error_arg = mock_display_error.call_args[0][0]
        assert isinstance(error_arg, InvalidContentError)


class TestFileInputHandling:
    """Tests for file input handling in main function."""
    
    @patch('main.Config.from_env')
    @patch('main.BedrockSummarizer')
    @patch('main.display_result')
    def test_file_input_success(self, mock_display, mock_summarizer_class, mock_config):
        """Test successful file input handling."""
        # Setup mocks
        mock_config.return_value = MagicMock()
        mock_summarizer = MagicMock()
        mock_summarizer_class.return_value = mock_summarizer
        
        mock_result = SummaryResult(
            summary="File summary",
            original_length=500,
            summary_length=100,
            model_used="test-model",
            timestamp=datetime.now()
        )
        mock_summarizer.summarize.return_value = mock_result
        
        # Run main with file argument
        with patch('sys.argv', ['main.py', '--file', 'test.txt']):
            exit_code = main()
        
        # Verify
        assert exit_code == 0
        # Should be called with Path object
        call_arg = mock_summarizer.summarize.call_args[0][0]
        assert isinstance(call_arg, Path)
        assert str(call_arg) == 'test.txt'
        mock_display.assert_called_once_with(mock_result)
    
    @patch('main.Config.from_env')
    @patch('main.BedrockSummarizer')
    @patch('main.display_error')
    def test_file_input_file_not_found(self, mock_display_error, mock_summarizer_class, mock_config):
        """Test handling of file not found error."""
        # Setup mocks
        mock_config.return_value = MagicMock()
        mock_summarizer = MagicMock()
        mock_summarizer_class.return_value = mock_summarizer
        mock_summarizer.summarize.side_effect = FileReadError("File not found: test.txt")
        
        # Run main with file argument
        with patch('sys.argv', ['main.py', '--file', 'test.txt']):
            exit_code = main()
        
        # Verify
        assert exit_code == 1
        assert mock_display_error.called
        error_arg = mock_display_error.call_args[0][0]
        assert isinstance(error_arg, FileReadError)


class TestErrorDisplayFormatting:
    """Tests for error display formatting."""
    
    def test_display_invalid_content_error(self):
        """Test display formatting for InvalidContentError."""
        error = InvalidContentError("Content cannot be empty")
        
        # Capture stderr
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Invalid Content" in output
        assert "Content cannot be empty" in output
        assert "ERROR" in output
    
    def test_display_file_read_error(self):
        """Test display formatting for FileReadError."""
        error = FileReadError("File not found: test.txt")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "File Error" in output
        assert "File not found: test.txt" in output
    
    def test_display_authentication_error(self):
        """Test display formatting for AuthenticationError."""
        error = AuthenticationError("AWS credentials not found")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Authentication Error" in output
        assert "AWS credentials not found" in output
        assert "AWS credentials are configured correctly" in output
    
    def test_display_configuration_error(self):
        """Test display formatting for ConfigurationError."""
        error = ConfigurationError("Invalid temperature value")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Configuration Error" in output
        assert "Invalid temperature value" in output
        assert "environment variables" in output
    
    def test_display_rate_limit_error(self):
        """Test display formatting for RateLimitError."""
        error = RateLimitError("Rate limit exceeded")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Rate Limit Exceeded" in output
        assert "Rate limit exceeded" in output
    
    def test_display_model_not_available_error(self):
        """Test display formatting for ModelNotAvailableError."""
        error = ModelNotAvailableError("Model is not ready")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Model Not Available" in output
        assert "Model is not ready" in output
    
    def test_display_network_error(self):
        """Test display formatting for NetworkError."""
        error = NetworkError("Cannot connect to AWS")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Network Error" in output
        assert "Cannot connect to AWS" in output
    
    def test_display_response_parse_error(self):
        """Test display formatting for ResponseParseError."""
        error = ResponseParseError("Failed to parse response")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Response Parse Error" in output
        assert "Failed to parse response" in output
    
    def test_display_generic_bedrock_error(self):
        """Test display formatting for generic BedrockServiceError."""
        error = BedrockServiceError("Unknown service error")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Bedrock Service Error" in output
        assert "Unknown service error" in output
    
    def test_display_unexpected_error(self):
        """Test display formatting for unexpected errors."""
        error = ValueError("Unexpected value error")
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            display_error(error)
        
        output = captured_output.getvalue()
        assert "Unexpected Error" in output
        assert "ValueError" in output
        assert "Unexpected value error" in output


class TestResultDisplay:
    """Tests for result display formatting."""
    
    def test_display_result_format(self):
        """Test that display_result formats output correctly."""
        result = SummaryResult(
            summary="This is a test summary.",
            original_length=1000,
            summary_length=100,
            model_used="anthropic.claude-3-haiku-20240307-v1:0",
            timestamp=datetime(2024, 1, 15, 10, 30, 45)
        )
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            display_result(result)
        
        output = captured_output.getvalue()
        
        # Verify all expected elements are present
        assert "SUMMARY" in output
        assert "This is a test summary." in output
        assert "METADATA" in output
        assert "1,000 characters" in output  # Original length with comma
        assert "100 characters" in output  # Summary length
        assert "90.0%" in output  # Compression ratio
        assert "anthropic.claude-3-haiku-20240307-v1:0" in output
        assert "2024-01-15 10:30:45" in output
    
    def test_display_result_with_multiline_summary(self):
        """Test display with multiline summary."""
        result = SummaryResult(
            summary="Line 1\nLine 2\nLine 3",
            original_length=500,
            summary_length=50,
            model_used="test-model",
            timestamp=datetime.now()
        )
        
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            display_result(result)
        
        output = captured_output.getvalue()
        assert "Line 1" in output
        assert "Line 2" in output
        assert "Line 3" in output


class TestMainFunction:
    """Tests for main function integration."""
    
    @patch('main.Config.from_env')
    def test_configuration_error_handling(self, mock_config):
        """Test that configuration errors are handled gracefully."""
        mock_config.side_effect = ConfigurationError("Invalid config")
        
        with patch('sys.argv', ['main.py', '--text', 'test']):
            with patch('main.display_error') as mock_display_error:
                exit_code = main()
        
        assert exit_code == 1
        assert mock_display_error.called
    
    @patch('main.Config.from_env')
    @patch('main.BedrockSummarizer')
    def test_keyboard_interrupt_handling(self, mock_summarizer_class, mock_config):
        """Test that keyboard interrupt is handled gracefully."""
        mock_config.return_value = MagicMock()
        mock_summarizer = MagicMock()
        mock_summarizer_class.return_value = mock_summarizer
        mock_summarizer.summarize.side_effect = KeyboardInterrupt()
        
        captured_output = StringIO()
        with patch('sys.argv', ['main.py', '--text', 'test']):
            with patch('sys.stderr', captured_output):
                exit_code = main()
        
        assert exit_code == 130
        output = captured_output.getvalue()
        assert "cancelled by user" in output
    
    @patch('main.load_dotenv')
    @patch('main.Config.from_env')
    @patch('main.BedrockSummarizer')
    @patch('main.display_result')
    def test_dotenv_loaded(self, mock_display, mock_summarizer_class, mock_config, mock_load_dotenv):
        """Test that .env file is loaded."""
        mock_config.return_value = MagicMock()
        mock_summarizer = MagicMock()
        mock_summarizer_class.return_value = mock_summarizer
        mock_summarizer.summarize.return_value = SummaryResult(
            summary="test",
            original_length=10,
            summary_length=5,
            model_used="test",
            timestamp=datetime.now()
        )
        
        with patch('sys.argv', ['main.py', '--text', 'test']):
            main()
        
        # Verify load_dotenv was called
        mock_load_dotenv.assert_called_once()
