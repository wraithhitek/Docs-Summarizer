# Switching to Google Gemini

This project has been updated to use Google Gemini instead of Amazon Bedrock.

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL_ID=gemini-pro
MAX_TOKENS=1024
TEMPERATURE=0.5
```

### 4. Run the Application

```bash
# Summarize text directly
python main.py --text "Your long article text here..."

# Summarize from a file
python main.py --file example_article.txt
```

## Available Models

- `gemini-pro` - Best for text-only tasks (recommended)
- `gemini-1.5-pro` - Latest model with improved capabilities
- `gemini-1.5-flash` - Faster, more cost-effective option

## Key Changes from Bedrock

1. **No AWS credentials needed** - Just a Gemini API key
2. **Simpler setup** - No region configuration required
3. **Free tier available** - Generous free quota for testing
4. **Different pricing** - Pay per request, not per token

## Pricing

Google Gemini offers:
- **Free tier**: 60 requests per minute
- **Paid tier**: Higher rate limits and priority access

Check current pricing at: https://ai.google.dev/pricing

## Troubleshooting

### "Invalid API key" error
- Verify your API key is correct in `.env`
- Make sure there are no extra spaces or quotes
- Regenerate your API key if needed

### "Rate limit exceeded" error
- You've hit the free tier limit (60 requests/minute)
- Wait a minute and try again
- Consider upgrading to paid tier for higher limits

### "Model not found" error
- Check that your model ID is correct
- Try using `gemini-pro` (the default)
- Some models may not be available in all regions

## Migration Notes

The code maintains backward compatibility:
- `BedrockSummarizer` is aliased to `GeminiSummarizer`
- `BedrockServiceError` is aliased to `GeminiServiceError`
- All existing tests should work with minimal changes

## Need Help?

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Python SDK Reference](https://ai.google.dev/api/python)
- [Community Forum](https://discuss.ai.google.dev/)
