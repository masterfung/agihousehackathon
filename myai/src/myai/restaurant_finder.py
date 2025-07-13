"""
Restaurant finder module using browser automation
Searches restaurants on various platforms and extracts information
"""

import asyncio
import re
import os
from typing import List, Dict, Any, Optional
from browser_use import Agent, BrowserContext
from browser_use.llm import ChatGoogle
try:
    from .preferences import UserContext, format_preferences_for_prompt
    from .evaluator import RestaurantInfo, RestaurantEvaluator, EvaluationScore
    from .site_optimizations import create_optimized_task
    from .fallback_data import get_fallback_restaurants
    from .simple_search import parse_raw_results
except ImportError:
    from preferences import UserContext, format_preferences_for_prompt
    from evaluator import RestaurantInfo, RestaurantEvaluator, EvaluationScore
    from site_optimizations import create_optimized_task
    from fallback_data import get_fallback_restaurants
    from simple_search import parse_raw_results


class RestaurantFinder:
    """Finds and evaluates restaurants using browser automation"""
    
    def __init__(self, user_context: UserContext, llm: ChatGoogle):
        self.context = user_context
        self.llm = llm
        self.evaluator = RestaurantEvaluator(user_context)
        
    async def find_restaurants(self, 
                             query: str = "dinner tonight",
                             platforms: List[str] = None,
                             num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find restaurants matching user preferences across multiple platforms
        
        Args:
            query: The search query (e.g., "dinner tonight", "lunch tomorrow")
            platforms: List of platforms to search (defaults to all)
            num_results: How many total restaurants to return
            
        Returns:
            List of top restaurants with scores from all platforms
        """
        if platforms is None:
            platforms = ["opentable", "resy", "yelp", "google"]
        
        # Create optimized tasks for all platforms
        tasks = []
        for platform in platforms:
            platform_lower = platform.lower()
            if platform_lower in ["opentable", "resy", "yelp", "google"]:
                # Use optimized platform-specific task with query
                task_desc = create_optimized_task(platform_lower, self.context, query)
                tasks.append(self._search_platform(platform, task_desc))
            else:
                print(f"Skipping unsupported platform: {platform}")
                continue
        
        # Run all searches in parallel
        print(f"🔄 Searching {len(tasks)} platforms in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all results
        all_restaurants = []
        for platform_results in results:
            if isinstance(platform_results, Exception):
                print(f"Error from platform: {platform_results}")
                continue
            all_restaurants.extend(platform_results)
        
        # If no results from any platform, use fallback data
        if not all_restaurants:
            print("\n⚠️  No results from web search.")
            
            # Use fallback data so user gets something
            print("📚 Using known vegetarian restaurants in San Francisco...")
            fallback_data = get_fallback_restaurants("san_francisco", num_results)
            
            for restaurant_data in fallback_data:
                restaurant_info = self._create_restaurant_info(restaurant_data, "fallback")
                score = self.evaluator.evaluate_restaurant(restaurant_info)
                
                all_restaurants.append({
                    "restaurant": restaurant_info,
                    "score": score,
                    "platform": "known"
                })
            
            print("\n💡 Tips for better results:")
            print("  - Try a single platform: poetry run python src/myai/main.py find 'dinner' yelp")
            print("  - Debug mode: BROWSER_HEADLESS=false python test_single_platform.py google")
            print("  - Check the troubleshooting section in README.md")
        
        # Sort by score and return top N
        all_restaurants.sort(key=lambda x: x["score"].total_score, reverse=True)
        return all_restaurants[:num_results]
    
    async def _search_platform(self, platform: str, task: str) -> List[Dict[str, Any]]:
        """Search a single platform and return evaluated restaurants"""
        try:
            # Create agent for this platform with correct settings
            agent = Agent(
                task=task,
                llm=self.llm,
                browser_config={
                    "headless": os.environ.get('BROWSER_HEADLESS', 'true').lower() == 'true',
                    "disable_security": True,  # Faster loading
                },
                max_actions_per_step=10,  # Allow more actions for scrolling
            )
            
            # Execute the search with timeout
            print(f"  🔍 Searching {platform}...")
            
            # Run with asyncio timeout - give it more time
            try:
                result = await asyncio.wait_for(agent.run(), timeout=45.0)  # 45 seconds
            except asyncio.TimeoutError:
                print(f"  ⏱️  {platform} search timed out after 45 seconds")
                return []
            except Exception as e:
                print(f"  ❌ Error on {platform}: {str(e)}")
                return []
            
            # Convert result to string if needed
            if hasattr(result, '__str__'):
                result_str = str(result)
            else:
                result_str = result
            
            # Debug: Show first 200 chars of result
            print(f"  📄 Raw result preview: {result_str[:200]}...")
            
            # Parse the results
            restaurants = self._parse_search_results(result_str, platform)
            print(f"  🔍 Parsed {len(restaurants)} raw restaurants from {platform}")
            
            # Evaluate each restaurant
            evaluated_restaurants = []
            for restaurant_data in restaurants[:5]:  # Limit per platform
                restaurant_info = self._create_restaurant_info(restaurant_data, platform)
                score = self.evaluator.evaluate_restaurant(restaurant_info)
                
                evaluated_restaurants.append({
                    "restaurant": restaurant_info,
                    "score": score,
                    "platform": platform
                })
            
            print(f"  ✅ Found {len(evaluated_restaurants)} restaurants on {platform}")
            return evaluated_restaurants
            
        except Exception as e:
            print(f"  ❌ Error on {platform}: {str(e)[:100]}")
            return []
    
    
    def _parse_search_results(self, result: str, platform: str) -> List[Dict[str, Any]]:
        """Parse the agent's results into structured data"""
        restaurants = []
        
        # Check if this looks like raw extracted text (no formatting)
        if result and '|' not in result and len(result) > 200:
            # Use simple parser for raw text
            print(f"  📝 Parsing raw text from {platform}...")
            return parse_raw_results(result, platform)
        
        # Look for pipe-delimited format first (our new format)
        lines = result.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or not '|' in line:
                continue
                
            # Remove numbering
            line = re.sub(r'^\d+\.\s*', '', line)
            
            # Parse pipe-delimited data
            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) >= 3:  # Need at least name, cuisine, and one more field
                restaurant = {
                    'name': parts[0],
                    'cuisine': parts[1]
                }
                
                # Platform-specific parsing
                if platform == "opentable" and len(parts) >= 4:
                    restaurant['price'] = parts[2]
                    restaurant['address'] = parts[3]
                elif platform == "yelp" and len(parts) >= 5:
                    restaurant['cuisine'] = parts[1]  # Categories
                    restaurant['rating'] = parts[2]
                    restaurant['price'] = parts[3]
                    restaurant['address'] = parts[4]
                elif platform == "google" and len(parts) >= 4:
                    restaurant['rating'] = parts[1]
                    restaurant['price'] = parts[2] if parts[2] != 'N/A' else '$$'
                    restaurant['address'] = parts[3]
                elif platform == "resy" and len(parts) >= 3:
                    restaurant['address'] = parts[2]
                    if len(parts) >= 4:
                        restaurant['price'] = parts[3]
                
                if restaurant.get('name'):
                    restaurants.append(restaurant)
        
        # If no pipe format found, try the old parsing method
        if not restaurants:
            # Fallback to key-value parsing
            blocks = re.split(r'\n(?=\d+\.)', result)
            
            for block in blocks:
                if not block.strip():
                    continue
                    
                lines = block.strip().split('\n')
                current_restaurant = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Remove list numbers
                    line = re.sub(r'^\d+\.\s*', '', line)
                    
                    # Parse key-value pairs
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        # Simple key mapping
                        if 'name' in key:
                            current_restaurant['name'] = value
                        elif 'cuisine' in key or 'type' in key or 'categor' in key:
                            current_restaurant['cuisine'] = value
                        elif 'price' in key:
                            current_restaurant['price'] = value
                        elif 'address' in key or 'neighborhood' in key or 'location' in key:
                            current_restaurant['address'] = value
                        elif 'rating' in key or 'star' in key:
                            current_restaurant['rating'] = value
                
                if current_restaurant.get('name'):
                    restaurants.append(current_restaurant)
        
        return restaurants[:5]  # Limit to 5 per platform
    
    def _create_restaurant_info(self, data: Dict[str, Any], platform: str) -> RestaurantInfo:
        """Convert parsed data into RestaurantInfo object with platform-aware defaults"""
        # Extract cuisine types
        cuisine_str = data.get('cuisine', '')
        cuisines = [c.strip() for c in cuisine_str.split(',') if c.strip()]
        
        # Default values based on the fact we filtered for vegetarian-friendly places
        has_vegetarian = True  # We searched for vegetarian restaurants
        veg_count = 5  # Assume decent selection since they came up in vegetarian search
        
        # Check for specific vegetarian indicators
        if 'vegetarian_options' in data:
            veg_text = data['vegetarian_options'].lower()
            if any(word in veg_text for word in ['vegan', 'plant-based', 'vegetarian']):
                veg_count = 8  # Likely dedicated vegetarian place
            elif 'friendly' in veg_text:
                veg_count = 5
        
        # Platform-specific defaults for wine
        wine_quality = 'good' if platform in ['opentable', 'resy'] else 'basic'
        allows_corkage = None  # Unknown by default
        
        # SF restaurants near 94109 are generally transit accessible
        near_transit = True  # Default for SF location
        
        # Parse rating if present
        rating = None
        if 'rating' in data:
            rating_match = re.search(r'(\d+\.?\d*)', data['rating'])
            if rating_match:
                rating = float(rating_match.group(1))
        
        # Calculate approximate distance based on neighborhood
        distance = None
        address = data.get('address', '')
        if address:
            # Common SF neighborhoods and approximate distances from 94109
            neighborhood_distances = {
                'nob hill': 0.5,
                'tenderloin': 0.3,
                'union square': 0.8,
                'mission': 2.5,
                'castro': 2.0,
                'hayes valley': 1.5,
                'soma': 1.5,
                'financial district': 1.2
            }
            
            address_lower = address.lower()
            for neighborhood, dist in neighborhood_distances.items():
                if neighborhood in address_lower:
                    distance = dist
                    break
        
        return RestaurantInfo(
            name=data.get('name', 'Unknown Restaurant'),
            cuisine_type=cuisines if cuisines else ['Vegetarian'],
            price_range=data.get('price', '$$'),
            address=address,
            distance_miles=distance,
            has_vegetarian_menu=has_vegetarian,
            vegetarian_options_count=veg_count,
            wine_list_quality=wine_quality,
            allows_corkage=allows_corkage,
            near_public_transit=near_transit,
            rating=rating,
            url=''  # We're not clicking into restaurants anymore
        )
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format the results for display"""
        if not results:
            return "No restaurants found matching your preferences."
        
        output = []
        output.append(f"🎯 Top {len(results)} restaurants from all platforms:\n")
        
        for i, result in enumerate(results, 1):
            restaurant = result['restaurant']
            score = result['score']
            platform = result.get('platform', 'Unknown')
            
            output.append(f"{i}. {restaurant.name} ({platform.upper()})")
            output.append(f"   Score: {score.total_score}/100 - {self._get_score_emoji(score.total_score)}")
            output.append(f"   Cuisine: {', '.join(restaurant.cuisine_type)}")
            output.append(f"   Price Range: {restaurant.price_range}")
            output.append(f"   Address: {restaurant.address}")
            
            if restaurant.distance_miles:
                output.append(f"   Distance: {restaurant.distance_miles} miles")
            
            output.append(f"\n   {score.explanation}")
            
            if restaurant.url:
                output.append(f"   Link: {restaurant.url}")
            
            output.append("")  # Empty line between restaurants
        
        return "\n".join(output)
    
    def _get_score_emoji(self, score: float) -> str:
        """Get emoji representation of score"""
        if score >= 85:
            return "🌟 Excellent Match!"
        elif score >= 70:
            return "✨ Good Match"
        elif score >= 50:
            return "👍 Decent Option"
        else:
            return "🤔 Consider Alternatives"