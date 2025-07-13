"""
Universal Restaurant Extractor - Configurable, Data-Driven Approach

No hardcoded values, platform configs loaded from data
"""

import subprocess
import os
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Platform configuration data (not hardcoded in logic)
PLATFORM_CONFIG = {
    "resy": {
        "base_url": "https://resy.com/cities/san-francisco-ca/search",
        "param_mapping": {
            "date": "date",           # YYYY-MM-DD
            "party_size": "seats",    # number
            "time": "time",           # HHMM (24hr)
            "cuisine": "facet"        # facet=cuisine:Value
        },
        "cuisine_mapping": {
            "asian": "Asian",
            "mexican": "Mexican", 
            "italian": "Italian",
            "thai": "Thai",
            "japanese": "Japanese",
            "chinese": "Chinese",
            "indian": "Indian",
            "fusion": "Fusion",
            "american": "American"
        },
        "default_cuisine": "Asian",
        "time_format": "HHMM",
        "date_format": "%Y-%m-%d"
    },
    "opentable": {
        "base_url": "https://www.opentable.com/s",
        "sf_specific_base": "https://www.opentable.com/region/san-francisco/san-francisco-restaurants",
        "param_mapping": {
            "date": "dateTime",       # YYYY-MM-DD HH:MM
            "party_size": "covers",   # number  
            "cuisine": "term",        # search terms
            "location": "metroId",    # metro area ID
            "latitude": "latitude",   # latitude
            "longitude": "longitude", # longitude
            "extra_params": {
                "regionIds[]": "5",  # San Francisco
                "persistRegionAndNeighborhoodIds": "true",
                "shouldUseLatLongSearch": "false",
                "showMap": "true", 
                "sortBy": "web_conversion",
                "queryUnderstandingType": "default",
                "metroId": "4"
            }
        },
        "cuisine_mapping": {
            "fusion": "fusion",
            "asian": "asian", 
            "mexican": "mexican",
            "italian": "italian", 
            "thai": "thai",
            "japanese": "japanese",
            "chinese": "chinese",
            "indian": "indian",
            "vegetarian": "vegetarian"
        },
        "location_data": {
            "san_francisco": {
                "metroId": "4",
                "latitude": "37.77725",
                "longitude": "-122.2757064"
            }
        },
        "time_format": "ISO_FULL",
        "date_format": "%Y-%m-%dT%H:%M:%S"
    }
}

@dataclass
class ExtractionResult:
    """Standardized extraction result"""
    name: str
    cuisine: str = ""
    price_range: str = ""
    location: str = ""
    availability_times: List[str] = None
    rating: str = ""
    features: List[str] = None
    raw_data: Dict = None

class UniversalExtractor:
    """Universal restaurant extractor with configurable platforms"""
    
    def __init__(self, api_key: str = None, config: Dict = None):
        self.api_key = api_key or self._load_api_key()
        self.config = config or PLATFORM_CONFIG
        self.timeout = 90  # 1.5 minute timeout
    
    def _load_api_key(self) -> str:
        """Load API key from environment"""
        if 'GOOGLE_API_KEY' in os.environ:
            return os.environ['GOOGLE_API_KEY']
        
        # Check parent .env file
        env_file = "/Users/jh/Code/exploration/agihousehackathon/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == 'GOOGLE_API_KEY':
                                return value
        
        raise ValueError("GOOGLE_API_KEY not found")
    
    def extract_restaurants(self, query: str, platform: str, context: Any) -> List[ExtractionResult]:
        """Main extraction method - platform agnostic"""
        
        if platform not in self.config:
            raise ValueError(f"Platform '{platform}' not configured")
        
        # Build URL using platform config
        url = self._build_url(platform, context)
        
        print(f"🔗 {platform.upper()} URL: {url}")
        print(f"📋 Context: {context.party_size} people, {context.meal_type}")
        
        # Create extraction prompt
        prompt = self._create_prompt(url, platform, context)
        
        # Execute extraction
        print(f"🤖 Executing browser automation...")
        raw_result = self._execute_cli(prompt)
        
        if not raw_result:
            print(f"❌ No raw results from browser")
            return []
        
        print(f"📝 Raw output length: {len(raw_result)} chars")
        
        # Parse results
        results = self._parse_results(raw_result, platform, context)
        
        print(f"✅ Extracted {len(results)} restaurants from {platform}")
        return results
    
    def _build_url(self, platform: str, context: Any) -> str:
        """Build platform URL using configuration"""
        
        platform_config = self.config[platform]
        base_url = platform_config["base_url"]
        param_mapping = platform_config["param_mapping"]
        
        params = {}
        
        # Date parameter
        if "date" in param_mapping and context.date:
            date_format = platform_config.get("date_format", "%Y-%m-%d")
            if platform_config.get("time_format") == "ISO_FULL":
                # OpenTable full ISO format with time
                # Use context.time if available, otherwise use meal_type defaults
                if context.time:
                    time_str = self._parse_time_to_24hr(context.time)
                else:
                    # Default times based on meal type
                    meal_times = {
                        'breakfast': '09:00',
                        'lunch': '12:30',
                        'dinner': '19:00'
                    }
                    time_str = meal_times.get(context.meal_type, '19:00')
                # OpenTable needs format: 2025-07-12T19:30:00
                datetime_str = context.date.strftime(f"%Y-%m-%dT{time_str}:00")
                params[param_mapping["date"]] = datetime_str
            else:
                # Simple date format for Resy
                params[param_mapping["date"]] = context.date.strftime(date_format)
        
        # Party size
        if "party_size" in param_mapping:
            params[param_mapping["party_size"]] = str(context.party_size)
        
        # Time (for platforms that separate time)
        if "time" in param_mapping and context.time and platform_config.get("time_format") == "HHMM":
            params[param_mapping["time"]] = self._parse_time_to_hhmm(context.time)
        
        # Cuisine/search terms
        if "cuisine" in param_mapping:
            # For OpenTable, use 'term' parameter with cuisines
            if platform == "opentable":
                # Check if user specified cuisine in query
                cuisine_from_query = self._extract_cuisine_from_query(context)
                if cuisine_from_query:
                    params[param_mapping["cuisine"]] = cuisine_from_query
                else:
                    # Always try to use preferred cuisines as default
                    # Get cuisines from context or preferences
                    cuisines = []
                    if hasattr(context, 'cuisine_context') and context.cuisine_context:
                        cuisines = context.cuisine_context.get('preferred_cuisines', [])
                    
                    if not cuisines:
                        # Fall back to getting preferences directly from context engine
                        from .context_engine import default_context_engine
                        all_prefs = default_context_engine.personal_data.get('cuisine_preferences', {})
                        cuisines = all_prefs.get('preferred_cuisines', [])
                    
                    if cuisines:
                        # Use the FIRST (most preferred) cuisine only
                        term = cuisines[0]
                        params[param_mapping["cuisine"]] = term
                        # Add OpenTable-specific term variants
                        params["originalTerm"] = term
                        params["intentModifiedTerm"] = term
            else:
                # For Resy, use facet parameter
                cuisine_value = self._map_cuisine(platform, context)
                if cuisine_value:
                    params[param_mapping["cuisine"]] = f"cuisine:{cuisine_value}"
        
        # Location data (for OpenTable) 
        if platform == "opentable":
            # SF coordinates
            params["latitude"] = "37.7829745"
            params["longitude"] = "-122.4182459"
            
            # Add extra params
            extra_params = platform_config.get("extra_params", {})
            params.update(extra_params)
        
        # Build query string with proper URL encoding
        from urllib.parse import urlencode
        
        query_string = urlencode(params)
        return f"{base_url}?{query_string}"
    
    def _extract_cuisine_from_query(self, context: Any) -> Optional[str]:
        """Extract cuisine type mentioned in the original query"""
        if not hasattr(context, 'original_query'):
            return None
            
        query_lower = context.original_query.lower()
        
        # Common cuisine keywords to look for
        cuisine_keywords = [
            'italian', 'mexican', 'thai', 'chinese', 'japanese', 'indian', 
            'korean', 'vietnamese', 'french', 'spanish', 'greek', 'mediterranean',
            'american', 'fusion', 'asian', 'sushi', 'pizza', 'burger', 'vegetarian'
        ]
        
        found_cuisines = []
        for cuisine in cuisine_keywords:
            if cuisine in query_lower:
                found_cuisines.append(cuisine)
        
        return ' '.join(found_cuisines) if found_cuisines else None
    
    def _map_cuisine(self, platform: str, context: Any) -> Optional[str]:
        """Map cuisine from context using platform config"""
        
        if not hasattr(context, 'cuisine_context') or not context.cuisine_context:
            # Use default
            return self.config[platform].get("default_cuisine")
        
        cuisines = context.cuisine_context.get('preferred_cuisines', [])
        if not cuisines:
            return self.config[platform].get("default_cuisine")
        
        # Map first cuisine using platform mapping
        cuisine_mapping = self.config[platform].get("cuisine_mapping", {})
        first_cuisine = cuisines[0].lower()
        
        return cuisine_mapping.get(first_cuisine, self.config[platform].get("default_cuisine"))
    
    def _parse_time_to_hhmm(self, time_str: str) -> str:
        """Parse time to HHMM format (e.g., 1830)"""
        if not time_str:
            return "1900"  # Default 7pm
        
        try:
            time_str = time_str.lower().replace(' ', '')
            if 'pm' in time_str:
                time_part = time_str.replace('pm', '')
                if ':' in time_part:
                    hour, minute = time_part.split(':')
                    hour = int(hour)
                    if hour < 12:
                        hour += 12
                    return f"{hour:02d}{minute}"
                else:
                    hour = int(time_part)
                    if hour < 12:
                        hour += 12
                    return f"{hour:02d}00"
            elif 'am' in time_str:
                time_part = time_str.replace('am', '')
                if ':' in time_part:
                    hour, minute = time_part.split(':')
                    return f"{int(hour):02d}{minute}"
                else:
                    return f"{int(time_part):02d}00"
        except:
            pass
        
        return "1900"  # Default fallback
    
    def _parse_time_to_24hr(self, time_str: str) -> str:
        """Parse time to HH:MM format (e.g., 18:30)"""
        hhmm = self._parse_time_to_hhmm(time_str)
        return f"{hhmm[:2]}:{hhmm[2:]}"
    
    def _create_prompt(self, url: str, platform: str, context: Any) -> str:
        """Create simple, effective prompt"""
        
        return f"""Go to {url}

Look for restaurant cards on the page. Scroll down once to see more.

Extract ONLY the restaurant names (nothing else). Stop after finding 5-10 restaurants.

Example output:
Farmhouse Kitchen Thai Cuisine
Burma Love Downtown
Hed Very Thai
Kin Khao
Nari

Just list restaurant names, one per line."""
    
    def _execute_cli(self, prompt: str) -> str:
        """Execute browser-use CLI"""
        
        try:
            env = os.environ.copy()
            env['GOOGLE_API_KEY'] = self.api_key
            
            # Try direct browser-use first, then with poetry
            commands = [
                ["browser-use", "--model", "gemini-2.5-flash-lite-preview-06-17", "--prompt", prompt],
                ["poetry", "run", "browser-use", "--model", "gemini-2.5-flash-lite-preview-06-17", "--prompt", prompt]
            ]
            
            for cmd in commands:
                try:
                    # Redirect stderr to devnull to avoid capturing logs
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,  # Ignore stderr logs
                        text=True,
                        env=env
                    )
                    break
                except FileNotFoundError:
                    continue
            else:
                raise Exception("browser-use command not found")
            
            try:
                # Wait for completion with timeout
                stdout, stderr = process.communicate(timeout=self.timeout)
                
                if stdout:
                    return stdout
                elif stderr and "1." in stderr:  # Check if results are in stderr
                    print(f"📝 Found results in stderr")
                    return stderr
                elif process.returncode != 0:
                    print(f"❌ CLI Error (code {process.returncode}): {stderr[:500]}")
                    return ""
                else:
                    print(f"⚠️ No output from browser-use")
                    return ""
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ CLI timed out after {self.timeout}s")
                # Kill the process and its children
                try:
                    process.terminate()
                    # Give it a moment to terminate gracefully
                    process.wait(timeout=2)
                except:
                    # Force kill if terminate didn't work
                    process.kill()
                
                # Try to get any output that was produced
                try:
                    stdout, stderr = process.communicate(timeout=5)
                    if stdout:
                        print(f"📝 Got partial output: {len(stdout)} chars")
                        return stdout
                except:
                    pass
                return ""
            finally:
                # Ensure process is terminated and cleaned up
                if process.poll() is None:
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                    except:
                        process.kill()
                
                # Close any lingering Chromium processes
                self._cleanup_chromium()
                
        except Exception as e:
            print(f"💥 CLI execution failed: {e}")
            self._cleanup_chromium()
            return ""
    
    def _cleanup_chromium(self):
        """Close any lingering Chromium browser windows"""
        try:
            # Kill Chromium processes on macOS
            import platform
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["pkill", "-f", "Chromium"], capture_output=True)
            elif platform.system() == "Linux":
                subprocess.run(["pkill", "-f", "chromium"], capture_output=True)
            # Note: On Windows, browser-use should handle cleanup
        except:
            pass  # Ignore errors in cleanup
    
    def _parse_results(self, raw_output: str, platform: str, context: Any) -> List[ExtractionResult]:
        """Parse CLI output into structured results"""
        
        results = []
        
        # First try pipe-delimited format (Restaurant | Price | Times)
        lines = raw_output.split('\n')
        for line in lines:
            line = line.strip()
            # Skip log lines and only process real restaurant data
            if ('|' in line and 
                not line.startswith('Restaurant Name') and
                not 'INFO' in line and 
                not '[cost]' in line and
                not '📥' in line and
                not 'gemini' in line):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    name = parts[0]
                    price = parts[1] if len(parts) > 1 else ''
                    times_str = parts[2] if len(parts) > 2 else ''
                    
                    # Parse times
                    availability = []
                    if times_str and times_str.lower() not in ['no times available', 'none', '']:
                        availability = [t.strip() for t in times_str.split(',') if t.strip()]
                    
                    if name and not name.startswith('[') and len(name) > 3:  # Avoid placeholder text
                        results.append(ExtractionResult(
                            name=name,
                            cuisine=self._get_context_cuisine(platform, context),
                            price_range=price,
                            location=self._get_context_location(platform, context),
                            availability_times=availability
                        ))
        
        # If no pipe format found, try structured format
        if not results:
            restaurant_blocks = re.findall(r'=== RESTAURANT ===(.+?)=== END ===', raw_output, re.DOTALL)
            for block in restaurant_blocks:
                result = self._parse_restaurant_block(block)
                if result:
                    results.append(result)
        
        # Last resort: simple parsing
        if not results:
            results = self._parse_simple_format(raw_output, platform, context)
        
        return results
    
    def _parse_restaurant_block(self, block: str) -> Optional[ExtractionResult]:
        """Parse structured restaurant block"""
        
        data = {}
        for line in block.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if value and value != 'N/A':
                    data[key] = value
        
        if 'name' not in data:
            return None
        
        # Parse availability times - handle both 'times' and 'available times'
        availability = []
        times_key = 'times' if 'times' in data else 'available times' if 'available times' in data else None
        
        if times_key and data[times_key]:
            times_str = data[times_key]
            # Check for "No times available" or similar
            if 'no times' in times_str.lower() or 'not available' in times_str.lower():
                availability = []
            elif '[' in times_str and ']' in times_str:
                # Parse list format [12:15 PM, 12:30 PM, ...]
                times_content = times_str.split('[')[1].split(']')[0]
                availability = [t.strip() for t in times_content.split(',') if t.strip() and 'PM' in t.upper() or 'AM' in t.upper()]
            else:
                # Single time or comma-separated times
                if ',' in times_str:
                    availability = [t.strip() for t in times_str.split(',') if t.strip()]
                else:
                    availability = [times_str.strip()] if times_str.strip() else []
        
        return ExtractionResult(
            name=data.get('name', ''),
            cuisine=data.get('cuisine', ''),
            price_range=data.get('price', '$$'),
            location=data.get('location', ''),
            availability_times=availability if availability else [],
            raw_data=data
        )
    
    def _parse_simple_format(self, raw_output: str, platform: str, context: Any) -> List[ExtractionResult]:
        """Fallback simple parsing using context preferences"""
        
        results = []
        lines = raw_output.split('\n')
        
        # Get context-based defaults
        default_cuisine = self._get_context_cuisine(platform, context)
        default_location = self._get_context_location(platform, context)
        default_price = self._get_context_price(platform, context)
        
        for line in lines:
            line = line.strip()
            # Skip empty lines, URLs, logging output, and common non-restaurant text
            if (not line or 
                line.startswith('http') or 
                line.startswith('(') or 
                line.startswith('INFO') or
                line.startswith('DEBUG') or
                line.startswith('ERROR') or
                line.startswith('WARNING') or
                line.startswith('Look for') or
                line.startswith('Extract') or
                line.startswith('Just list') or
                line.startswith('The user') or
                line.startswith('The agent') or
                '[cost]' in line or
                '[browser_use' in line or
                'gemini' in line.lower() or
                'scroll' in line.lower() or
                'extract' in line.lower() or
                '📥' in line or '📤' in line or '💾' in line or '🧠' in line or
                line.lower() in ['restaurant name', 'price', 'available times', 'example output:']):
                continue
                
            # Check for numbered list format
            if re.match(r'^\d+\.', line):
                # Extract restaurant name from numbered list
                name = re.sub(r'^\d+\.\s*', '', line)
            else:
                # Just use the line as the name if it looks like a restaurant
                name = line
            
            # Basic filtering to avoid non-restaurant lines
            if (name and 
                len(name) > 3 and 
                len(name) < 100 and  # Restaurant names shouldn't be super long
                not name.startswith('[') and 
                not '|' in name and
                not name.startswith('gemini') and
                not name.startswith('INFO') and
                'cost' not in name.lower() and
                'restaurant' not in name.lower() and  # Avoid instructions
                'extract' not in name.lower() and
                'scroll' not in name.lower() and
                'user wants' not in name.lower() and
                'agent has' not in name.lower()):
                # Check if it looks like a restaurant name (has capital letters, not all lowercase)
                if any(c.isupper() for c in name) and not name.isupper():
                    # Final check: does it look like an actual restaurant name?
                    word_count = len(name.split())
                    if 1 <= word_count <= 6:  # Restaurant names are usually 1-6 words
                        results.append(ExtractionResult(
                            name=name,
                            cuisine=default_cuisine,
                            price_range=default_price or "$$",
                            location=default_location or "San Francisco",
                            availability_times=[]
                        ))
        
        return results
    
    def _get_context_cuisine(self, platform: str, context: Any) -> str:
        """Get cuisine from context or platform config"""
        if hasattr(context, 'cuisine_context') and context.cuisine_context:
            cuisines = context.cuisine_context.get('preferred_cuisines', [])
            if cuisines:
                # Map first cuisine using platform mapping
                cuisine_mapping = self.config[platform].get("cuisine_mapping", {})
                first_cuisine = cuisines[0].lower()
                return cuisine_mapping.get(first_cuisine, cuisines[0].capitalize())
        
        # Return empty string instead of hardcoded default
        return ""
    
    def _get_context_location(self, platform: str, context: Any) -> str:
        """Get location from context or platform config"""
        if hasattr(context, 'location_context') and context.location_context:
            neighborhoods = context.location_context.get('preferred_neighborhoods', [])
            if neighborhoods:
                return neighborhoods[0].replace('_', ' ').title()
        
        # Return empty string instead of hardcoded default
        return ""
    
    def _get_context_price(self, platform: str, context: Any) -> str:
        """Get price range from context or platform config"""
        if hasattr(context, 'budget_context') and context.budget_context:
            price_range = context.budget_context.get('preferred_price_range', '')
            if price_range:
                # Convert formats like "$$_to_$$$" to "$$"
                if '_to_' in price_range:
                    return price_range.split('_to_')[0]
                return price_range
        
        # Return empty string instead of hardcoded default
        return ""

# Global instance
universal_extractor = UniversalExtractor()

def extract_restaurants(query: str, platform: str, context: Any) -> List[ExtractionResult]:
    """Convenience function"""
    return universal_extractor.extract_restaurants(query, platform, context)