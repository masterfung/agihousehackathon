"""
Personal preferences module - hardcoded data that will eventually come from MCP server
This represents the user's personal context for restaurant selection
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DietaryPreferences:
    """User's dietary restrictions and preferences"""
    is_vegetarian: bool = True
    vegetarian_notes: str = "Not just salads - wants proper vegetarian meals with variety"
    allergies: List[str] = field(default_factory=lambda: ["peanut"])
    spice_tolerance: str = "mild"  # mild, medium, hot
    spice_notes: str = "Cannot stand too spicy food"


@dataclass
class CuisinePreferences:
    """User's cuisine preferences"""
    preferred_cuisines: List[str] = field(default_factory=lambda: ["asian", "mexican"])
    cuisine_notes: str = "Wants variety but flexible with different food types"
    avoid_cuisines: List[str] = field(default_factory=list)


@dataclass
class BudgetPreferences:
    """User's budget constraints"""
    min_price_per_dish: float = 30.0
    max_price_per_dish: float = 50.0
    currency: str = "USD"
    budget_notes: str = "Prefers mid-range pricing"


@dataclass
class LocationPreferences:
    """User's location and transportation preferences"""
    home_address: str = "500 Hyde St, San Francisco, CA 94109"
    zip_code: str = "94109"
    city: str = "San Francisco"
    state: str = "CA"
    country: str = "USA"
    
    has_car: bool = False
    uses_rideshare: bool = True
    prefers_public_transit: bool = True
    max_distance_miles: float = 5.0
    transit_notes: str = "Prefers locations close to public transit in the Bay Area"


@dataclass
class RestaurantPreferences:
    """User's restaurant-specific preferences"""
    wine_list_important: bool = True
    corkage_preferred: bool = True
    ambiance_preferences: List[str] = field(default_factory=lambda: ["casual", "upscale casual", "fine dining"])
    meal_preferences: Dict[str, Any] = field(default_factory=lambda: {
        "dinner": True,
        "lunch": True,
        "brunch": False,
        "breakfast": False
    })


@dataclass
class UserContext:
    """Complete user context combining all preferences"""
    dietary: DietaryPreferences = field(default_factory=DietaryPreferences)
    cuisine: CuisinePreferences = field(default_factory=CuisinePreferences)
    budget: BudgetPreferences = field(default_factory=BudgetPreferences)
    location: LocationPreferences = field(default_factory=LocationPreferences)
    restaurant: RestaurantPreferences = field(default_factory=RestaurantPreferences)
    
    # Metadata for MCP server compatibility
    user_id: str = "user_123"
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            "user_id": self.user_id,
            "version": self.version,
            "last_updated": self.last_updated.isoformat(),
            "preferences": {
                "dietary": {
                    "is_vegetarian": self.dietary.is_vegetarian,
                    "vegetarian_notes": self.dietary.vegetarian_notes,
                    "allergies": self.dietary.allergies,
                    "spice_tolerance": self.dietary.spice_tolerance,
                    "spice_notes": self.dietary.spice_notes
                },
                "cuisine": {
                    "preferred": self.cuisine.preferred_cuisines,
                    "notes": self.cuisine.cuisine_notes,
                    "avoid": self.cuisine.avoid_cuisines
                },
                "budget": {
                    "min_per_dish": self.budget.min_price_per_dish,
                    "max_per_dish": self.budget.max_price_per_dish,
                    "currency": self.budget.currency,
                    "notes": self.budget.budget_notes
                },
                "location": {
                    "home": self.location.home_address,
                    "city": self.location.city,
                    "zip": self.location.zip_code,
                    "transportation": {
                        "has_car": self.location.has_car,
                        "rideshare": self.location.uses_rideshare,
                        "prefers_transit": self.location.prefers_public_transit,
                        "max_distance": self.location.max_distance_miles
                    },
                    "notes": self.location.transit_notes
                },
                "restaurant": {
                    "wine_important": self.restaurant.wine_list_important,
                    "corkage": self.restaurant.corkage_preferred,
                    "ambiance": self.restaurant.ambiance_preferences,
                    "meals": self.restaurant.meal_preferences
                }
            }
        }
    
    def get_search_keywords(self) -> List[str]:
        """Generate search keywords based on preferences"""
        keywords = []
        
        if self.dietary.is_vegetarian:
            keywords.extend(["vegetarian", "plant-based", "vegan-friendly"])
        
        keywords.extend(self.cuisine.preferred_cuisines)
        
        if self.restaurant.wine_list_important:
            keywords.append("wine list")
        
        if self.restaurant.corkage_preferred:
            keywords.append("corkage")
            
        return keywords
    
    def get_negative_keywords(self) -> List[str]:
        """Keywords to avoid in search results"""
        keywords = []
        
        if self.dietary.spice_tolerance == "mild":
            keywords.extend(["very spicy", "extra hot", "szechuan", "thai spicy"])
            
        if self.dietary.is_vegetarian:
            keywords.extend(["steakhouse", "bbq", "seafood-only"])
            
        return keywords


# Create the default user context instance
def get_user_context() -> UserContext:
    """Get the hardcoded user context (will be replaced by MCP server data)"""
    return UserContext()


# Helper function to format preferences for prompts
def format_preferences_for_prompt(context: UserContext) -> str:
    """Format user preferences as a natural language prompt"""
    prompt_parts = []
    
    # Dietary
    prompt_parts.append(f"I am a vegetarian who {context.dietary.vegetarian_notes.lower()}.")
    if context.dietary.allergies:
        prompt_parts.append(f"I am allergic to {', '.join(context.dietary.allergies)}.")
    prompt_parts.append(f"I {context.dietary.spice_notes.lower()}.")
    
    # Cuisine
    prompt_parts.append(f"I strongly prefer {', '.join(context.cuisine.preferred_cuisines)} cuisine.")
    prompt_parts.append(context.cuisine.cuisine_notes)
    
    # Budget
    prompt_parts.append(f"My budget is ${context.budget.min_price_per_dish}-${context.budget.max_price_per_dish} per dish.")
    
    # Location
    prompt_parts.append(f"I live in {context.location.city}, {context.location.zip_code}.")
    prompt_parts.append(context.location.transit_notes)
    
    # Restaurant preferences
    if context.restaurant.wine_list_important:
        prompt_parts.append("A good wine list is important to me.")
    if context.restaurant.corkage_preferred:
        prompt_parts.append("I prefer restaurants that allow corkage.")
    
    return " ".join(prompt_parts)