"""
Build preference-aware search URLs for each platform
"""

from typing import Dict, Any
from datetime import datetime
from urllib.parse import quote_plus
try:
    from .preferences import UserContext
except ImportError:
    from preferences import UserContext


def build_opentable_url(context: UserContext, date: datetime, party_size: int = 2) -> str:
    """Build OpenTable URL with all preferences pre-filled"""
    # OpenTable metro IDs: 4 = San Francisco
    base_url = "https://www.opentable.com/s"
    
    params = {
        "covers": str(party_size),
        "dateTime": date.strftime("%Y-%m-%dT19:00"),  # 7pm default
        "metroId": "4",  # San Francisco
        "term": "vegetarian",  # Search term
        "prices": "2,3",  # $$ and $$$ (matches $30-50 range)
    }
    
    # Build URL
    query_parts = [f"{k}={v}" for k, v in params.items()]
    return f"{base_url}?{'&'.join(query_parts)}"


def build_yelp_url(context: UserContext) -> str:
    """Build Yelp URL with preferences"""
    base_url = "https://www.yelp.com/search"
    
    # Combine dietary with preferred cuisines
    search_terms = ["vegetarian"]
    if context.cuisine.preferred_cuisines:
        # Add first preferred cuisine
        search_terms.append(context.cuisine.preferred_cuisines[0].lower())
    
    params = {
        "find_desc": "+".join(search_terms),
        "find_loc": f"{context.location.zip_code}",
        "attrs": "RestaurantsReservations",  # Can make reservations
        "price": "2",  # $$ price range
    }
    
    query_parts = [f"{k}={v}" for k, v in params.items()]
    return f"{base_url}?{'&'.join(query_parts)}"


def build_google_url(context: UserContext) -> str:
    """Build Google search URL with preferences"""
    # Build intelligent search query
    search_parts = ["vegetarian"]
    
    # Add cuisines
    if context.cuisine.preferred_cuisines:
        search_parts.extend([c.lower() for c in context.cuisine.preferred_cuisines[:2]])
    
    search_parts.extend(["restaurants", "$30-50", "near", context.location.zip_code])
    
    search_query = " ".join(search_parts)
    encoded_query = quote_plus(search_query)
    
    return f"https://www.google.com/search?q={encoded_query}"


def build_resy_url(context: UserContext, date: datetime, party_size: int = 2) -> str:
    """Build Resy URL - they don't support as many URL params"""
    # Resy uses different URL structure
    # We'll search by cuisine type since they don't handle dietary well
    cuisine = "mexican" if "mexican" in [c.lower() for c in context.cuisine.preferred_cuisines] else "asian"
    
    return f"https://resy.com/cities/sf?query={cuisine}&date={date.strftime('%Y-%m-%d')}&seats={party_size}"


def create_fast_search_task(platform: str, context: UserContext, query: str) -> str:
    """Create optimized search task with pre-built URLs"""
    from .date_parser import parse_date_query, parse_party_size
    
    # Parse query details
    date_obj, date_str = parse_date_query(query)
    party_size = parse_party_size(query)
    
    if platform == "opentable":
        url = build_opentable_url(context, date_obj, party_size)
        return f"""
        Go to: {url}
        
        Once the page loads, immediately extract text content from the first 5 restaurant listings you see.
        For each restaurant, capture: Name | Cuisine | Price | Area
        
        Example format:
        Greens Restaurant | Vegetarian | $$$ | Fort Mason
        
        Just extract what's visible on screen right now.
        """
    
    elif platform == "yelp":
        url = build_yelp_url(context)
        return f"""
        Yelp search for VEGETARIAN restaurants (preferably {', '.join(context.cuisine.preferred_cuisines)}).
        
        1. Go to: {url}
        2. This URL searches for vegetarian + {context.cuisine.preferred_cuisines[0] if context.cuisine.preferred_cuisines else 'All'} restaurants
        3. Wait for search results to load
        4. VERIFY the search box shows "vegetarian" as a search term
        5. From the SEARCH RESULTS (not ads), extract first 5 restaurants:
           - Name
           - Categories (should include "Vegetarian" or "Vegan")
           - Star rating
           - Price level
           - Neighborhood
        
        Format: [Name] | [Categories] | [Rating] | [Price] | [Area]
        
        Example:
        Shizen | Vegan, Sushi Bars | 4.5 | $$ | Mission
        Loving Hut | Vegan, Chinese | 4.0 | $ | Chinatown
        
        ONLY list vegetarian/vegan restaurants!
        """
    
    elif platform == "google":
        url = build_google_url(context)
        return f"""
        Google search for your preferred restaurants.
        
        1. Go to: {url}
        2. This searches for: vegetarian {' '.join(context.cuisine.preferred_cuisines)} restaurants $30-50 near {context.location.zip_code}
        3. Look at the local results (map pack)
        4. Extract first 5 restaurants:
           - Name
           - Rating
           - Price
           - Type/Cuisine
           - Distance
        
        Format: [Name] | [Rating] | [Price] | [Type] | [Distance]
        """
    
    elif platform == "resy":
        url = build_resy_url(context, date_obj, party_size)
        cuisine = "Mexican" if "mexican" in [c.lower() for c in context.cuisine.preferred_cuisines] else "Asian"
        return f"""
        Resy search for {cuisine} restaurants (many have great vegetarian options).
        
        1. Go to: {url}
        2. This searches for:
           - {cuisine} restaurants in SF
           - Date: {date_str}
           - Party size: {party_size}
        3. Get first 5 restaurants shown:
           - Name
           - Cuisine/Type
           - Neighborhood
           - Price range
           - Available times
        
        Format: [Name] | [Type] | [Neighborhood] | [Price] | [Times]
        
        Note: {cuisine} restaurants often have excellent vegetarian options.
        """
    
    return ""