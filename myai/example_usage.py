#!/usr/bin/env python3
"""
Example usage of the MyAI restaurant finder system
Demonstrates how personal preferences drive restaurant selection
"""

import asyncio
from src.myai.preferences import get_user_context, format_preferences_for_prompt
from src.myai.evaluator import RestaurantInfo, RestaurantEvaluator
from browser_use.llm import ChatGoogle
from src.myai.restaurant_finder import RestaurantFinder
from src.myai.search_optimizer import ContextPriority
from src.myai.date_parser import parse_date_query
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def demonstrate_preferences():
    """Show how preferences are structured"""
    print("=== Personal Context Demo ===\n")
    
    context = get_user_context()
    
    print("Your personal preferences (hardcoded for now, MCP integration coming):")
    print(f"\n{format_preferences_for_prompt(context)}\n")
    
    print("\n=== Prioritized Context (Markdown) ===")
    print(ContextPriority.get_context_markdown(context))
    
    print("\nThis data structure will be provided by your MCP server, allowing:")
    print("  • Any AI service to access your preferences")
    print("  • Dynamic updates to your profile")
    print("  • Consistent experience across platforms\n")


def demonstrate_scoring():
    """Show how the scoring system works"""
    print("=== Restaurant Scoring Demo ===\n")
    
    context = get_user_context()
    evaluator = RestaurantEvaluator(context)
    
    # Example restaurants
    restaurants = [
        RestaurantInfo(
            name="Shizen Vegan Sushi Bar",
            cuisine_type=["Japanese", "Sushi", "Vegan"],
            price_range="$$",
            address="370 14th St, San Francisco, CA 94103",
            distance_miles=1.2,
            has_vegetarian_menu=True,
            vegetarian_options_count=20,
            wine_list_quality="good",
            allows_corkage=True,
            near_public_transit=True,
            rating=4.5
        ),
        RestaurantInfo(
            name="Bob's Steak House",
            cuisine_type=["Steakhouse", "American"],
            price_range="$$$$",
            address="1234 Market St, San Francisco, CA",
            distance_miles=0.8,
            has_vegetarian_menu=False,
            vegetarian_options_count=1,  # Just a salad
            wine_list_quality="excellent",
            allows_corkage=True,
            near_public_transit=True,
            rating=4.7
        ),
        RestaurantInfo(
            name="Casa Mexicana",
            cuisine_type=["Mexican"],
            price_range="$$",
            address="789 Mission St, San Francisco, CA",
            distance_miles=1.5,
            has_vegetarian_menu=True,
            vegetarian_options_count=8,
            wine_list_quality="basic",
            allows_corkage=False,
            near_public_transit=True,
            rating=4.3
        )
    ]
    
    print("Evaluating 3 example restaurants:\n")
    
    for restaurant in restaurants:
        score = evaluator.evaluate_restaurant(restaurant)
        print(f"{restaurant.name}")
        print(f"  Score: {score.total_score}/100")
        print(f"  {score.explanation}")
        print()


async def demonstrate_browser_search():
    """Show how browser automation works (requires API key)"""
    print("=== Browser Automation Demo ===\n")
    
    try:
        llm = ChatGoogle(model='gemini-2.0-pro')
        context = get_user_context()
        finder = RestaurantFinder(context, llm)
        
        print("This would normally:")
        print("1. Open a browser (headless mode)")
        print("2. Navigate to OpenTable/Yelp/Google")
        print("3. Search with your preferences")
        print("4. Extract restaurant information")
        print("5. Score each result")
        print("6. Return ranked recommendations\n")
        
        print("Example command:")
        print('  python -m myai find "dinner tonight" opentable')
        print('  python -m myai find "lunch tomorrow" yelp')
        print('  python -m myai evaluate "Restaurant Name" "Cuisine" "$$ " "Address"')
        
    except Exception as e:
        print(f"Note: Browser automation requires GOOGLE_API_KEY in .env file")
        print(f"Error: {e}")


def demonstrate_date_parsing():
    """Show how date parsing works"""
    print("=== Date Parsing Demo ===\n")
    
    test_queries = [
        "dinner tonight",
        "lunch tomorrow", 
        "dinner next friday",
        "brunch this weekend",
        "dinner day after tomorrow"
    ]
    
    for query in test_queries:
        date_obj, date_str = parse_date_query(query)
        print(f'"{query}" → {date_str} ({date_obj.strftime("%Y-%m-%d")})')
    
    print()


def demonstrate_mcp_integration():
    """Show how MCP integration will work"""
    print("\n=== Future MCP Integration ===\n")
    
    print("Current: Hardcoded preferences in preferences.py")
    print("Future: Dynamic preferences from MCP server\n")
    
    print("MCP Server will provide:")
    print("  • GET /preferences - Retrieve current user preferences")
    print("  • POST /preferences - Update preferences based on interactions")
    print("  • GET /history - Access past restaurant visits and ratings")
    print("  • POST /feedback - Learn from user feedback\n")
    
    print("Benefits:")
    print("  • Works with any AI that supports MCP (Claude, GPT, Gemini)")
    print("  • Preferences evolve based on your choices")
    print("  • Consistent experience across all platforms")
    print("  • Privacy-focused (your data stays with you)")


def main():
    """Run all demonstrations"""
    print("\n🍽️  MyAI Restaurant Finder - Demonstration\n")
    print("This system uses your personal preferences to find perfect restaurants")
    print("=" * 60 + "\n")
    
    demonstrate_preferences()
    print("\n" + "=" * 60 + "\n")
    
    demonstrate_scoring()
    print("\n" + "=" * 60 + "\n")
    
    demonstrate_date_parsing()
    print("\n" + "=" * 60 + "\n")
    
    asyncio.run(demonstrate_browser_search())
    print("\n" + "=" * 60 + "\n")
    
    demonstrate_mcp_integration()
    
    print("\n" + "=" * 60)
    print("\n✅ Ready to use! Try these commands:")
    print("  poetry run python src/myai/main.py find")
    print("  poetry run python src/myai/main.py find 'dinner tomorrow'")
    print("  poetry run python src/myai/main.py find 'lunch next friday' opentable")
    print("  poetry run python src/myai/main.py evaluate 'Greens Restaurant' 'Vegetarian' '$$' '2 Marina Blvd, SF'")


if __name__ == "__main__":
    main()