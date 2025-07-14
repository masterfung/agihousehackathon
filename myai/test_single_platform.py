#!/usr/bin/env python3
"""
Test script to debug single platform searches
"""

import asyncio
import sys
from src.myai.preferences import get_user_context
from src.myai.restaurant_finder import RestaurantFinder
from browser_use.llm import ChatGoogle
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_platform(platform: str):
    """Test a single platform"""
    print(f"\n{'='*60}")
    print(f"Testing {platform.upper()} search")
    print(f"{'='*60}\n")
    
    # Initialize
    context = get_user_context()
    llm = ChatGoogle(model='gemini-2.5-flash-lite-preview-06-17')
    finder = RestaurantFinder(context, llm)
    
    # Search just this platform
    results = await finder.find_restaurants(
        query="dinner tonight",
        platforms=[platform],
        num_results=5
    )
    
    if results:
        print(f"\n✅ SUCCESS! Found {len(results)} restaurants:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['restaurant'].name}")
            print(f"   Platform: {r['platform']}")
            print(f"   Score: {r['score'].total_score}")
            print(f"   Cuisine: {', '.join(r['restaurant'].cuisine_type)}")
            print(f"   Price: {r['restaurant'].price_range}")
    else:
        print("\n❌ No results found")
    
    print(f"\n{'='*60}")

async def main():
    """Run tests"""
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        await test_platform(platform)
    else:
        # Test each platform individually
        for platform in ["yelp", "google", "opentable", "resy"]:
            await test_platform(platform)
            print("\nPress Enter to continue to next platform...")
            input()

if __name__ == "__main__":
    asyncio.run(main())