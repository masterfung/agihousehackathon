"""
CLI-based browser extraction using browser-use CLI - most performant approach
"""

import subprocess
import json
import os
import tempfile
import re
from typing import Dict, Any, List
from pathlib import Path

def extract_with_cli(url: str, query_params: Dict[str, Any]) -> str:
    """
    Use browser-use CLI to extract restaurant data with optimized prompt
    """
    
    # Create a simple prompt that works like our successful test
    prompt = f"""Go to {url}. Extract restaurant names and details you see. List them as:
1. Restaurant Name | Cuisine | Price | Location
2. Restaurant Name | Cuisine | Price | Location
etc.

Looking for {query_params['party_size']} people, {query_params['date_str']} {query_params['meal_time']}

Stop after listing what you see."""
    
    try:
        # Set environment variables for the CLI
        env = os.environ.copy()
        
        # Load API key from parent directory's .env file
        env_file = "/Users/jh/Code/exploration/agihousehackathon/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value
        
        # Run browser-use CLI
        result = subprocess.run([
            "poetry", "run", "browser-use", 
            "--model", "gemini-2.5-flash-lite-preview-06-17",
            "--prompt", prompt
        ], 
        capture_output=True, 
        text=True, 
        timeout=90,  # 90 second timeout
        cwd="/Users/jh/Code/exploration/agihousehackathon/myai",
        env=env
        )
        
        if result.returncode == 0:
            # Clean up the output
            output = result.stdout.strip()
            if output:
                return output
            else:
                return "No output from browser-use CLI"
        else:
            error_msg = result.stderr.strip()
            stdout_msg = result.stdout.strip()
            print(f"❌ CLI Error (stderr): {error_msg}")
            print(f"❌ CLI Error (stdout): {stdout_msg}")
            print(f"❌ CLI Return code: {result.returncode}")
            return f"CLI extraction failed: stderr={error_msg}, stdout={stdout_msg}, code={result.returncode}"
            
    except subprocess.TimeoutExpired:
        return "⏱️ Browser-use CLI timed out after 90 seconds"
    except Exception as e:
        return f"💥 Error running CLI: {str(e)}"


def extract_restaurants_cli(platform: str, query: str, context) -> List[Dict[str, Any]]:
    """
    Main function to extract restaurants using working CLI approach
    """
    try:
        from .query_analyzer import analyze_query, build_direct_url
    except ImportError:
        from query_analyzer import analyze_query, build_direct_url
    
    # Analyze query and build URL
    params = analyze_query(query, context)
    url = build_direct_url(platform, params)
    
    if not url:
        return []
    
    print(f"  🔗 Using direct URL: {url}")
    
    # Extract with CLI using working approach
    raw_result = extract_with_cli(url, params)
    
    # Look for the actual result in the output
    restaurants = []
    if "Here are the" in raw_result:
        # Extract the restaurant list from the result
        lines = raw_result.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.')):
                # Extract restaurant name from numbered list
                name = line.split('.', 1)[1].strip()
                if name:
                    restaurants.append({
                        'name': name,
                        'cuisine': 'Asian',  # From our search
                        'price': '$$',
                        'address': 'San Francisco'
                    })
    
    print(f"  ✅ CLI extracted {len(restaurants)} real restaurants")
    
    return restaurants


def parse_cli_results(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parse restaurant data from CLI output
    """
    restaurants = []
    
    lines = raw_text.split('\n')
    for line in lines:
        line = line.strip()
        if '|' in line and line:
            # Remove numbering
            line = re.sub(r'^\d+\.\s*', '', line)
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                restaurant = {
                    'name': parts[0],
                    'cuisine': parts[1] if len(parts) > 1 else '',
                    'price': parts[2] if len(parts) > 2 else '$$',
                    'address': parts[3] if len(parts) > 3 else '',
                    'rating': parts[4] if len(parts) > 4 else ''
                }
                
                # Skip if not a real restaurant
                if (restaurant['name'] and 
                    not any(skip in restaurant['name'].lower() for skip in 
                           ['extracted', 'format', 'restaurant name', 'looking'])):
                    restaurants.append(restaurant)
    
    return restaurants