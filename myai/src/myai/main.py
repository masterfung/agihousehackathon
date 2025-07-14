import asyncio
import sys
from typing import List
from browser_use.llm import ChatGoogle
from browser_use import Agent
from dotenv import load_dotenv
try:
    from .preferences import get_user_context, format_preferences_for_prompt
    from .restaurant_finder import RestaurantFinder
    from .evaluator import RestaurantEvaluator
except ImportError:
    # Handle when running as script
    from preferences import get_user_context, format_preferences_for_prompt
    from restaurant_finder import RestaurantFinder
    from evaluator import RestaurantEvaluator

# Read GOOGLE_API_KEY into env
load_dotenv()

# Initialize the model
# llm = ChatGoogle(model='gemini-2.5-pro')
llm = ChatGoogle(model='gemini-2.5-flash-lite-preview-06-17')


async def find_dinner_spot(query: str = "dinner tonight", platforms: List[str] = None):
    """
    Main function to find a dinner spot based on user preferences
    
    Args:
        query: What type of meal/time (e.g., "dinner tonight", "lunch tomorrow")
        platforms: List of platforms to search (defaults to all: opentable, resy, yelp, google)
    """
    if platforms is None:
        platforms = ["opentable", "resy", "yelp", "google"]
    
    print(f"\n🚀 Searching for restaurants for '{query}' across {len(platforms)} platforms...\n")
    
    # Load user context (hardcoded for now, will come from MCP later)
    user_context = get_user_context()
    
    # Show user preferences being used
    print("Using your preferences:")
    print(f"  • Dietary: Vegetarian (no peanuts)")
    print(f"  • Cuisines: {', '.join(user_context.cuisine.preferred_cuisines)}")
    print(f"  • Budget: ${user_context.budget.min_price_per_dish}-${user_context.budget.max_price_per_dish}/dish")
    print(f"  • Location: {user_context.location.zip_code} (prefer public transit)")
    print(f"  • Wine: Important with corkage preference")
    print(f"  • Spice tolerance: Mild\n")
    
    # Create restaurant finder
    finder = RestaurantFinder(user_context, llm)
    
    try:
        # Find restaurants
        results = await finder.find_restaurants(
            query=query,
            platforms=platforms,
            num_results=5
        )
        
        # Display results
        if results:
            print(finder.format_results(results))
            
            # Show top recommendation
            if results[0]['score'].total_score >= 70:
                print("\n💡 Top Recommendation:")
                top = results[0]
                print(f"   {top['restaurant'].name} ({top['platform'].upper()})")
                print(f"   Score: {top['score'].total_score}/100")
                print(f"   {top['score'].explanation}")
                
                # Show how to book
                print(f"\n📅 Ready to book for {query}?")
                print(f"   Visit {top['platform']} to make a reservation.")
        else:
            print("No highly-rated restaurants found. Try adjusting your search or preferences.")
            
    except Exception as e:
        print(f"Error during search: {e}")
        print("Please check your internet connection and try again.")


async def evaluate_specific_restaurant(restaurant_name: str, cuisine: str, price: str, address: str):
    """
    Evaluate a specific restaurant against user preferences
    
    Args:
        restaurant_name: Name of the restaurant
        cuisine: Type of cuisine (e.g., "Italian, Mediterranean")
        price: Price range (e.g., "$$", "$$$")
        address: Restaurant address
    """
    try:
        from .evaluator import RestaurantInfo
    except ImportError:
        from evaluator import RestaurantInfo
    
    print(f"\n📊 Evaluating '{restaurant_name}' against your preferences...\n")
    
    # Load user context
    user_context = get_user_context()
    evaluator = RestaurantEvaluator(user_context)
    
    # Create restaurant info (in real usage, this would come from web scraping)
    restaurant = RestaurantInfo(
        name=restaurant_name,
        cuisine_type=[c.strip() for c in cuisine.split(',')],
        price_range=price,
        address=address,
        # These would be extracted from the restaurant's website
        has_vegetarian_menu=True,
        vegetarian_options_count=4,
        wine_list_quality="good",
        allows_corkage=True,
        near_public_transit=True
    )
    
    # Evaluate
    score = evaluator.evaluate_restaurant(restaurant)
    
    # Display results
    print(f"Restaurant: {restaurant_name}")
    print(f"Overall Score: {score.total_score}/100 - {_get_score_emoji(score.total_score)}\n")
    
    print("Score Breakdown:")
    print(f"  • Dietary Fit: {score.dietary_score}/25")
    print(f"  • Cuisine Match: {score.cuisine_score}/20")
    print(f"  • Budget Fit: {score.budget_score}/20")
    print(f"  • Location Access: {score.location_score}/20")
    print(f"  • Wine Program: {score.wine_score}/15\n")
    
    print(f"Summary: {score.explanation}\n")
    
    if score.match_reasons:
        print("✅ Strengths:")
        for reason in score.match_reasons:
            print(f"   • {reason}")
    
    if score.concerns:
        print("\n⚠️  Considerations:")
        for concern in score.concerns:
            print(f"   • {concern}")


def _get_score_emoji(score: float) -> str:
    """Get emoji representation of score"""
    if score >= 85:
        return "🌟"
    elif score >= 70:
        return "✨"
    elif score >= 50:
        return "👍"
    else:
        return "🤔"


# Main entry point
def main():
    """Main entry point for the CLI"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "find":
            # Find restaurants
            query = sys.argv[2] if len(sys.argv) > 2 else "dinner tonight"
            # Support single platform or "all" for all platforms
            if len(sys.argv) > 3 and sys.argv[3].lower() != "all":
                platforms = [sys.argv[3]]
            else:
                platforms = None  # Use all platforms
            asyncio.run(find_dinner_spot(query, platforms))
            
        elif command == "evaluate":
            # Evaluate specific restaurant
            if len(sys.argv) < 6:
                print("Usage: python -m myai evaluate <name> <cuisine> <price> <address>")
                print('Example: python -m myai evaluate "Shizen" "Japanese, Sushi" "$$" "370 14th St, San Francisco"')
            else:
                asyncio.run(evaluate_specific_restaurant(
                    sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
                ))
        else:
            print(f"Unknown command: {command}")
            print("Available commands: find, evaluate")
    else:
        # Default action - find dinner for tonight
        asyncio.run(find_dinner_spot())


if __name__ == "__main__":
    main()