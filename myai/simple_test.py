#!/usr/bin/env python3
"""
Simple test to get real restaurant results
"""

import os
import subprocess
import tempfile

def test_real_extraction():
    """Test browser-use with a very simple task"""
    
    url = "https://www.opentable.com/s?covers=4&dateTime=2025-07-16T19:00&metroId=4&term=vegetarian%20asian&prices=2,3"
    
    # Very simple prompt
    prompt = f"""Go to {url}. Extract restaurant names you see. Just list them as:
1. Restaurant Name
2. Restaurant Name
etc.

Stop after listing what you see."""

    try:
        # Set the API key
        env = os.environ.copy()
        env['GOOGLE_API_KEY'] = 'AIzaSyClb6J1M2TcTbBSGcfYt1OJ3PK_TTjW9Rg'
        
        result = subprocess.run([
            "poetry", "run", "browser-use", 
            "--model", "gemini-2.5-flash-lite-preview-06-17",
            "--prompt", prompt
        ], 
        capture_output=True, 
        text=True, 
        timeout=45,
        env=env
        )
        
        print("=== REAL EXTRACTION RESULT ===")
        print(result.stdout)
        
        if result.stderr:
            print("\n=== ERRORS ===")
            print(result.stderr)
            
        return result.stdout
        
    except subprocess.TimeoutExpired:
        print("Extraction timed out")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_real_extraction()