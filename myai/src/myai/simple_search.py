"""
Simplified search approach using direct extraction
"""

from typing import List, Dict, Any
import re

def create_simple_task(platform: str, location: str = "San Francisco") -> str:
    """Create a very simple extraction task"""
    
    if platform == "opentable":
        return f"""
        Extract San Francisco restaurant data from OpenTable.
        
        Steps:
        1. Go to https://www.opentable.com/san-francisco-restaurant-listings
        2. Wait for restaurant cards to load
        3. Look at the first 5-7 restaurant cards on the page
        4. For each restaurant card, find and extract:
           - Restaurant name (the main title)
           - Cuisine type (usually under the name)
           - Price (shown as $ symbols)
           - Neighborhood (location info)
        
        Format each restaurant as:
        [Name] | [Cuisine] | [Price] | [Neighborhood]
        
        Example:
        Greens Restaurant | Vegetarian | $$$ | Fort Mason
        
        List 5 restaurants this way.
        """
    
    elif platform == "yelp":
        return f"""
        Get vegetarian restaurants from Yelp San Francisco.
        
        1. Go to: https://www.yelp.com/search?find_desc=vegetarian&find_loc=San+Francisco+CA
        2. Wait for search results to load
        3. Look at the search results list
        4. For the first 5 restaurants, extract:
           - Business name
           - Categories/cuisine (e.g. "Vegan, Asian Fusion")  
           - Star rating (e.g. "4.5")
           - Price ($ symbols)
           - Neighborhood/area
        
        Format as:
        [Name] | [Categories] | [Rating] | [Price] | [Area]
        
        Example:
        Shizen | Vegan, Sushi Bars | 4.5 | $$ | Mission
        
        Just list 5 restaurants.
        """
    
    elif platform == "google":
        return f"""
        TASK: Extract restaurant data from Google.
        
        1. Navigate to: https://www.google.com/search?q=vegetarian+restaurants+san+francisco+94109
        2. Wait for the local results to appear (the map box with restaurants)
        3. Find the section that shows restaurant listings
        4. For each restaurant in the local results, extract:
           - The restaurant name
           - The star rating (e.g. "4.5")
           - The price level ($ symbols)
           - The restaurant type/cuisine
        
        Return as simple list:
        1. [Name] | [Rating] | [Price] | [Type]
        2. [Name] | [Rating] | [Price] | [Type]
        etc.
        
        Just the first 5 restaurants from the local pack.
        """
    
    elif platform == "resy":
        return f"""
        SIMPLE TASK: Get Resy restaurant listings.
        
        1. Go to: https://resy.com/cities/sf
        2. Wait 3 seconds
        3. Extract ALL restaurant names and info visible on page
        4. Just dump everything you see
        
        Raw text only.
        """
    
    return ""


def parse_raw_results(raw_text: str, platform: str) -> List[Dict[str, Any]]:
    """Parse raw extracted text into restaurant data"""
    restaurants = []
    
    if not raw_text or len(raw_text) < 50:
        return []
    
    # Split into potential restaurant blocks
    lines = raw_text.split('\n')
    current_restaurant = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Look for patterns that indicate restaurant names
        # Usually restaurant names are in title case and don't have too many words
        if (platform in ["yelp", "google"] and 
            len(line.split()) <= 5 and 
            line[0].isupper() and 
            not any(skip in line.lower() for skip in ['search', 'filter', 'map', 'sign', 'ad', 'sponsored'])):
            
            # Save previous restaurant if exists
            if current_restaurant.get('name'):
                restaurants.append(current_restaurant)
            
            # Start new restaurant
            current_restaurant = {'name': line}
            
        # Look for ratings (e.g., "4.5", "4.5 stars", "4.5★")
        elif current_restaurant.get('name') and re.search(r'\d\.\d', line):
            match = re.search(r'(\d\.\d)', line)
            if match:
                current_restaurant['rating'] = match.group(1)
        
        # Look for price indicators
        elif current_restaurant.get('name') and '$' in line and len(line) <= 10:
            price_match = re.search(r'(\$+)', line)
            if price_match:
                current_restaurant['price'] = price_match.group(1)
        
        # Look for cuisine types (common patterns)
        elif (current_restaurant.get('name') and 
              any(cuisine in line.lower() for cuisine in ['italian', 'mexican', 'asian', 'vegan', 'vegetarian', 'chinese', 'thai', 'japanese', 'indian'])):
            current_restaurant['cuisine'] = line
        
        # Look for addresses/neighborhoods
        elif (current_restaurant.get('name') and 
              any(area in line.lower() for area in ['mission', 'soma', 'marina', 'castro', 'sunset', 'richmond', 'nob hill', 'chinatown', 'haight'])):
            current_restaurant['address'] = line
    
    # Don't forget the last restaurant
    if current_restaurant.get('name'):
        restaurants.append(current_restaurant)
    
    # Filter out incomplete entries
    valid_restaurants = []
    for r in restaurants:
        if r.get('name') and len(r) >= 2:  # Need at least name + 1 other field
            valid_restaurants.append(r)
    
    return valid_restaurants[:10]  # Return up to 10 to have good selection