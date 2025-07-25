"""
Centralized Context Engine for Personal Preferences and Prompt Analysis

This module provides a unified system for:
1. Storing personal preferences in a structured, parseable format
2. Analyzing prompts to determine what context is relevant
3. Providing context to various AI models (MCP servers, direct calls, etc.)
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Set
import re
from datetime import datetime
import json

# ============================================================================
# PERSONAL CONTEXT DATA (JSON format for easy access and modification)
# ============================================================================

PERSONAL_CONTEXT = {
    "dietary_requirements": {
        "vegetarian": True,
        "keto": True,
        "dietary_restrictions": ["vegetarian", "keto"]
    },
    "cuisine_preferences": {
        "preferred_cuisines": ["thai", "indian"],
        "thai": True,
        "indian": True
    },
    "budget_pricing": {
        "cheap": True,
        "preferred_price_range": "$"
    },
    "dining_preferences": {
        "baking": True,
        "party_size_typical": 2
    },
    "meal_prep": {
        "chicken_and_rice": True
    },
    "location_transit": {
        "home_zip": "94109",
        "preferred_neighborhoods": ["san_francisco"]
    },
    "availability_preferences": {
        "preferred_meal_times": {
            "breakfast": "9:00-11:00",
            "lunch": "12:00-14:00",
            "dinner": "18:00-21:00"
        }
    }
}

@dataclass
class ContextualRequest:
    """Represents a parsed user request with relevant context"""
    
    # Request details
    original_query: str
    intent: str  # "find_restaurants", "make_reservation", etc.
    
    # Extracted parameters
    party_size: int
    date: Optional[datetime]
    time: Optional[str]
    meal_type: str  # breakfast, lunch, dinner
    
    # Relevant personal context
    dietary_context: Dict[str, Any]
    cuisine_context: Dict[str, Any] 
    budget_context: Dict[str, Any]
    location_context: Dict[str, Any]
    timing_context: Dict[str, Any]
    
    # Context relevance scores
    context_relevance: Dict[str, float]


class ContextEngine:
    """Intelligent context engine that analyzes prompts and provides relevant personal data"""
    
    def __init__(self, personal_context: Dict[str, Any] = None):
        if personal_context is None:
            personal_context = PERSONAL_CONTEXT
        self.personal_data = personal_context if isinstance(personal_context, dict) else self._parse_personal_context(personal_context)
        self.context_keywords = self._build_context_keywords()
    
    def _parse_personal_context(self, context_text: str) -> Dict[str, Any]:
        """Parse the docstring-style personal context into structured data"""
        
        data = {}
        current_section = None
        
        for line in context_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Skip only single # comments, not section headers ##
            if line.startswith('#') and not line.startswith('##'):
                continue
                
            # Section headers
            if line.startswith('## '):
                current_section = line[3:].lower().replace(' ', '_').replace('&', '_')
                data[current_section] = {}
                continue
            
            # Parse key-value pairs
            if ':' in line and current_section:
                if line.startswith('- '):
                    line = line[2:]
                
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Parse different value types
                if value.startswith('[') and value.endswith(']'):
                    # List
                    value = [item.strip().strip('"') for item in value[1:-1].split(',') if item.strip()]
                elif value.startswith('"') and value.endswith('"'):
                    # String
                    value = value[1:-1]
                elif value.lower() in ['true', 'false']:
                    # Boolean
                    value = value.lower() == 'true'
                elif value.replace('.', '').isdigit():
                    # Number
                    value = float(value) if '.' in value else int(value)
                
                data[current_section][key] = value
        
        return data
    
    def _build_context_keywords(self) -> Dict[str, Set[str]]:
        """Build keyword mappings for context relevance detection"""
        
        return {
            'dietary': {
                'vegetarian', 'vegan', 'allergy', 'allergic', 'spicy', 'mild', 
                'meat', 'dairy', 'gluten', 'diet', 'dietary'
            },
            'cuisine': {
                'asian', 'mexican', 'thai', 'chinese', 'indian', 'italian', 
                'japanese', 'vietnamese', 'cuisine', 'food', 'restaurant'
            },
            'budget': {
                'cheap', 'expensive', 'budget', 'price', 'cost', 'affordable',
                '$', '$$', '$$$', 'money', 'spend'
            },
            'location': {
                'near', 'close', 'distance', 'neighborhood', 'area', 'transit',
                'walk', 'drive', 'uber', 'bart', 'muni'
            },
            'timing': {
                'time', 'when', 'available', 'reservation', 'book', 'table',
                'tonight', 'tomorrow', 'weekend', 'lunch', 'dinner', 'breakfast'
            }
        }
    
    def analyze_request(self, query: str) -> ContextualRequest:
        """Analyze a user request and determine what personal context is relevant"""
        
        query_lower = query.lower()
        
        # Extract basic parameters
        party_size = self._extract_party_size(query)
        date_info = self._extract_date(query)
        time_info = self._extract_time(query)
        meal_type = self._extract_meal_type(query)
        intent = self._extract_intent(query)
        
        # Determine context relevance
        relevance = {}
        for context_type, keywords in self.context_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower) / len(keywords)
            relevance[context_type] = score
        
        # Build relevant context data
        dietary_context = self.personal_data.get('dietary_requirements', {}) if relevance['dietary'] > 0.1 else {}
        # Always include cuisine preferences as defaults for restaurant searches
        cuisine_context = self.personal_data.get('cuisine_preferences', {})
        budget_context = self.personal_data.get('budget_pricing', {}) if relevance['budget'] > 0.1 else {}
        location_context = self.personal_data.get('location_transit', {}) if relevance['location'] > 0.1 else {}
        timing_context = self.personal_data.get('availability_preferences', {}) if relevance['timing'] > 0.1 else {}
        
        return ContextualRequest(
            original_query=query,
            intent=intent,
            party_size=party_size,
            date=date_info,
            time=time_info,
            meal_type=meal_type,
            dietary_context=dietary_context,
            cuisine_context=cuisine_context,
            budget_context=budget_context,
            location_context=location_context,
            timing_context=timing_context,
            context_relevance=relevance
        )
    
    def _extract_party_size(self, query: str) -> int:
        """Extract party size from query"""
        patterns = [
            r'for (\d+) people',
            r'for (\d+)',
            r'party of (\d+)',
            r'table for (\d+)',
            r'(\d+) people'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        
        return self.personal_data.get('dining_preferences', {}).get('party_size_typical', 2)
    
    def _extract_date(self, query: str) -> Optional[datetime]:
        """Extract date from query with better parsing"""
        from datetime import timedelta
        
        query_lower = query.lower()
        today = datetime.now()
        
        if 'tomorrow' in query_lower:
            return today + timedelta(days=1)
        elif 'tonight' in query_lower or 'today' in query_lower:
            return today
        elif 'next week' in query_lower:
            return today + timedelta(days=7)
        else:
            # Check for day names
            days = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }
            
            for day_name, day_num in days.items():
                if day_name in query_lower:
                    days_ahead = (day_num - today.weekday()) % 7
                    if days_ahead == 0:
                        days_ahead = 7  # Next week's day
                    return today + timedelta(days=days_ahead)
        
        return None
    
    def _extract_time(self, query: str) -> Optional[str]:
        """Extract time from query"""
        time_patterns = [
            r'(\d{1,2}):(\\d{2})\\s*(am|pm)',
            r'(\d{1,2})\\s*(am|pm)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(0)
        
        return None
    
    def _extract_meal_type(self, query: str) -> str:
        """Extract meal type from query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['breakfast', 'brunch']):
            return 'breakfast'
        elif 'lunch' in query_lower:
            return 'lunch'
        elif any(word in query_lower for word in ['dinner', 'tonight']):
            return 'dinner'
        return 'dinner'  # default
    
    def _extract_intent(self, query: str) -> str:
        """Extract user intent from query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['find', 'search', 'recommend']):
            return 'find_restaurants'
        elif any(word in query_lower for word in ['book', 'reserve', 'table']):
            return 'make_reservation'
        return 'find_restaurants'  # default
    
    def build_search_context(self, request: ContextualRequest) -> Dict[str, Any]:
        """Build optimized search context for restaurant finding"""
        
        context = {
            'party_size': request.party_size,
            'meal_type': request.meal_type,
            'intent': request.intent
        }
        
        # Add relevant personal context based on relevance scores
        if request.context_relevance['dietary'] > 0.1:
            context['dietary'] = request.dietary_context
        
        if request.context_relevance['cuisine'] > 0.1:
            context['cuisine'] = request.cuisine_context
        
        if request.context_relevance['budget'] > 0.1:
            context['budget'] = request.budget_context
            
        if request.context_relevance['location'] > 0.1:
            context['location'] = request.location_context
            
        if request.context_relevance['timing'] > 0.1:
            context['timing'] = request.timing_context
        
        return context
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Export personal context in MCP-compatible format"""
        return {
            'personal_context': self.personal_data,
            'context_keywords': {k: list(v) for k, v in self.context_keywords.items()},
            'last_updated': datetime.now().isoformat()
        }
    
    def from_mcp_data(self, mcp_data: Dict[str, Any]) -> None:
        """Load personal context from MCP server data"""
        if 'personal_context' in mcp_data:
            self.personal_data = mcp_data['personal_context']
        if 'context_keywords' in mcp_data:
            self.context_keywords = {k: set(v) for k, v in mcp_data['context_keywords'].items()}


# Global instance - can be replaced with MCP server data
default_context_engine = ContextEngine()

def analyze_query_with_context(query: str) -> ContextualRequest:
    """Convenience function for analyzing queries with default context"""
    return default_context_engine.analyze_request(query)