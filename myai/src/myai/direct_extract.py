"""
Direct extraction without browser automation - fastest approach
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re

def extract_direct(url: str) -> List[Dict[str, Any]]:
    """
    Direct HTTP extraction - fastest method
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        restaurants = []
        
        # Look for OpenTable restaurant cards
        restaurant_cards = soup.find_all(['div', 'article'], class_=re.compile(r'restaurant|listing|card'))
        
        for card in restaurant_cards[:10]:  # Limit to first 10
            name = None
            cuisine = None
            price = None
            location = None
            
            # Extract name
            name_elem = card.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'name|title'))
            if name_elem:
                name = name_elem.get_text(strip=True)
            
            # Extract cuisine
            cuisine_elem = card.find(text=re.compile(r'Asian|Mexican|Italian|American|Cuisine'))
            if cuisine_elem:
                cuisine = cuisine_elem.strip()
            
            # Extract price
            price_elem = card.find(text=re.compile(r'\$+'))
            if price_elem:
                price = re.search(r'\$+', price_elem).group()
            
            # Extract location
            location_elem = card.find(text=re.compile(r'San Francisco|SF|Castro|Mission|SOMA'))
            if location_elem:
                location = location_elem.strip()
            
            if name:
                restaurants.append({
                    'name': name,
                    'cuisine': cuisine or 'Various',
                    'price': price or '$$',
                    'address': location or 'San Francisco'
                })
        
        return restaurants
        
    except Exception as e:
        print(f"Direct extraction failed: {e}")
        return []


def fallback_restaurants() -> List[Dict[str, Any]]:
    """
    Fallback vegetarian Asian restaurants in SF for demonstration
    """
    return [
        {
            'name': 'Greens Restaurant',
            'cuisine': 'Vegetarian Fine Dining',
            'price': '$$$',
            'address': 'Marina District'
        },
        {
            'name': 'Loving Hut',
            'cuisine': 'Asian Vegetarian',
            'price': '$$',
            'address': 'Chinatown'
        },
        {
            'name': 'Shizen',
            'cuisine': 'Vegan Sushi',
            'price': '$$$',
            'address': 'Mission District'
        },
        {
            'name': 'Buddha\'s Kitchen',
            'cuisine': 'Asian Fusion',
            'price': '$$',
            'address': 'Castro'
        }
    ]