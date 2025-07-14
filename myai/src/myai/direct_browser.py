"""
Direct browser approach for extracting restaurant data
"""

import asyncio
from browser_use import Agent
from browser_use.browser.service import BrowserService
from typing import List, Dict, Any


async def extract_restaurants_directly(url: str, llm) -> List[Dict[str, Any]]:
    """Extract restaurants using direct browser commands"""
    
    # Create browser service
    browser = BrowserService()
    await browser.start()
    
    try:
        # Navigate to URL
        page = await browser.get_page()
        await page.goto(url)
        
        # Wait for content to load
        await page.wait_for_timeout(3000)
        
        # Extract all text content from restaurant cards
        restaurants = []
        
        # Try to find restaurant cards using common selectors
        selectors = [
            '[data-testid*="restaurant"]',
            '.restaurant-card',
            '[class*="RestaurantCard"]',
            '[class*="restaurant-item"]',
            'article',
            '[role="article"]'
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    for i, element in enumerate(elements[:10]):  # Get up to 10
                        try:
                            text = await element.inner_text()
                            if text and len(text) > 20:  # Filter out empty/small elements
                                restaurants.append({
                                    'raw_text': text,
                                    'index': i
                                })
                        except:
                            continue
                    if restaurants:
                        break
            except:
                continue
        
        # If no cards found, get all visible text
        if not restaurants:
            content = await page.content()
            # Simple extraction - just get the page text
            text_content = await page.inner_text('body')
            restaurants.append({'raw_text': text_content, 'index': 0})
        
        return restaurants
        
    finally:
        await browser.stop()


async def smart_extract(url: str, llm) -> str:
    """Use browser-use Agent with smart extraction"""
    
    task = f"""
Navigate to: {url}

Your goal: Extract restaurant information.

1. After the page loads, use extract_structured_data to get ALL restaurant names visible
2. If you see less than 5 restaurants, scroll down ONCE 
3. Then extract ALL restaurant data again
4. Format each as: [Name] | [Type] | [Price] | [Area]

Return the formatted list of restaurants.
"""
    
    agent = Agent(
        task=task,
        llm=llm,
        browser_config={
            "headless": True,
            "disable_security": True,
        },
        max_actions_per_step=10,
    )
    
    try:
        result = await asyncio.wait_for(agent.run(), timeout=45.0)
        return str(result)
    except asyncio.TimeoutError:
        return "Timeout"