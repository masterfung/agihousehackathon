#!/usr/bin/env python3
"""
Restaurant finder using browser-use MCP server commands directly
This shows how to use the MCP server instead of the browser-use Python agent
"""

import subprocess
import json
from datetime import datetime
from src.myai.preferences import get_user_context
from src.myai.date_parser import parse_date_query, parse_party_size, get_meal_time

def run_mcp_command(command: str) -> str:
    """Run a browser-use MCP command and return the result"""
    # This assumes you have browser-use MCP server running
    # You might need to adjust this based on your MCP setup
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def find_restaurants_with_mcp(query: str = "dinner for 5 at 8pm"):
    """Find restaurants using browser-use MCP commands"""
    
    # Parse the query
    context = get_user_context()
    date_obj, date_str = parse_date_query(query)
    party_size = parse_party_size(query)
    meal_time = get_meal_time(query)
    
    # Convert time to 24-hour format
    try:
        time_obj = datetime.strptime(meal_time, "%I:%M %p")
        hour = time_obj.hour
    except:
        hour = 19  # Default to 7pm
    
    # Build OpenTable URL
    url = f"https://www.opentable.com/s?covers={party_size}&dateTime={date_obj.strftime(f'%Y-%m-%dT{hour:02d}:00')}&metroId=4&term=vegetarian&prices=2,3"
    
    print(f"🔍 Searching for vegetarian restaurants...")
    print(f"📅 Date: {date_str}")
    print(f"👥 Party size: {party_size}")
    print(f"🕐 Time: {meal_time}")
    print(f"🔗 URL: {url}")
    print()
    
    # Step 1: Navigate
    print("1️⃣ Navigating to OpenTable...")
    run_mcp_command(f'browser_navigate "{url}"')
    
    # Step 2: Wait a bit
    import time
    time.sleep(3)
    
    # Step 3: Extract content
    print("2️⃣ Extracting restaurant data...")
    extraction_query = """
    Find all restaurant cards on this page and extract:
    - Restaurant name
    - Cuisine type
    - Price level ($ symbols)
    - Neighborhood/location
    
    Format each restaurant as:
    [Name] | [Cuisine] | [Price] | [Neighborhood]
    
    Return only the formatted list, nothing else.
    """
    
    result = run_mcp_command(f'browser_extract_content "{extraction_query}"')
    
    print("3️⃣ Results:")
    print(result)
    
    # Optional: Get screenshot
    # run_mcp_command('browser_screenshot "restaurant_search.png"')
    
    return result

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "dinner for 5 tomorrow at 8pm"
    find_restaurants_with_mcp(query)