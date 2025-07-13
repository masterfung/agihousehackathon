"""
Simplified browser task generator
"""

def create_simple_extraction_task(url: str) -> str:
    """Create a very simple extraction task that actually works"""
    
    return f"""
1. Navigate to {url}
2. Wait 3 seconds for page to load
3. Take a screenshot
4. Look at the screenshot and identify restaurant cards/listings
5. For each restaurant visible, read:
   - The restaurant name (usually the biggest text in each card)
   - The cuisine type (usually smaller text below the name)  
   - The price level (shown as $ symbols)
   - The neighborhood/area (location text)
6. Format your findings as:
   Restaurant 1: [Name] | [Cuisine] | [Price] | [Area]
   Restaurant 2: [Name] | [Cuisine] | [Price] | [Area]
   ... (up to 5 restaurants)
7. Return ONLY the formatted list, nothing else.

Do NOT scroll. Just extract what's visible in the first view.
"""