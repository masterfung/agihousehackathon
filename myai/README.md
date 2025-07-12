# MyAI - Personal Context-Driven Restaurant Finder

A browser automation system that uses your personal preferences to find and evaluate restaurants across multiple platforms (OpenTable, Yelp, Google Maps).

## Overview

This project demonstrates how personal context can enhance AI-driven automation. It uses hardcoded preferences now but is designed to integrate with MCP (Model Context Protocol) servers for dynamic preference management.

## Features

- 🎯 **Personal Preference System**: Dietary restrictions, cuisine preferences, budget, location, and more
- 🏆 **Smart Scoring**: Evaluates restaurants on multiple criteria (0-100 score)
- 🌐 **Multi-Platform Search**: Parallel search across OpenTable, Resy, Yelp, and Google Maps
- ⚡ **Platform Optimization**: Uses each site's native filters for fast, accurate results
- 📅 **Smart Date Parsing**: Understands "tomorrow", "next Friday", etc. and sets dates correctly
- 🎯 **Context Prioritization**: Ranks requirements by importance (dietary > location > cuisine)
- ⏱️ **Fast Results**: 45-second timeout per platform to prevent endless searching
- 🤖 **Browser Automation**: Uses browser-use with Gemini 2.5 Pro to search and extract data
- 📊 **Detailed Evaluation**: Breaks down scores by category with explanations

## Your Preferences (Hardcoded)

```
- Dietary: Vegetarian (no peanuts), not just salads
- Cuisines: Asian, Mexican preferred
- Budget: $30-50 per dish
- Location: San Francisco 94109, prefers public transit
- Wine: Important, corkage preferred
- Spice: Mild tolerance
```

## Installation

```bash
# Install dependencies with Poetry
poetry install

# Set up environment
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

## Usage

### Find Restaurants
```bash
# Default search (all platforms in parallel)
poetry run python src/myai/main.py find

# Search all platforms for specific query
poetry run python src/myai/main.py find "lunch tomorrow"

# Search single platform only
poetry run python src/myai/main.py find "dinner tonight" yelp
poetry run python src/myai/main.py find "lunch tomorrow" google

# Debug mode - see browser in action
BROWSER_HEADLESS=false poetry run python src/myai/main.py find "dinner" yelp

# Increase timeout for slow connections
BROWSER_TIMEOUT=60000 poetry run python src/myai/main.py find
```

### Evaluate Specific Restaurant
```bash
python -m myai evaluate "Shizen" "Japanese, Sushi" "$$" "370 14th St, San Francisco"
```

### Run Demo
```bash
python example_usage.py
```

### Debug Single Platform
```bash
# Test one platform at a time
python test_single_platform.py yelp
python test_single_platform.py google

# See browser in action
BROWSER_HEADLESS=false python test_single_platform.py opentable
```

## How It Works

1. **Preferences** (`preferences.py`): Stores your personal context
2. **Date Parser** (`date_parser.py`): Understands natural language dates ("tomorrow", "next Friday")
3. **Search Optimizer** (`search_optimizer.py`): Builds smart queries and prioritizes context
4. **Site Optimizations** (`site_optimizations.py`): Platform-specific search filters
5. **Evaluator** (`evaluator.py`): Scores restaurants based on preferences
6. **Finder** (`restaurant_finder.py`): Automates browser to search platforms in parallel
7. **Main** (`main.py`): Orchestrates the search and evaluation

### Key Optimizations

#### Smart Search Queries
- **Google Maps**: "vegetarian mexican restaurants near 94109" (not all cuisines at once)
- **Yelp**: Searches "vegetarian restaurants" directly
- **OpenTable**: Simple city search, reads vegetarian-friendly results
- **Resy**: Searches by cuisine type (Mexican/Asian) since dietary filters don't work well

#### Context Prioritization
1. **🚨 Must Have**: Dietary restrictions (vegetarian, allergies)
2. **⚡ Important**: Location, budget, transit access
3. **👍 Nice to Have**: Cuisine preferences, wine program

#### Performance Optimizations
- **Simple Extraction**: Just navigate to URL and extract text
- **3-Minute Timeout**: Gives agent enough time to load pages
- **Debug Mode**: Run with `BROWSER_HEADLESS=false` to see what's happening
- **Raw Text Parsing**: Extracts all text and parses it locally
- **Direct URLs**: Pre-built search URLs to avoid complex navigation

## Scoring System

- **Dietary Fit** (25 points): Vegetarian options quality and variety
- **Cuisine Match** (20 points): Alignment with preferred cuisines
- **Budget Fit** (20 points): Price range compatibility
- **Location** (20 points): Distance and transit accessibility
- **Wine Program** (15 points): Wine list quality and corkage policy

## Future MCP Integration

The system is designed to connect to an MCP server that will:
- Dynamically load user preferences
- Update preferences based on feedback
- Share context across different AI services
- Maintain privacy with local data control

## Example Output

```
🚀 Searching for restaurants for 'dinner tomorrow' across 4 platforms...

Using your preferences:
  • Dietary: Vegetarian (no peanuts)
  • Cuisines: asian, mexican
  • Budget: $30-50/dish
  • Location: 94109 (prefer public transit)
  • Wine: Important with corkage preference
  • Spice tolerance: Mild

🔄 Searching 4 platforms in parallel...
  🔍 Searching opentable...
  🔍 Searching resy...
  🔍 Searching yelp...
  🔍 Searching google...
  ✅ Found 5 restaurants on yelp
  ✅ Found 5 restaurants on google
  ✅ Found 4 restaurants on opentable
  ✅ Found 3 restaurants on resy

🎯 Top 5 restaurants from all platforms:

1. Shizen Vegan Sushi Bar (YELP)
   Score: 88.0/100 - 🌟 Excellent Match!
   Cuisine: Vegan, Sushi Bars, Japanese
   Price Range: $$
   Address: Mission
   
   This is an excellent match for your preferences! Strengths: Excellent vegetarian options available; 
   Serves your preferred Vegan, Sushi Bars, Japanese cuisine; Price range perfectly matches your budget; 
   Conveniently located with transit access.

2. Greens Restaurant (GOOGLE)
   Score: 85.5/100 - 🌟 Excellent Match!
   Cuisine: Vegetarian restaurant
   Price Range: $$
   Address: Fort Mason
   Distance: 1.5 miles
   
   ...

💡 Top Recommendation:
   Shizen Vegan Sushi Bar (YELP)
   Score: 88.0/100
   This is an excellent match for your preferences!

📅 Ready to book for dinner tomorrow?
   Visit yelp to make a reservation.
```

## Troubleshooting

### No Results Found
1. **Run in visible mode**: `BROWSER_HEADLESS=false poetry run python src/myai/main.py find "dinner" yelp`
2. **Test single platform**: `python test_single_platform.py google`
3. **Check browser loads**: The agent might be having issues with page loading
4. **Increase timeout**: Set longer timeout if on slow connection
5. **Check API key**: Ensure your `GOOGLE_API_KEY` is valid in `.env`

### AFC Rate Limit Errors
- The Gemini API has limits on function calls
- Try using a single platform instead of all 4
- Consider using `gemini-1.5-flash` instead of `gemini-2.5-flash-lite-preview`

### Debugging Tips
```bash
# See what the browser is doing
BROWSER_HEADLESS=false python test_single_platform.py yelp

# Test with more verbose output
poetry run python src/myai/main.py find "dinner" google

# Check if websites are accessible
curl -I https://www.yelp.com
```

## License

MIT