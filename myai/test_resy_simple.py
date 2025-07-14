#!/usr/bin/env python3
"""
Simple test of Resy extraction with the proper URL
"""

import subprocess
import os

def test_resy_direct():
    """Test Resy extraction directly"""
    
    # Use the optimized URL format with facet
    url = "https://resy.com/cities/san-francisco-ca/search?date=2025-07-16&seats=3&time=1830&facet=cuisine:Asian"
    
    prompt = f"""Go to {url}

SIMPLE TASK: Extract restaurant names and times from Resy page.

1. Look at the page
2. Find restaurant listings 
3. For each restaurant, extract name and any visible time slots
4. Return as: Restaurant Name | Available Times

Stop after extracting 5 restaurants or 30 seconds.
"""

    try:
        env = os.environ.copy()
        env['GOOGLE_API_KEY'] = 'AIzaSyDSOZd5v5_pjnekZ0tdpxX0pTg3JsJ1Xg8'
        
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
        
        print("=== RESY EXTRACTION RESULT ===")
        print(result.stdout)
        
        if result.stderr:
            print("\n=== ERRORS ===")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_resy_direct()