#!/usr/bin/env python3
"""Test the query analyzer"""

from src.myai.query_analyzer import analyze_query, create_smart_browser_task
from src.myai.preferences import get_user_context

# Test queries
queries = [
    "dinner for 5 at 8pm tuesday",
    "lunch for three tomorrow",
    "italian restaurant tonight",
    "vegan brunch this weekend",
    "dinner near union square for 6"
]

context = get_user_context()

print("Testing Query Analyzer\n")
print("=" * 60)

for query in queries:
    print(f"\nQuery: '{query}'")
    params = analyze_query(query, context)
    print(f"Parsed:")
    print(f"  - Party size: {params['party_size']}")
    print(f"  - Date: {params['date_str']}")
    print(f"  - Time: {params['meal_time']}")
    print(f"  - Dietary: {params['dietary']}")
    print(f"  - Cuisines: {params['cuisines']}")
    print(f"  - Location: {params['location']}")
    
print("\n" + "=" * 60)
print("\nSmart Browser Task for OpenTable:")
print(create_smart_browser_task("opentable", "dinner for 5 at 8pm tuesday", context))