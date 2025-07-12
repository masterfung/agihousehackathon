"""
Fallback restaurant data for San Francisco when browser automation fails
"""

FALLBACK_RESTAURANTS = {
    "san_francisco": [
        {
            "name": "Shizen Vegan Sushi Bar",
            "cuisine": "Vegan, Sushi, Japanese",
            "price": "$$",
            "address": "Mission",
            "rating": "4.5",
            "platform": "known"
        },
        {
            "name": "Greens Restaurant", 
            "cuisine": "Vegetarian, American",
            "price": "$$$",
            "address": "Fort Mason",
            "rating": "4.3",
            "platform": "known"
        },
        {
            "name": "Loving Hut",
            "cuisine": "Vegan, Asian",
            "price": "$",
            "address": "Chinatown",
            "rating": "4.2",
            "platform": "known"
        },
        {
            "name": "The Plant Cafe Organic",
            "cuisine": "Organic, Vegetarian-Friendly",
            "price": "$$",
            "address": "Marina",
            "rating": "4.0",
            "platform": "known"
        },
        {
            "name": "Herbivore",
            "cuisine": "Vegan, American",
            "price": "$$",
            "address": "Valencia",
            "rating": "4.1",
            "platform": "known"
        },
        {
            "name": "Burma Superstar",
            "cuisine": "Burmese, Asian",
            "price": "$$",
            "address": "Clement",
            "rating": "4.4",
            "platform": "known"
        },
        {
            "name": "Thanh Long",
            "cuisine": "Vietnamese, Seafood",
            "price": "$$$",
            "address": "Sunset",
            "rating": "4.3",
            "platform": "known"
        },
        {
            "name": "Gracias Madre",
            "cuisine": "Mexican, Vegan",
            "price": "$$",
            "address": "Mission",
            "rating": "4.2",
            "platform": "known"
        }
    ]
}

def get_fallback_restaurants(city: str = "san_francisco", num: int = 5):
    """Get fallback restaurant data"""
    return FALLBACK_RESTAURANTS.get(city, [])[:num]