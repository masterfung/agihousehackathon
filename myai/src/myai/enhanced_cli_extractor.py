"""
Enhanced CLI Extractor with Availability Times and Composable Architecture
"""

import subprocess
import os
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .context_engine import ContextualRequest, default_context_engine

@dataclass
class RestaurantResult:
    """Structured restaurant result with all available data"""
    name: str
    cuisine: str
    price_range: str
    location: str
    rating: Optional[str] = None
    availability_times: List[str] = None
    phone: Optional[str] = None
    distance: Optional[str] = None
    special_features: List[str] = None

class EnhancedCLIExtractor:
    """Enhanced CLI-based extraction with availability times and better parsing"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._load_api_key()
        self.timeout = 90
        
    def _load_api_key(self) -> str:
        """Load API key from environment or .env file"""
        # Check environment first
        if 'GOOGLE_API_KEY' in os.environ:
            return os.environ['GOOGLE_API_KEY']
            
        # Check .env file
        env_file = "/Users/jh/Code/exploration/agihousehackathon/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'GOOGLE_API_KEY':
                            return value
        
        raise ValueError("GOOGLE_API_KEY not found in environment or .env file")
    
    def create_enhanced_prompt(self, url: str, context: ContextualRequest) -> str:
        """Create an enhanced prompt that extracts availability times"""
        
        return f"""Go to {url}

TASK: Extract restaurant information with availability times

For each restaurant you see, extract:

1. BASIC INFO:
   - Restaurant name
   - Cuisine type
   - Price range ($ symbols)
   - Neighborhood/location
   - Rating (if visible)

2. AVAILABILITY (IMPORTANT):
   - Available reservation times for {context.meal_type}
   - Look for time slots like "7:00 PM", "7:30 PM", etc.
   - Note if restaurant is "fully booked" or "no availability"

3. ADDITIONAL INFO (if visible):
   - Phone number
   - Distance
   - Special features (outdoor seating, vegetarian menu, etc.)

SEARCH CONTEXT:
- Looking for: {context.party_size} people
- Date: {context.date.strftime('%A, %B %d') if context.date else 'flexible'}
- Meal: {context.meal_type}
- Preferences: {', '.join(context.cuisine_context.get('preferred_cuisines', []))} cuisine

EXTRACTION FORMAT:
For each restaurant, return:

=== RESTAURANT X ===
Name: [Restaurant Name]
Cuisine: [Cuisine Type]
Price: [$ or $$ or $$$]
Location: [Neighborhood]
Rating: [X.X stars or N/A]
Available Times: [7:00 PM, 7:30 PM, 8:00 PM] or [Fully Booked] or [Call for availability]
Phone: [XXX-XXX-XXXX or N/A]
Features: [vegetarian options, outdoor seating, etc.]

=== END RESTAURANT X ===

IMPORTANT: 
- Extract availability times if shown
- If no times visible, note "Check availability" 
- Focus on {context.dietary_context.get('dietary_restrictions', [])} friendly options
- Extract exactly what you see, don't make up data

Stop when you've extracted all visible restaurants or reached 5 restaurants.
"""
    
    def extract_restaurants(self, query: str) -> List[RestaurantResult]:
        """Main extraction method using context engine"""
        
        # Analyze query with context engine
        context = default_context_engine.analyze_request(query)
        
        # Build URL based on context
        url = self._build_url(context)
        
        print(f"🔗 Enhanced URL: {url}")
        print(f"📋 Context: {context.party_size} people, {context.meal_type}")
        print(f"🎯 Relevance: {context.context_relevance}")
        
        # Create enhanced prompt
        prompt = self.create_enhanced_prompt(url, context)
        
        # Execute CLI extraction
        raw_result = self._execute_cli(prompt)
        
        if not raw_result:
            return []
            
        # Parse enhanced results
        restaurants = self._parse_enhanced_results(raw_result)
        
        print(f"✅ Extracted {len(restaurants)} restaurants with availability")
        
        return restaurants
    
    def _build_url(self, context: ContextualRequest) -> str:
        """Build OpenTable URL from context"""
        
        # Base OpenTable search URL
        base_url = "https://www.opentable.com/s"
        
        # Extract date/time info
        if context.date:
            if context.time:
                # Parse time
                hour = 19  # default 7pm
                minute = 0
                try:
                    if 'pm' in context.time.lower():
                        hour_str = context.time.lower().replace('pm', '').strip()
                        if ':' in hour_str:
                            h, m = hour_str.split(':')
                            hour = int(h) + (12 if int(h) < 12 else 0)
                            minute = int(m)
                        else:
                            hour = int(hour_str) + (12 if int(hour_str) < 12 else 0)
                    elif 'am' in context.time.lower():
                        hour_str = context.time.lower().replace('am', '').strip()
                        if ':' in hour_str:
                            h, m = hour_str.split(':')
                            hour = int(h)
                            minute = int(m)
                        else:
                            hour = int(hour_str)
                except:
                    pass
                
                datetime_str = context.date.strftime(f"%Y-%m-%dT{hour:02d}:{minute:02d}")
            else:
                # Default times based on meal type
                meal_times = {
                    'breakfast': '10:00',
                    'lunch': '12:30', 
                    'dinner': '19:00'
                }
                time_str = meal_times.get(context.meal_type, '19:00')
                datetime_str = context.date.strftime(f"%Y-%m-%dT{time_str}")
        else:
            # Default to today dinner
            from datetime import datetime
            datetime_str = datetime.now().strftime("%Y-%m-%dT19:00")
        
        # Build search terms from context
        search_terms = []
        if context.dietary_context:
            if context.dietary_context.get('vegetarian'):
                search_terms.append('vegetarian')
            allergies = context.dietary_context.get('allergies', [])
            if allergies:
                search_terms.extend([f"no {allergy}" for allergy in allergies])
        
        if context.cuisine_context:
            cuisines = context.cuisine_context.get('preferred_cuisines', [])
            if cuisines:
                search_terms.extend(cuisines[:2])  # Limit to 2 cuisines
        
        # Build URL parameters
        params = {
            'covers': str(context.party_size),
            'dateTime': datetime_str,
            'metroId': '4',  # San Francisco
            'term': ' '.join(search_terms),
            'prices': '2,3'  # $$ and $$$
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def _execute_cli(self, prompt: str) -> str:
        """Execute browser-use CLI with enhanced prompt"""
        
        try:
            env = os.environ.copy()
            env['GOOGLE_API_KEY'] = self.api_key
            
            result = subprocess.run([
                "poetry", "run", "browser-use",
                "--model", "gemini-2.5-flash-lite-preview-06-17", 
                "--prompt", prompt
            ],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env=env
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"❌ CLI Error: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ CLI timed out after {self.timeout}s")
            return ""
        except Exception as e:
            print(f"💥 CLI execution failed: {e}")
            return ""
    
    def _parse_enhanced_results(self, raw_output: str) -> List[RestaurantResult]:
        """Parse enhanced CLI output with availability times"""
        
        restaurants = []
        
        # Look for restaurant blocks
        restaurant_blocks = re.findall(r'=== RESTAURANT.*?===(.*?)=== END RESTAURANT.*?===', raw_output, re.DOTALL)
        
        for block in restaurant_blocks:
            restaurant = self._parse_restaurant_block(block)
            if restaurant:
                restaurants.append(restaurant)
        
        # Fallback: if no structured blocks found, try simple parsing
        if not restaurants:
            restaurants = self._parse_simple_output(raw_output)
        
        return restaurants
    
    def _parse_restaurant_block(self, block: str) -> Optional[RestaurantResult]:
        """Parse a structured restaurant block"""
        
        data = {}
        for line in block.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if value and value != 'N/A':
                    data[key] = value
        
        if 'name' not in data:
            return None
            
        # Parse availability times
        availability = []
        if 'available times' in data:
            times_str = data['available times']
            if '[' in times_str and ']' in times_str:
                # Parse list format: [7:00 PM, 7:30 PM, 8:00 PM]
                times_content = times_str.split('[')[1].split(']')[0]
                availability = [t.strip() for t in times_content.split(',') if t.strip()]
            else:
                availability = [times_str]
        
        # Parse features
        features = []
        if 'features' in data:
            features_str = data['features']
            if '[' in features_str and ']' in features_str:
                features_content = features_str.split('[')[1].split(']')[0]
                features = [f.strip() for f in features_content.split(',') if f.strip()]
            else:
                features = [features_str] if features_str else []
        
        return RestaurantResult(
            name=data.get('name', ''),
            cuisine=data.get('cuisine', ''),
            price_range=data.get('price', '$$'),
            location=data.get('location', ''),
            rating=data.get('rating'),
            availability_times=availability,
            phone=data.get('phone'),
            distance=data.get('distance'),
            special_features=features
        )
    
    def _parse_simple_output(self, raw_output: str) -> List[RestaurantResult]:
        """Fallback simple parsing for basic restaurant lists"""
        
        restaurants = []
        
        # Look for numbered lists
        lines = raw_output.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line):
                # Extract restaurant name
                name = re.sub(r'^\d+\.\s*', '', line)
                if name:
                    restaurants.append(RestaurantResult(
                        name=name,
                        cuisine='Asian',  # Default from search
                        price_range='$$',
                        location='San Francisco',
                        availability_times=['Check availability']
                    ))
        
        return restaurants

# Global instance
enhanced_extractor = EnhancedCLIExtractor()

def extract_restaurants_with_times(query: str) -> List[RestaurantResult]:
    """Convenience function for enhanced extraction"""
    return enhanced_extractor.extract_restaurants(query)