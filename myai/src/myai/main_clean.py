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
            print("❌ Please provide a query. Example: find 'lunch for 3 next tuesday'")
            return
        
        query = " ".join(sys.argv[2:]).strip().strip('"').strip("'")
        results = restaurant_ai.find_restaurants(query)
        
        # Also show summary
        summary = results['summary']
        print(f"\n📊 Summary:")
        print(f"   • Found {summary['total_restaurants']} restaurants")
        print(f"   • {summary['with_availability']} with availability times")
        print(f"   • Cuisines: {', '.join(summary['cuisines_found'])}")
        print(f"   • Price ranges: {', '.join(summary['price_ranges'])}")
    
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