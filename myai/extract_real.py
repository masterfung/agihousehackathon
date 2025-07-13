#!/usr/bin/env python3
"""
Direct working extraction
"""

import subprocess
import os
from src.myai.query_analyzer import analyze_query, build_direct_url
from src.myai.preferences import get_user_context

def extract_real_restaurants(query: str):
    """Extract real restaurants using working CLI approach"""
    
    # Get user context and analyze query
    context = get_user_context()
    params = analyze_query(query, context)
    url = build_direct_url("opentable", params)
    
    print(f"🔗 URL: {url}")
    print(f"📅 Query: {query}")
    print(f"👥 Party: {params['party_size']} people")
    print(f"📅 Date: {params['date_str']} at {params['meal_time']}")
    
    # Simple working prompt
    prompt = f"""Go to {url}. Extract restaurant names you see. List them as:
1. Restaurant Name
2. Restaurant Name
etc.

Stop after listing what you see."""

    try:
        # Run with API key
        env = os.environ.copy()
        env['GOOGLE_API_KEY'] = 'AIzaSyClb6J1M2TcTbBSGcfYt1OJ3PK_TTjW9Rg'
        
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
        
        if result.returncode == 0:
            # Extract the actual result from the output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Result:' in line:
                    # Found the result line, extract the restaurant list
                    result_text = line.split('Result:', 1)[1].strip()
                    print("\n🎯 REAL RESTAURANTS FOUND:")
                    print(result_text)
                    return result_text
            
            print("\n📄 Full output:")
            print(result.stdout)
            return result.stdout
        else:
            print(f"❌ Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"💥 Failed: {e}")
        return None

if __name__ == "__main__":
    extract_real_restaurants("lunch for 3 next tuesday")