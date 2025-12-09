#!/usr/bin/env python3
"""Test the new Gemini API."""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:10]}...")

# Initialize client
client = genai.Client(api_key=api_key)

# Test with simple prompt
try:
    print("\nTesting Gemini API with new structure...")
    
    model = "gemini-2.0-flash-exp"
    print(f"Using model: {model}")
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="Say hello in one sentence.")],
        )
    ]
    
    config = types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=100,
    )
    
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    
    print(f"\nSuccess!")
    print(f"Response text: {response.text}")
    
except Exception as e:
    print(f"\nError: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()
