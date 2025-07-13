"""
Restaurant AI - Clean, Composable Interface

Main interface for restaurant finding with:
- Centralized context engine
- Enhanced CLI extraction with availability times
- MCP server compatibility
- Modular, composable architecture
"""

from typing import List, Dict, Any, Optional
from dataclasses import asdict
import json
from datetime import datetime

from .context_engine import default_context_engine, ContextualRequest
from .universal_extractor import universal_extractor, ExtractionResult

class RestaurantAI:
    """Main restaurant AI interface"""
    
    def __init__(self, mcp_data: Optional[Dict[str, Any]] = None):
        """Initialize with optional MCP server data"""
        self.context_engine = default_context_engine
        self.extractor = universal_extractor
        
        # Load MCP data if provided
        if mcp_data:
            self.context_engine.from_mcp_data(mcp_data)
    
    def find_restaurants(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for restaurant finding
        
        Args:
            query: Natural language query like "lunch for 3 next tuesday"
            
        Returns:
            Dict with restaurants, context, and metadata
        """
        
        print(f"🚀 Processing: '{query}'")
        
        # Analyze query with context engine
        context = self.context_engine.analyze_request(query)
        
        print(f"📊 Context Analysis:")
        print(f"  • Intent: {context.intent}")
        print(f"  • Party: {context.party_size} people")
        print(f"  • Meal: {context.meal_type}")
        print(f"  • Relevance: {self._format_relevance(context.context_relevance)}")
        
        # Extract restaurants with universal CLI
        restaurants = self.extractor.extract_restaurants(query, "opentable", context)
        
        # Format results
        results = {
            'query': query,
            'context': asdict(context),
            'restaurants': [asdict(r) for r in restaurants],
            'summary': self._create_summary(restaurants, context),
            'timestamp': datetime.now().isoformat()
        }
        
        # Display results
        self._display_results(restaurants, context)
        
        return results
    
    def _format_relevance(self, relevance: Dict[str, float]) -> str:
        """Format relevance scores for display"""
        relevant = [f"{k}({v:.1f})" for k, v in relevance.items() if v > 0.1]
        return ", ".join(relevant) if relevant else "general"
    
    def _create_summary(self, restaurants: List[ExtractionResult], context: ContextualRequest) -> Dict[str, Any]:
        """Create a summary of the search results"""
        
        total_found = len(restaurants)
        with_availability = len([r for r in restaurants if r.availability_times and r.availability_times != ['Check availability']])
        
        cuisines = list(set([r.cuisine for r in restaurants if r.cuisine]))
        price_ranges = list(set([r.price_range for r in restaurants if r.price_range]))
        
        return {
            'total_restaurants': total_found,
            'with_availability': with_availability,
            'cuisines_found': cuisines,
            'price_ranges': price_ranges,
            'context_used': {k: v for k, v in context.context_relevance.items() if v > 0.1}
        }
    
    def _display_results(self, restaurants: List[ExtractionResult], context: ContextualRequest):
        """Display formatted results to user"""
        
        if not restaurants:
            print("❌ No restaurants found")
            return
        
        print(f"\n🎯 Found {len(restaurants)} restaurants:")
        print(f"📅 For: {context.party_size} people, {context.meal_type}")
        
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\n{i}. **{restaurant.name}**")
            print(f"   🍽️  {restaurant.cuisine} • {restaurant.price_range} • {restaurant.location}")
            
            if restaurant.rating:
                print(f"   ⭐ {restaurant.rating}")
            
            if restaurant.availability_times:
                times_str = ", ".join(restaurant.availability_times[:3])  # Show first 3 times
                if len(restaurant.availability_times) > 3:
                    times_str += f" (+{len(restaurant.availability_times)-3} more)"
                print(f"   🕐 Available: {times_str}")
            
            if restaurant.features:
                features_str = ", ".join(restaurant.features[:2])
                print(f"   ✨ {features_str}")
    
    def get_context_status(self) -> Dict[str, Any]:
        """Get current context engine status"""
        return {
            'personal_data_loaded': bool(self.context_engine.personal_data),
            'context_sections': list(self.context_engine.personal_data.keys()),
            'keyword_categories': list(self.context_engine.context_keywords.keys()),
            'extractor_ready': bool(self.extractor.api_key)
        }
    
    def export_for_mcp(self) -> Dict[str, Any]:
        """Export current state for MCP server"""
        return self.context_engine.to_mcp_format()
    
    def update_from_mcp(self, mcp_data: Dict[str, Any]):
        """Update context from MCP server data"""
        self.context_engine.from_mcp_data(mcp_data)
    
    def quick_find(self, query: str) -> List[str]:
        """Quick find that returns just restaurant names"""
        results = self.find_restaurants(query)
        return [r['name'] for r in results['restaurants']]

# Global instance for easy access
restaurant_ai = RestaurantAI()

# Convenience functions
def find_restaurants(query: str) -> Dict[str, Any]:
    """Find restaurants with full context analysis"""
    return restaurant_ai.find_restaurants(query)

def quick_find(query: str) -> List[str]:
    """Quick restaurant name search"""
    return restaurant_ai.quick_find(query)