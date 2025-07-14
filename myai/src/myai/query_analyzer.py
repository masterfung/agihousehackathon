"""
Query analyzer that breaks down user input and combines with personal preferences
"""

from typing import Dict, Any
import re
from datetime import datetime
try:
    from .preferences import UserContext
    from .date_parser import parse_date_query, parse_party_size, get_meal_time
except ImportError:
    from preferences import UserContext
    from date_parser import parse_date_query, parse_party_size, get_meal_time


def analyze_query(query: str, context: UserContext) -> Dict[str, Any]:
    """
    Break down the user's query and combine with personal preferences
    Returns a structured dict with all search parameters
    """
    
    # Parse basic elements from query
    date_obj, date_str = parse_date_query(query)
    party_size = parse_party_size(query)
    meal_time = get_meal_time(query)
    
    # Extract any specific requests from query
    query_lower = query.lower()
    
    # Check if user mentioned specific cuisine (overrides preferences)
    mentioned_cuisines = []
    cuisine_keywords = ['italian', 'mexican', 'asian', 'chinese', 'japanese', 'thai', 'indian', 'french', 'american']
    for cuisine in cuisine_keywords:
        if cuisine in query_lower:
            mentioned_cuisines.append(cuisine)
    
    # Check for specific dietary mentions
    dietary_overrides = []
    if 'vegan' in query_lower:
        dietary_overrides.append('vegan')
    elif 'vegetarian' in query_lower:
        dietary_overrides.append('vegetarian')
    
    # Check for location mentions
    location_override = None
    if 'near' in query_lower:
        # Extract location after "near"
        match = re.search(r'near\s+(\w+(?:\s+\w+)*)', query_lower)
        if match:
            location_override = match.group(1)
    
    # Build the complete search context
    search_params = {
        'date': date_obj,
        'date_str': date_str,
        'party_size': party_size,
        'meal_time': meal_time,
        'dietary': dietary_overrides if dietary_overrides else ['vegetarian'] if context.dietary.is_vegetarian else [],
        'cuisines': mentioned_cuisines if mentioned_cuisines else context.cuisine.preferred_cuisines,
        'budget_min': context.budget.min_price_per_dish,
        'budget_max': context.budget.max_price_per_dish,
        'location': location_override if location_override else context.location.zip_code,
        'allergies': context.dietary.allergies,
        'preferences': {
            'wine': context.restaurant.wine_list_important,
            'spice_level': context.dietary.spice_tolerance,
            'ambiance': context.restaurant.ambiance_preferences,
            'transit': context.location.prefers_public_transit
        }
    }
    
    return search_params


def create_enhanced_search_prompt(query: str, context: UserContext) -> str:
    """
    Create an enhanced search prompt that includes both user query and personal preferences
    """
    params = analyze_query(query, context)
    
    prompt = f"""
Search for restaurants with these requirements:

USER REQUEST: {query}

PARSED DETAILS:
- Date: {params['date_str']}
- Time: {params['meal_time']}
- Party size: {params['party_size']} people
- Location: {params['location']}

DIETARY REQUIREMENTS:
- Diet: {', '.join(params['dietary'])}
- Allergies: {', '.join(params['allergies']) if params['allergies'] else 'None'}

PREFERENCES:
- Cuisines: {', '.join(params['cuisines'])}
- Budget: ${params['budget_min']}-${params['budget_max']} per person
- Spice tolerance: {params['preferences']['spice_level']}
- Wine list important: {'Yes' if params['preferences']['wine'] else 'No'}
- Prefers transit accessible: {'Yes' if params['preferences']['transit'] else 'No'}

Find restaurants that match these criteria.
"""
    
    return prompt.strip()


def build_direct_url(platform: str, params: Dict[str, Any]) -> str:
    """Build a direct URL with all search parameters"""
    
    if platform == "opentable":
        # Convert time to 24-hour format
        try:
            from datetime import datetime
            time_obj = datetime.strptime(params['meal_time'], "%I:%M %p")
            hour = time_obj.hour
            minute = time_obj.minute
        except:
            hour = 19  # Default to 7pm
            minute = 0
        
        base_url = "https://www.opentable.com/s"
        url_params = {
            "covers": str(params['party_size']),
            "dateTime": params['date'].strftime(f"%Y-%m-%dT{hour:02d}:{minute:02d}"),
            "metroId": "4",  # San Francisco
            "term": " ".join(params['dietary'] + params['cuisines'][:1]),  # e.g. "vegetarian asian"
            "prices": "2,3",  # $$ and $$$ to match budget
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in url_params.items()])
        return f"{base_url}?{query_string}"
    
    elif platform == "yelp":
        base_url = "https://www.yelp.com/search"
        search_terms = params['dietary'] + params['cuisines'][:1] + ["restaurants"]
        url_params = {
            "find_desc": "+".join(search_terms),
            "find_loc": f"San Francisco, CA {params['location']}",
            "attrs": "RestaurantsReservations",
            "price": "2",  # $$ price range
        }
        query_string = "&".join([f"{k}={v}" for k, v in url_params.items()])
        return f"{base_url}?{query_string}"
    
    return ""


def create_smart_browser_task(platform: str, query: str, context: UserContext) -> str:
    """
    Create a browser task that uses visual screenshot extraction
    """
    params = analyze_query(query, context)
    url = build_direct_url(platform, params)
    
    try:
        from .smart_extractor import create_screenshot_extraction_task
    except ImportError:
        from smart_extractor import create_screenshot_extraction_task
    
    # Use the enhanced screenshot extraction
    return create_screenshot_extraction_task(url, params)