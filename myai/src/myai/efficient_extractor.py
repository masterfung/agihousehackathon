"""
Efficient restaurant extraction that stops when no more results
"""

def create_efficient_extraction_task(url: str, query_params: dict) -> str:
    """
    Create a task that efficiently extracts all visible results and stops
    """
    
    return f"""
Go to: {url}

EFFICIENT EXTRACTION - Stop when done:

1. Wait 2 seconds for page load
2. Look at current page and extract ALL visible restaurants:
   - Restaurant name
   - Cuisine type  
   - Price range
   - Neighborhood
   
3. Check if there are more results:
   - Look for "Load more" button
   - Look for pagination (next page)
   - Check if page can scroll down more
   
4. If no more results available, STOP and return what you found
5. If more results exist, scroll ONCE and extract new ones
6. Repeat step 3-5 maximum 2 times (total 3 screens)

IMPORTANT:
- If you see "No more results" or reach end of page, STOP immediately
- If you see the same restaurants repeated, STOP
- Maximum 3 scroll attempts then STOP
- Focus on vegetarian/asian restaurants

Return format:
RESTAURANTS FOUND:
1. [Name] | [Cuisine] | [Price] | [Location]
2. [Name] | [Cuisine] | [Price] | [Location]
...

EXTRACTION COMPLETE - Found X restaurants for {query_params['party_size']} people on {query_params['date_str']} at {query_params['meal_time']}.
"""


def create_quick_snapshot_task(url: str, query_params: dict) -> str:
    """
    Create a task that just takes a quick snapshot of results
    """
    
    return f"""
Navigate to: {url}

QUICK SNAPSHOT:
1. Wait 3 seconds for load
2. Extract what's visible right now
3. Do NOT scroll - just get current results
4. Return immediately

Looking for {query_params['party_size']} people, {query_params['date_str']} {query_params['meal_time']}

Return visible restaurants in format:
[Name] | [Cuisine] | [Price] | [Location]

That's it - no scrolling, just current results.
"""