"""
Search query optimization based on user context priorities
"""

from typing import List, Dict, Any
try:
    from .preferences import UserContext
except ImportError:
    from preferences import UserContext


class SearchQueryBuilder:
    """Builds optimized search queries based on context priorities"""
    
    def __init__(self, context: UserContext):
        self.context = context
    
    def build_google_search(self) -> str:
        """
        Build Google Maps search query with smart prioritization
        Priority: dietary > location > cuisine > features
        """
        components = []
        
        # 1. Dietary restrictions (highest priority)
        if self.context.dietary.is_vegetarian:
            components.append("vegetarian")
        
        # 2. Add ONE primary cuisine (not all)
        if self.context.cuisine.preferred_cuisines:
            # Pick the most specific/searchable cuisine
            primary_cuisine = self._get_primary_cuisine()
            if primary_cuisine:
                components.append(primary_cuisine)
        
        # 3. Add "restaurants"
        components.append("restaurants")
        
        # 4. Location
        components.append(f"near {self.context.location.zip_code}")
        
        return " ".join(components)
    
    def build_yelp_search(self) -> str:
        """Build Yelp search query"""
        if self.context.dietary.is_vegetarian:
            return f"vegetarian restaurants"
        else:
            cuisine = self._get_primary_cuisine()
            return f"{cuisine} restaurants" if cuisine else "restaurants"
    
    def build_opentable_search(self) -> str:
        """Build OpenTable search query"""
        # OpenTable works better with cuisine or neighborhood search
        if self.context.dietary.is_vegetarian:
            return "vegetarian"
        else:
            return self.context.location.city
    
    def build_resy_search(self) -> str:
        """Build Resy search query - cuisine-focused"""
        # Resy doesn't handle dietary restrictions well, use cuisine instead
        if self.context.cuisine.preferred_cuisines:
            # Pick Mexican first if available (tends to have good veg options)
            for cuisine in ["mexican", "asian", "italian"]:
                if any(cuisine in pref.lower() for pref in self.context.cuisine.preferred_cuisines):
                    return cuisine.capitalize()
        return "Asian"  # Default to Asian as it often has veg options
    
    def _get_primary_cuisine(self) -> str:
        """Get the most specific/searchable cuisine from preferences"""
        cuisine_priority = {
            "mexican": 1,  # Very specific
            "asian": 3,    # Too broad, better to use specific Asian cuisines
            "italian": 1,
            "indian": 1,
            "thai": 1,
            "chinese": 1,
            "japanese": 1,
            "vietnamese": 1
        }
        
        # Find the best cuisine to search with
        best_cuisine = ""
        best_priority = 999
        
        for cuisine in self.context.cuisine.preferred_cuisines:
            cuisine_lower = cuisine.lower()
            priority = cuisine_priority.get(cuisine_lower, 2)
            
            if priority < best_priority:
                best_priority = priority
                best_cuisine = cuisine_lower
        
        # If "asian" is preferred, pick a specific Asian cuisine
        if best_cuisine == "asian":
            return "japanese"  # Default to Japanese as it's vegetarian-friendly
        
        return best_cuisine


class ContextPriority:
    """Defines importance ranking for different context elements"""
    
    PRIORITIES = {
        "dietary_restrictions": 1,  # Highest - must have
        "location": 2,              # Very important
        "budget": 3,                # Important
        "cuisine": 4,               # Nice to have
        "wine": 5,                  # Nice to have
        "ambiance": 6               # Lowest priority
    }
    
    @classmethod
    def get_context_markdown(cls, context: UserContext) -> str:
        """Convert context to prioritized markdown format"""
        sections = []
        
        # Dietary (Priority 1)
        dietary_items = []
        if context.dietary.is_vegetarian:
            dietary_items.append(f"- **Vegetarian** (not just salads - {context.dietary.vegetarian_notes})")
        if context.dietary.allergies:
            dietary_items.append(f"- **Allergies**: {', '.join(context.dietary.allergies)}")
        if context.dietary.spice_tolerance == "mild":
            dietary_items.append(f"- **Spice**: {context.dietary.spice_notes}")
        
        if dietary_items:
            sections.append(f"## 🚨 Must Have (Critical)\n" + "\n".join(dietary_items))
        
        # Location & Budget (Priority 2-3)
        important_items = []
        important_items.append(f"- **Location**: {context.location.zip_code} ({context.location.city})")
        important_items.append(f"- **Budget**: ${context.budget.min_price_per_dish}-${context.budget.max_price_per_dish} per dish")
        if context.location.prefers_public_transit:
            important_items.append(f"- **Transit**: {context.location.transit_notes}")
        
        sections.append(f"## ⚡ Important\n" + "\n".join(important_items))
        
        # Preferences (Priority 4-6)
        pref_items = []
        if context.cuisine.preferred_cuisines:
            pref_items.append(f"- **Cuisine**: Prefers {', '.join(context.cuisine.preferred_cuisines)}")
        if context.restaurant.wine_list_important:
            pref_items.append(f"- **Wine**: Good wine list important")
            if context.restaurant.corkage_preferred:
                pref_items.append(f"- **Corkage**: Preferred")
        
        if pref_items:
            sections.append(f"## 👍 Nice to Have\n" + "\n".join(pref_items))
        
        return "\n\n".join(sections)