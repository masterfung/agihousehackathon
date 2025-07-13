#!/usr/bin/env python3
"""Test browser-use CLI directly"""

import subprocess
import os

# Simple test URL
url = "https://www.opentable.com/s?dateTime=2025-07-13T12%3A30%3A00&covers=2&term=chinese"

prompt = f"""Go to {url} and list the first 3 restaurant names you see.

Just list them like:
1. Restaurant Name
2. Restaurant Name  
3. Restaurant Name"""

env = os.environ.copy()
# Make sure API key is set
if 'GOOGLE_API_KEY' not in env:
    print("ERROR: GOOGLE_API_KEY not set!")
    exit(1)

print(f"Testing browser-use with prompt:\n{prompt}\n")
print("Running browser-use CLI...")

try:
    result = subprocess.run([
        "poetry", "run", "browser-use",
        "--model", "gemini-2.5-flash-lite-preview-06-17",
        "--prompt", prompt
    ],
    capture_output=True,
    text=True,
    timeout=60,
    env=env
    )
    
    print(f"\nReturn code: {result.returncode}")
    print(f"\nSTDOUT ({len(result.stdout)} chars):")
    print(result.stdout)
    print(f"\nSTDERR ({len(result.stderr)} chars):")
    print(result.stderr)
    
except subprocess.TimeoutExpired:
    print("\nTIMEOUT after 60 seconds!")
except Exception as e:
    print(f"\nERROR: {e}")