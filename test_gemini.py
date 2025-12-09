#!/usr/bin/env python3
"""Simple test script to verify Gemini API is working."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {api_key[:10]}..." if api_key else "No API key found")

# Configure Gemini
genai.configure(api_key=api_key)

# Create model - try different model names
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Using model: gemini-1.5-flash")
except:
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("Using model: gemini-1.5-pro")
    except:
        model = genai.GenerativeModel('gemini-pro')
        print("Using model: gemini-pro")

# Test with simple prompt
try:
    print("\nTesting Gemini API...")
    response = model.generate_content("Say hello in one sentence.")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
