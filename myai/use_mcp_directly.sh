#!/bin/bash
# Direct browser-use MCP commands for restaurant search

# Example: Search for dinner for 5 people at 8PM on Tuesday
URL="https://www.opentable.com/s?covers=5&dateTime=2025-07-15T20:00&metroId=4&term=vegetarian&prices=2,3"

echo "Using browser-use MCP to find vegetarian restaurants..."
echo ""

# Step 1: Navigate to the URL
echo "Step 1: Navigate to OpenTable search"
browser_navigate "$URL"

# Step 2: Wait for page to load
sleep 3

# Step 3: Get the page state to see what's available
echo "Step 2: Getting page state"
browser_get_state

# Step 4: Extract restaurant data
echo "Step 3: Extracting restaurant information"
browser_extract_content "Extract all restaurant names, cuisine types, price levels ($ symbols), and neighborhoods from the restaurant cards on this page. Format each as: [Name] | [Cuisine] | [Price] | [Neighborhood]"

# Alternative: You could also use browser_extract_links to get reservation links
# browser_extract_links "reservation" 

echo "Done!"