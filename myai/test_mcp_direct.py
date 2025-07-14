#!/usr/bin/env python3
"""
Test direct MCP server call for restaurant extraction
"""

import subprocess
import json
import os

def test_mcp_extraction():
    """Test MCP server directly"""
    
    # Test OpenTable URL with parameters
    url = "https://www.opentable.com/s?covers=4&dateTime=2025-07-16T19:00&metroId=4&term=vegetarian%20asian&prices=2,3"
    
    prompt = f"""
Navigate to {url} and extract restaurant data.

Look for restaurant cards/listings and extract:
- Restaurant name
- Cuisine type
- Price range ($ symbols)
- Neighborhood/location

If you see only 4 results, extract all 4 and stop.
Do NOT scroll if you've reached the end of results.

Return in format:
1. [Name] | [Cuisine] | [Price] | [Location]
2. [Name] | [Cuisine] | [Price] | [Location]
...
"""
    
    try:
        # Call browser-use as MCP server
        result = subprocess.run([
            "poetry", "run", "browser-use", 
            "--mcp",
            "--model", "gemini-2.5-flash-lite-preview-06-17"
        ], 
        input=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "browser_use",
            "params": {
                "task": prompt
            }
        }),
        capture_output=True, 
        text=True, 
        timeout=60,
        env={**os.environ, "GOOGLE_API_KEY": "AIzaSyClb6J1M2TcTbBSGcfYt1OJ3PK_TTjW9Rg"}
        )
        
        print("MCP Response:")
        print(result.stdout)
        if result.stderr:
            print("MCP Errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"MCP test failed: {e}")

if __name__ == "__main__":
    test_mcp_extraction()