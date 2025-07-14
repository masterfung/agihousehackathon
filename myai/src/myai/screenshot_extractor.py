"""
Simple screenshot-based extraction
"""

def create_screenshot_task(url: str) -> str:
    """Create a task that just takes a screenshot and extracts data"""
    
    return f"""
1. Navigate to: {url}
2. Wait 3 seconds for page to load
3. Take a screenshot
4. Look at the screenshot and find all restaurant listings visible
5. For each restaurant you can see, extract:
   - Name
   - Cuisine/Food type
   - Price ($ symbols)
   - Location/Neighborhood

Format each as: [Name] | [Cuisine] | [Price] | [Location]

If you see less than 5 restaurants, scroll down and repeat.

Return the first 5 restaurants.
"""