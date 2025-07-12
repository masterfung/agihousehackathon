"""
Date parsing utilities for restaurant searches
"""

from datetime import datetime, timedelta
import re


def parse_party_size(query: str) -> int:
    """Extract party size from query"""
    query_lower = query.lower()
    
    # Look for explicit numbers
    patterns = [
        r'for (\d+) people',
        r'for (\d+) person',
        r'party of (\d+)',
        r'table for (\d+)',
        r'(\d+) people',
        r'(\d+) person',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return int(match.group(1))
    
    # Look for word numbers
    word_to_num = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8
    }
    
    for word, num in word_to_num.items():
        if word in query_lower:
            return num
    
    # Default to 2 people
    return 2


def parse_date_query(query: str) -> tuple[datetime, str]:
    """
    Parse natural language date from query
    Returns: (date_object, formatted_date_string)
    """
    today = datetime.now()
    query_lower = query.lower()
    
    # Check for specific date patterns
    if "tonight" in query_lower or "today" in query_lower:
        date = today
        date_str = "Today"
    elif "tomorrow" in query_lower:
        date = today + timedelta(days=1)
        date_str = "Tomorrow"
    elif "day after tomorrow" in query_lower:
        date = today + timedelta(days=2)
        date_str = date.strftime("%A, %B %d")
    elif "this weekend" in query_lower:
        # Get next Saturday
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        date = today + timedelta(days=days_until_saturday)
        date_str = date.strftime("%A, %B %d")
    elif "next week" in query_lower:
        date = today + timedelta(days=7)
        date_str = date.strftime("%A, %B %d")
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
                date = today + timedelta(days=days_ahead)
                date_str = date.strftime("%A, %B %d")
                break
        else:
            # Default to today
            date = today
            date_str = "Today"
    
    return date, date_str


def get_meal_time(query: str) -> str:
    """Extract meal time from query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["breakfast", "brunch"]):
        return "10:00 AM"
    elif any(word in query_lower for word in ["lunch"]):
        return "12:30 PM"
    elif any(word in query_lower for word in ["dinner", "tonight"]):
        return "7:00 PM"
    else:
        return "7:00 PM"  # Default to dinner