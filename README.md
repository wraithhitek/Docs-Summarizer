# Content Summarizer

A Python application that leverages Google Gemini's AI capabilities to generate concise summaries of long-form content such as articles and blog posts.

## Features

- Summarize articles and blog posts using Google Gemini models
- Support for both direct text input and file input
- Configurable summarization parameters (model, max tokens, temperature)
- Comprehensive error handling with user-friendly messages
- Input validation to ensure quality content processing
- Detailed metadata in results (original length, summary length, model used)

## Prerequisites

- Python 3.8 or higher
- Google account with Gemini API access
- Gemini API key (free tier available)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd content-summarizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get your Gemini API key:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in and create an API key

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` file with your API key:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_ID=gemini-pro
MAX_TOKENS=1024
TEMPERATURE=0.5
```

## Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | - | Yes |
| `GEMINI_MODEL_ID` | Gemini model to use | gemini-pro | No |
| `MAX_TOKENS` | Maximum tokens in summary | 1024 | No |
| `TEMPERATURE` | Model temperature (0-1) | 0.5 | No |

## Usage

### Web UI (Recommended)

Start the web interface:

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

Features:
- 🎨 Beautiful, modern interface
- 📝 Text input or file upload
- 📋 One-click copy to clipboard
- 📱 Mobile-friendly responsive design
- 📊 Detailed statistics and metadata

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for more details.

### Command Line Interface (CLI)

#### Summarize text directly:

```bash
python main.py --text "Your long article text here..."
```

#### Summarize from a file:

```bash
python main.py --file example_article.txt
```

### Example with the included sample article:

```bash
python main.py --file example_article.txt
```

Expected output:
```
Summary:
--------
Artificial intelligence is revolutionizing healthcare through medical imaging analysis, 
natural language processing of clinical records, and accelerated drug discovery. While 
these advances offer significant benefits, they also raise important ethical concerns 
around data privacy, algorithmic bias, and human judgment that require careful 
consideration by healthcare providers, technologists, and policymakers.

Metadata:
---------
Original Length: 1,234 characters
Summary Length: 287 characters
Model Used: gemini-pro
Timestamp: 2025-12-06 10:30:45
```

## Error Messages and Troubleshooting

### Common Errors

**"Content cannot be empty or contain only whitespace"**
- Cause: Input text is empty or contains only spaces/tabs/newlines
- Solution: Provide valid text content with actual characters

**"Invalid API key" or "API key authentication failed"**
- Cause: Missing or invalid Gemini API key in environment variables
- Solution: Ensure `GEMINI_API_KEY` is set correctly in `.env` file

**"Rate limit exceeded"**
- Cause: Too many requests to Amazon Bedrock API
- Solution: Wait a few moments and retry. Consider implementing delays between requests

**"Model not available"**
- Cause: The specified Gemini model is not available
- Solution: Try using `gemini-pro` (the default model), or check available models in the API documentation

**"Invalid model parameters"**
- Cause: Configuration values are outside valid ranges
- Solution: Ensure `MAX_TOKENS` is positive and `TEMPERATURE` is between 0 and 1

**"Connection error"**
- Cause: Network connectivity issues with Google services
- Solution: Check your internet connection and Google AI service status

**"File not found"**
- Cause: The specified file path doesn't exist
- Solution: Verify the file path is correct and the file exists

### Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the generated key
5. Add it to your `.env` file

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only property-based tests
pytest tests/property/

# Run with coverage report
pytest --cov=src --cov-report=html
```

## Project Structure

```
content-summarizer/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── validator.py       # Input validation
│   └── summarizer.py      # Core Bedrock integration
├── tests/
│   ├── unit/              # Unit tests
│   ├── property/          # Property-based tests
│   └── integration/       # Integration tests
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── example_article.txt   # Sample article for testing
└── README.md             # This file
```

## Available Models

The application supports various Google Gemini models:

- `gemini-pro` - Best for text-only tasks (recommended)
- `gemini-1.5-pro` - Latest model with improved capabilities
- `gemini-1.5-flash` - Faster, more cost-effective option

Update `GEMINI_MODEL_ID` in your `.env` file to switch models.

## Configuration Tips

### For shorter summaries:
```
MAX_TOKENS=512
TEMPERATURE=0.3
```

### For more creative summaries:
```
MAX_TOKENS=2048
TEMPERATURE=0.8
```

### For technical/factual content:
```
MAX_TOKENS=1024
TEMPERATURE=0.2
```

## Limitations

- Maximum input content length: Varies by model (typically 30,000+ characters)
- API response time: 1-3 seconds per request
- Rate limits: 60 requests/minute on free tier
- Requires active internet connection
- Free tier available with generous quotas

## Pricing

Google Gemini offers:
- **Free tier**: 60 requests per minute
- **Paid tier**: Higher rate limits and priority access

Check current pricing at: https://ai.google.dev/pricing
