# Using Browser-Use MCP Server

Browser-use can run as an MCP (Model Context Protocol) server, which provides direct browser control commands.

## Starting the MCP Server

```bash
poetry run browser-use --mcp
```

This starts the MCP server that listens on stdin/stdout for JSON-RPC commands.

## Using with Claude Desktop or MCP Client

If you're using Claude Desktop, you need to add browser-use to your MCP servers configuration:

1. Edit your Claude Desktop config (usually at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS)

2. Add browser-use to the mcpServers section:

```json
{
  "mcpServers": {
    "browser-use": {
      "command": "poetry",
      "args": ["run", "browser-use", "--mcp"],
      "cwd": "/Users/jh/Code/exploration/agihousehackathon/myai"
    }
  }
}
```

3. Restart Claude Desktop

## Direct Usage with browser-use CLI

For now, you can use browser-use directly with a single prompt:

```bash
# Find restaurants with a single command
poetry run browser-use -p "Go to https://www.opentable.com/s?covers=5&dateTime=2025-07-15T20:00&metroId=4&term=vegetarian&prices=2,3 and extract the first 5 restaurant names, cuisine types, prices, and neighborhoods. Format as: [Name] | [Cuisine] | [Price] | [Neighborhood]"

# Or run interactively
poetry run browser-use
```

## Example: Finding Vegetarian Restaurants

```bash
# Headless mode (no browser window)
poetry run browser-use --headless -p "Navigate to OpenTable, search for vegetarian restaurants in San Francisco for 5 people at 8pm, and list the first 5 results with name, cuisine, price, and location"

# With visible browser
poetry run browser-use -p "Navigate to OpenTable, search for vegetarian restaurants in San Francisco for 5 people at 8pm, and list the first 5 results with name, cuisine, price, and location"
```

## Using the URL directly

Since we already build the perfect URL with all preferences:

```bash
poetry run browser-use --headless -p "Go to https://www.opentable.com/s?covers=5&dateTime=2025-07-15T20:00&metroId=4&term=vegetarian&prices=2,3 and extract restaurant information from the first 5 listings shown. For each restaurant, get the name, cuisine type, price level, and neighborhood. Format the output as a list."
```