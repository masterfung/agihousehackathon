"""
Smart termination logic for browser extraction
"""

def create_terminating_task(url: str, query_params: dict) -> str:
    """
    Create a task that terminates when no more results are found
    """
    
    return f"""
Navigate to: {url}

SMART EXTRACTION WITH TERMINATION:

1. Wait 3 seconds for page load
2. Extract ALL visible restaurants on current view
3. Count how many restaurants you found
4. If you found restaurants, scroll down ONCE
5. Extract any NEW restaurants (don't repeat previous ones)
6. If NO new restaurants appear after scrolling, STOP immediately
7. If you see "No more results" or similar message, STOP immediately
8. Maximum 2 scrolls then STOP regardless

Return format:
RESTAURANTS FOUND: [count]
1. [Name] | [Cuisine] | [Price] | [Location]
2. [Name] | [Cuisine] | [Price] | [Location]
...

EXTRACTION COMPLETE - Found [final count] restaurants for {query_params['party_size']} people.

IMPORTANT: If page has reached the end or no new results, say "END OF RESULTS" and stop.
"""