#!/usr/bin/env python3
"""
Test script to debug browser extraction
"""

import asyncio
from browser_use import Agent
from browser_use.llm import ChatGoogle
from dotenv import load_dotenv

load_dotenv()

async def test_extraction():
    """Test different extraction approaches"""
    
    llm = ChatGoogle(model='gemini-2.5-flash-lite-preview-06-17')
    
    # Test URL with party of 3
    url = "https://www.opentable.com/s?covers=3&dateTime=2025-07-12T19:00&metroId=4&term=vegetarian&prices=2,3"
    
    print(f"Testing extraction from: {url}\n")
    
    # Approach 1: Very simple task
    simple_task = f"""
Go to {url}

Once loaded, immediately extract any text that looks like restaurant information.
Don't analyze, just extract raw text from the page.
Return whatever you find.
"""
    
    print("Approach 1: Simple extraction")
    agent = Agent(
        task=simple_task,
        llm=llm,
        browser_config={"headless": False},  # Show browser
        max_actions_per_step=5,
    )
    
    try:
        result = await asyncio.wait_for(agent.run(), timeout=30.0)
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Approach 2: Use extract_structured_data explicitly
    extract_task = f"""
1. Navigate to {url}
2. Wait 2 seconds
3. Use extract_structured_data with query: "Find all restaurant names on this page"
4. Return the extracted data
"""
    
    print("\nApproach 2: Structured extraction")
    agent2 = Agent(
        task=extract_task,
        llm=llm,
        browser_config={"headless": False},
        max_actions_per_step=5,
    )
    
    try:
        result2 = await asyncio.wait_for(agent2.run(), timeout=30.0)
        print(f"Result: {result2}\n")
    except Exception as e:
        print(f"Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(test_extraction())