"""
Browser-use lifecycle hooks for restaurant data extraction
"""

import json
import os
from pathlib import Path

def on_page_load(page_url: str, screenshot_path: str = None):
    """Hook called when page loads - extract restaurant data from screenshot"""
    print(f"🔍 Page loaded: {page_url}")
    
    if screenshot_path and os.path.exists(screenshot_path):
        print(f"📸 Screenshot captured: {screenshot_path}")
        # Here we could analyze the screenshot with an LLM
        # For now, just log that we have it
        
def on_action_complete(action_type: str, screenshot_path: str = None):
    """Hook called after each action - capture scroll results"""
    print(f"✅ Action completed: {action_type}")
    
    if action_type == "scroll" and screenshot_path:
        print(f"📸 Scroll screenshot: {screenshot_path}")
        # Extract new restaurants from this view
        
def on_task_complete(final_result: str, screenshots: list = None):
    """Hook called when task completes - compile all extracted data"""
    print(f"🎯 Task completed with {len(screenshots) if screenshots else 0} screenshots")
    
    # Save extracted restaurant data
    results_file = Path("extracted_restaurants.json")
    data = {
        "result": final_result,
        "screenshots": screenshots or [],
        "timestamp": str(os.times())
    }
    
    with open(results_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Results saved to {results_file}")