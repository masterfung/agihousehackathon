"""
Smart extraction with screenshot-based data collection and real-time ranking
"""

from typing import List, Dict, Any
import re


def create_screenshot_extraction_task(url: str, query_params: Dict[str, Any]) -> str:
    """
    Create a simple task focused on quick extraction
    """
    
    return f"""
Go to: {url}

Search parameters:
- {query_params['party_size']} people
- {query_params['date_str']} at {query_params['meal_time']}
- Looking for: {', '.join(query_params['dietary'])} {', '.join(query_params['cuisines'])}

TASK:
1. Let page load (3 seconds)
2. Look at what's visible and extract restaurant data
3. Scroll down once and extract more
4. Return the restaurants you found

Extract format:
[Name] | [Cuisine] | [Price] | [Location]

Prioritize vegetarian-friendly options.
"""


def create_visual_extraction_task(url: str, preferences: Dict[str, Any]) -> str:
    """
    Create a task that emphasizes visual extraction from screenshots
    """
    
    dietary = preferences.get('dietary', [])
    cuisines = preferences.get('cuisines', [])
    
    return f"""
Open browser and go to: {url}

SCREENSHOT-BASED EXTRACTION:
1. Wait for page to load (3 seconds)
2. Take a screenshot of the visible area
3. In the screenshot, identify restaurant listings/cards
4. Extract the following from what you SEE:
   - Restaurant names (usually the largest text in each card)
   - Cuisine types (often listed below the name)
   - Price indicators ($ symbols)
   - Neighborhoods/locations
   - Ratings (stars or numbers)
   - Any "Vegetarian" or "Vegan" labels

5. After extracting from first view, scroll down to see more
6. Take another screenshot and extract NEW restaurants

FOCUS ON VISUAL ELEMENTS:
- Restaurant cards often have borders or are in a grid
- Names are usually prominent/bold
- Look for $ symbols for pricing
- Cuisine types often in smaller text
- Ratings shown as stars or numbers

Looking for: {', '.join(dietary)} {', '.join(cuisines)} restaurants

Return in this exact format:
SCREENSHOT 1 RESTAURANTS:
1. [Name] | [Cuisine] | [Price] | [Location]
2. [Name] | [Cuisine] | [Price] | [Location]
...

SCREENSHOT 2 RESTAURANTS:
1. [Name] | [Cuisine] | [Price] | [Location]
2. [Name] | [Cuisine] | [Price] | [Location]
...

BEST VEGETARIAN MATCHES:
1. [Restaurant] - [Why it's good]
2. [Restaurant] - [Why it's good]
3. [Restaurant] - [Why it's good]
"""


def parse_screenshot_results(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parse restaurant data from screenshot-based extraction
    """
    restaurants = []
    
    # Look for sections in the output
    sections = raw_text.split('===')[1:]  # Split by section markers
    
    # First try to find the extracted restaurants section
    for section in sections:
        if 'EXTRACTED RESTAURANTS' in section or 'SCREENSHOT' in section:
            lines = section.split('\n')
            for line in lines:
                if '|' in line:
                    # Remove numbering if present
                    line = re.sub(r'^\d+\.\s*', '', line.strip())
                    
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:  # Need at least name, cuisine, price
                        restaurant = {
                            'name': parts[0],
                            'cuisine': parts[1] if len(parts) > 1 else '',
                            'price': parts[2] if len(parts) > 2 else '',
                            'neighborhood': parts[3] if len(parts) > 3 else '',
                            'rating': parts[4] if len(parts) > 4 else ''
                        }
                        
                        # Skip if it's clearly not a restaurant
                        if restaurant['name'] and not any(skip in restaurant['name'].lower() 
                            for skip in ['search', 'filter', 'results', 'showing', 'found', 'screenshot', 'extracted']):
                            restaurants.append(restaurant)
    
    # If no sections found, fall back to original parsing
    if not restaurants:
        lines = raw_text.split('\n')
        for line in lines:
            if '|' in line and not any(skip in line.lower() for skip in ['===', 'screenshot', 'extracted']):
                # Remove numbering if present
                line = re.sub(r'^\d+\.\s*', '', line.strip())
                
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:  # Need at least name, cuisine, price
                    restaurant = {
                        'name': parts[0],
                        'cuisine': parts[1] if len(parts) > 1 else '',
                        'price': parts[2] if len(parts) > 2 else '',
                        'neighborhood': parts[3] if len(parts) > 3 else '',
                        'rating': parts[4] if len(parts) > 4 else ''
                    }
                    
                    if restaurant['name']:
                        restaurants.append(restaurant)
    
    return restaurants


def rank_restaurants(restaurants: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Rank restaurants based on user preferences
    """
    for restaurant in restaurants:
        score = 0
        
        # Dietary match (most important)
        cuisine_lower = restaurant.get('cuisine', '').lower()
        name_lower = restaurant.get('name', '').lower()
        
        for dietary in preferences.get('dietary', []):
            if dietary.lower() in cuisine_lower or dietary.lower() in name_lower:
                score += 30
        
        # Cuisine preference match
        for preferred in preferences.get('cuisines', []):
            if preferred.lower() in cuisine_lower:
                score += 20
        
        # Price range match
        price = restaurant.get('price', '')
        if price in ['$$', '$$$']:
            score += 15
        elif price == '$$$$':
            score += 5
        
        # Rating bonus
        rating_str = restaurant.get('rating', '')
        try:
            rating = float(re.search(r'(\d+\.?\d*)', rating_str).group(1))
            score += rating * 5
        except:
            pass
        
        restaurant['preference_score'] = score
    
    # Sort by score
    return sorted(restaurants, key=lambda x: x.get('preference_score', 0), reverse=True)