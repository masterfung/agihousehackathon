# MyAI - Personal Context-Driven Restaurant Finder

A composable, intelligent restaurant discovery system using browser automation and personal preferences to find restaurants on OpenTable, Resy, and other platforms.

## Overview

MyAI uses a centralized context engine to understand your personal dining preferences and intelligently search restaurant platforms. It features a clean CLI interface, real-time availability extraction, and MCP server compatibility for dynamic preference management.

## Key Features

- 🎯 **Centralized Context Engine**: Docstring-style personal preferences with intelligent prompt analysis
- 🍽️ **Multi-Platform Support**: OpenTable, Resy with platform-specific optimizations
- ⚡ **Fast CLI Extraction**: Direct browser-use CLI calls for reliable results
- 📅 **Smart Date/Time Parsing**: "next wednesday", "6:30PM", party size detection
- 🔗 **Optimized URLs**: Direct search URLs with proper parameters (e.g., `facet=cuisine:Asian` for Resy)
- 🤖 **MCP Server Ready**: Composable architecture for Model Context Protocol integration
- 🎨 **Simple Interface**: Clean command-line interface with platform selection

## Personal Preferences (Editable)

Your preferences are stored in `src/myai/context_engine.py` in a docstring format:

```python
## Dietary Requirements
- vegetarian: true
- allergies: ["peanut", "shrimp"]
- spice_tolerance: "mild"

## Cuisine Preferences  
- preferred_cuisines: ["fusion", "asian", "mexican"]
- favorite_types: ["thai", "vietnamese", "indian"]

## Budget & Pricing
- min_price_per_dish: 10.0
- max_price_per_dish: 30.0
- comfortable_total_per_person: 40.0

## Location & Transit
- home_zip: "94109"
- prefers_public_transit: true
```

## Installation

```bash
# Install dependencies
poetry install

# Set up API key (required)
export GOOGLE_API_KEY="your-gemini-api-key"
# OR add to .env file in parent directory
```

## Usage

### Basic Commands

```bash
# Search Resy for dinner
PYTHONPATH=src poetry run python -m myai.main_clean find "next wednesday for 3 people dinner at 7:15PM" resy

# Search OpenTable  
PYTHONPATH=src poetry run python -m myai.main_clean find "lunch for 2 tomorrow" opentable

# Quick search (names only)
PYTHONPATH=src poetry run python -m myai.main_clean quick "vegetarian asian dinner"

# Check system status
PYTHONPATH=src poetry run python -m myai.main_clean status

# Export data for MCP server
PYTHONPATH=src poetry run python -m myai.main_clean export-mcp
```

### Query Examples

```bash
# Natural language queries work
"lunch for 3 next tuesday"
"dinner for 4 wednesday at 6:30PM"  
"breakfast for 2 tomorrow"
"next friday dinner for 5"
```

### Platform-Specific Features

**Resy:**
- Uses `facet=cuisine:Asian` filtering
- Extracts availability times
- Optimized for fusion/asian cuisine

**OpenTable:**
- Direct search with party size and date/time
- Vegetarian filtering
- Transit-accessible locations

## How It Works

### Architecture

1. **Context Engine** (`context_engine.py`): Parses personal preferences and analyzes queries
2. **Universal Extractor** (`universal_extractor.py`): Configuration-driven platform extraction with no hardcoded values
3. **Simple Prompts**: Uses minimal prompts for reliable browser-use CLI execution
4. **Real-time Results**: Extracts actual restaurant names, availability, and details

### URL Generation Examples

**Resy:**
```
https://resy.com/cities/san-francisco-ca/search?date=2025-07-16&seats=3&time=1830&facet=cuisine:Asian
```

**OpenTable:**
```
https://www.opentable.com/s?covers=3&dateTime=2025-07-16T18:30&metroId=4&term=vegetarian+asian&prices=2,3
```

### Context Analysis

The system intelligently determines what personal context is relevant:

```python
# Query: "vegetarian asian dinner for 4"
Relevance: {
  'dietary': 0.8,    # High - "vegetarian" detected
  'cuisine': 0.9,    # High - "asian" detected  
  'timing': 0.6,     # Medium - "dinner" detected
  'location': 0.0,   # Low - no location keywords
  'budget': 0.0      # Low - no budget keywords
}
```

## Recent Restaurant Results

**Resy (Asian, Wednesday 6:30PM, 3 people):**
- Good Good Culture Club
- Liholiho Yacht Club  
- E&O Kitchen and Bar
- Piglet & Co

**OpenTable (Vegetarian Asian):**
- New Delhi Restaurant
- Osha Thai Embarcadero
- Burma Love
- Roti Indian Bistro

## Performance Optimizations

### Simple Prompts Work Best
❌ **Complex prompts cause timeouts:**
```
"Go to URL. TASK: Extract restaurant information with availability times from RESY. 
RESY-SPECIFIC INSTRUCTIONS: Look for restaurant cards with names and time slots..."
```

✅ **Simple prompts work reliably:**
```
"Go to URL and extract restaurant names you see. List them as:
1. Restaurant Name
2. Restaurant Name"
```

### Direct CLI Approach
- Uses `browser-use` CLI directly with subprocess
- 60-90 second timeout per platform
- Minimal wrapper overhead
- Real-time restaurant extraction

## MCP Server Integration

The system is designed for MCP server compatibility:

```python
# Export current context
restaurant_ai.export_for_mcp()

# Load from MCP server
restaurant_ai.update_from_mcp(mcp_data)

# Check MCP compatibility
restaurant_ai.get_context_status()
```

## Example Output

```
🔍 Searching RESY for: 'next wednesday for 3 people dinner at 6:30PM'
🔗 Enhanced URL: https://resy.com/cities/san-francisco-ca/search?date=2025-07-16&seats=3&time=1830&facet=cuisine:Asian
📋 Context: 3 people, dinner
✅ Extracted 4 restaurants with availability

🎯 Found 4 restaurants on RESY:

1. **Good Good Culture Club**
   🍽️  Asian • $$ • San Francisco
   🕐 Available: Check availability

2. **Liholiho Yacht Club**  
   🍽️  Asian • $$ • San Francisco
   🕐 Available: Check availability

📊 Summary:
   • Found 4 restaurants on resy
   • 0 with availability times  
   • Cuisines: Asian
   • Price ranges: $$
```

## File Structure

```
src/myai/
├── context_engine.py          # Personal preferences & query analysis
├── universal_extractor.py     # Configuration-driven platform extraction
├── restaurant_ai.py           # Main composable interface
├── main_clean.py             # CLI interface
├── date_parser.py            # Date/time parsing utilities
└── preferences.py            # Legacy preference system
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're using `PYTHONPATH=src`
2. **API Key Error**: Set `GOOGLE_API_KEY` environment variable
3. **Timeouts**: Complex prompts cause issues - system uses simple prompts
4. **No Results**: Check if the generated URL is correct

### Debug Commands

```bash
# Test URL generation
PYTHONPATH=src python -c "from myai.universal_extractor import universal_extractor; print('URL building test')"

# Test direct CLI
GOOGLE_API_KEY=your-key poetry run browser-use --model gemini-2.5-flash-lite-preview-06-17 --prompt "Go to resy.com and list restaurants"

# Check system status  
PYTHONPATH=src poetry run python -m myai.main_clean status
```

## Contributing

The system is designed to be composable and extensible:

1. **Add new platforms**: Extend `universal_extractor.py` platform configuration
2. **Update preferences**: Edit the docstring in `context_engine.py`  
3. **Improve parsing**: Enhance query analysis in `context_engine.py`
4. **MCP integration**: Use the `restaurant_ai.py` interface

## License

MIT