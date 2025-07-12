"""
Site-specific optimizations for restaurant search platforms
Each platform has unique filters and UI elements we can leverage
"""

from typing import Dict, List, Any
try:
    from .preferences import UserContext
    from .date_parser import parse_date_query, get_meal_time, parse_party_size
    from .search_optimizer import SearchQueryBuilder, ContextPriority
    from .simple_search import create_simple_task
    from .preference_urls import create_fast_search_task
except ImportError:
    from preferences import UserContext
    from date_parser import parse_date_query, get_meal_time, parse_party_size
    from search_optimizer import SearchQueryBuilder, ContextPriority
    from simple_search import create_simple_task
    from preference_urls import create_fast_search_task


class SiteOptimizations:
    """Platform-specific search optimizations"""
    
    @staticmethod
    def get_opentable_filters(context: UserContext) -> Dict[str, Any]:
        """Get OpenTable-specific filters"""
        return {
            "search_term": "vegetarian",
            "filters": {
                "cuisine": ["Asian", "Mexican", "Latin American", "Vegetarian"],
                "price": ["$", "$$"],  # Under $30 and $31-50
                "neighborhood": "Tenderloin/Nob Hill",
                "features": ["Good for groups", "Good wine list"],
                "dietary": ["Vegetarian friendly", "Vegan options"]
            },
            "sort": "Best match"
        }
    
    @staticmethod
    def get_resy_filters(context: UserContext) -> Dict[str, Any]:
        """Get Resy-specific filters"""
        return {
            "search_term": "vegetarian friendly",
            "filters": {
                "cuisine": ["Asian", "Mexican", "Plant-based"],
                "price": ["$$"],  # Moderate pricing
                "neighborhood": ["Nob Hill", "Tenderloin", "Union Square"],
                "amenities": ["Natural Wine", "Wine Focused"]
            }
        }
    
    @staticmethod
    def get_yelp_filters(context: UserContext) -> Dict[str, Any]:
        """Get Yelp-specific filters"""
        return {
            "search_term": "vegetarian restaurants",
            "filters": {
                "category": ["vegetarian", "vegan", "asian", "mexican"],
                "price": ["2"],  # $$ = 2 on Yelp
                "features": ["Good for Dinner", "Takes Reservations"],
                "distance": "Walking (1 mi.)",
                "sort": "Recommended"
            }
        }
    
    @staticmethod
    def get_google_filters(context: UserContext) -> Dict[str, Any]:
        """Get Google Maps-specific filters"""
        return {
            "search_term": "vegetarian asian mexican restaurants near 94109",
            "filters": {
                "price": ["Moderate"],
                "rating": "4+ stars",
                "open_now": True,
                "dine_in": True
            }
        }


def create_optimized_task(platform: str, context: UserContext, query: str = "dinner tonight", use_simple: bool = False) -> str:
    """Create an optimized task for each platform using their native filters"""
    
    # Use preference-aware fast search
    return create_fast_search_task(platform, context, query)