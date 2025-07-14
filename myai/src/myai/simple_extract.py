"""
Simple extraction that just gets visible results and stops
"""

def create_simple_task(url: str) -> str:
    """Create a task that just extracts visible results immediately"""
    
    return f"""
Go to {url}

SIMPLE TASK:
1. Wait 3 seconds for page load
2. Look at page and extract ALL restaurants you can see right now
3. Do NOT scroll, do NOT click anything
4. Just return what's visible

Format each restaurant as:
[Name] | [Cuisine] | [Price] | [Location]

That's it - no scrolling, no waiting, just extract and return.
"""