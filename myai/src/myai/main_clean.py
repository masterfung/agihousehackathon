#!/usr/bin/env python3
"""
Clean Main Interface for Restaurant AI

Usage:
    python -m myai.main_clean find "lunch for 3 next tuesday"
    python -m myai.main_clean status
    python -m myai.main_clean export-mcp
"""

import sys
import json
from typing import List

from .restaurant_ai import restaurant_ai

def main():
    """Main CLI interface"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "find":
        if len(sys.argv) < 3:
            print("❌ Please provide a query. Example: find 'lunch for 3 next tuesday' [platform]")
            print("   Platforms: opentable, resy")
            return
        
        # Parse platform if provided
        platform = "opentable"  # default
        args = sys.argv[2:]
        if args[-1].lower() in ["opentable", "resy"]:
            platform = args[-1].lower()
            args = args[:-1]
        
        query = " ".join(args).strip().strip('"').strip("'")
        
        # Use universal extractor (configurable, not hardcoded)
        from .universal_extractor import universal_extractor
        from .context_engine import default_context_engine
        
        print(f"🔍 Searching {platform.upper()} for: '{query}'")
        
        # Analyze query for context
        context = default_context_engine.analyze_request(query)
        
        # Extract restaurants using universal system
        restaurants = universal_extractor.extract_restaurants(query, platform, context)
        
        # Format results 
        if not restaurants:
            print("❌ No restaurants found")
            return
            
        print(f"\n🎯 Found {len(restaurants)} restaurants on {platform.upper()}:")
        for i, r in enumerate(restaurants, 1):
            print(f"\n{i}. **{r.name}**")
            print(f"   🍽️  {r.cuisine} • {r.price_range} • {r.location}")
            
            if r.availability_times and r.availability_times != ['Check availability']:
                times_str = ", ".join(r.availability_times[:3])
                if len(r.availability_times) > 3:
                    times_str += f" (+{len(r.availability_times)-3} more)"
                print(f"   🕐 Available: {times_str}")
            elif r.availability_times:
                print(f"   🕐 {r.availability_times[0]}")
        
        # Show summary
        with_real_times = len([r for r in restaurants if r.availability_times and r.availability_times != ['Check availability']])
        cuisines = list(set([r.cuisine for r in restaurants if r.cuisine]))
        price_ranges = list(set([r.price_range for r in restaurants if r.price_range]))
        
        print(f"\n📊 Summary:")
        print(f"   • Found {len(restaurants)} restaurants on {platform}")
        print(f"   • {with_real_times} with real availability times")
        print(f"   • Cuisines: {', '.join(cuisines)}")
        print(f"   • Price ranges: {', '.join(price_ranges)}")
        
        # Show context analysis
        print(f"\n🎯 Context Analysis:")
        print(f"   • Query: {query}")
        print(f"   • Parsed: {context.party_size} people, {context.meal_type}")
        if context.time:
            print(f"   • Time: {context.time}")
        if context.date:
            print(f"   • Date: {context.date.strftime('%A, %B %d')}")
        relevant_context = [k for k, v in context.context_relevance.items() if v > 0.1]
        if relevant_context:
            print(f"   • Used context: {', '.join(relevant_context)}")
    
    elif command == "quick":
        if len(sys.argv) < 3:
            print("❌ Please provide a query for quick search")
            return
        
        query = " ".join(sys.argv[2:]).strip().strip('"').strip("'")
        names = restaurant_ai.quick_find(query)
        
        print(f"🔍 Quick results for '{query}':")
        for i, name in enumerate(names, 1):
            print(f"   {i}. {name}")
    
    elif command == "status":
        status = restaurant_ai.get_context_status()
        
        print("📊 Restaurant AI Status:")
        print(f"   • Personal data loaded: {'✅' if status['personal_data_loaded'] else '❌'}")
        print(f"   • Context sections: {', '.join(status['context_sections'])}")
        print(f"   • Extractor ready: {'✅' if status['extractor_ready'] else '❌'}")
    
    elif command == "export-mcp":
        mcp_data = restaurant_ai.export_for_mcp()
        output_file = "mcp_export.json"
        
        with open(output_file, 'w') as f:
            json.dump(mcp_data, f, indent=2)
        
        print(f"📤 Exported MCP data to {output_file}")
    
    elif command == "test":
        # Test mode
        test_queries = [
            "lunch for 3 next tuesday", 
            "dinner for 4 wednesday",
            "breakfast for 2 tomorrow"
        ]
        
        print("🧪 Running test queries...")
        for query in test_queries:
            print(f"\n--- Testing: '{query}' ---")
            names = restaurant_ai.quick_find(query)
            print(f"Found: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")
    
    else:
        print_help()

def print_help():
    """Print help information"""
    print("""
🍽️  Restaurant AI - Clean Interface

Commands:
    find "query"     - Find restaurants with full analysis
    quick "query"    - Quick search (names only)
    status          - Show system status
    export-mcp      - Export data for MCP server
    test            - Run test queries

Examples:
    python -m myai.main_clean find "lunch for 3 next tuesday"
    python -m myai.main_clean quick "vegetarian asian dinner"
    python -m myai.main_clean status
""")

if __name__ == "__main__":
    main()