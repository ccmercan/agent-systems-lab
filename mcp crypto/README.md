# Crypto Finance MCP Server

An MCP (Model Context Protocol) server that provides cryptocurrency price and market data using the CoinGecko API.

## External API

**CoinGecko API**: https://api.coingecko.com/api/v3
- Endpoints used:
  - `/simple/price` - Get current cryptocurrency prices
  - `/search/trending` - Get trending cryptocurrencies
- Free tier: No API key required, ~10-30 calls per minute rate limit

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup

1. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux (must use 'source', not execute directly)
# or
venv\Scripts\activate  # On Windows
```


2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the server executable (optional):
```bash
chmod +x server/main.py
```

## Running the Server

The MCP server communicates via STDIO (standard input/output). There are two ways to use it:

### Option 1: Direct Testing (Quick Way to Get API Data)

You can test the tools directly with our test script:

```bash
# Activate virtual environment first (if using one)
source venv/bin/activate

# Run quick tests
python test_tools.py test

# Or run in interactive mode
python test_tools.py interactive
```

In interactive mode, you can type:
- `price bitcoin` - Get Bitcoin price
- `price ethereum` - Get Ethereum price  
- `trending` - Get trending cryptocurrencies
- `quit` - Exit

### Option 2: Use with MCP Client (Claude Desktop / Cursor)

The server runs in STDIO mode and waits for MCP client connections:

```bash
# Activate virtual environment first (if using one)
source venv/bin/activate

# Run the server
python server/main.py
```

The server will wait for an MCP client to connect and will respond to tool calls automatically.

## MCP Client Configuration

### Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-finance": {
      "command": "/absolute/path/to/week3/venv/bin/python",
      "args": ["/absolute/path/to/week3/server/main.py"]
    }
  }
}
```

Replace `/absolute/path/to/week3/server/main.py` with your actual path.

### Cursor IDE Configuration

In Cursor, go to Settings → Features → Model Context Protocol and add a server:

- Name: `crypto-finance`
- Command: `python`
- Args: `["/absolute/path/to/week3/server/main.py"]`

## Tools

### 1. `get_crypto_price`

Get the current price and market data for a cryptocurrency.

**Parameters:**
- `coin_id` (required, string): Cryptocurrency ID (e.g., "bitcoin", "ethereum", "solana")

**Example:**
```
Tool: get_crypto_price
Arguments: {"coin_id": "bitcoin"}
```

**Output:**
```
BITCOIN Price Information:
Current Price: $43,250.50
Market Cap: $847,234,567,890
24h Change: +2.34%
```

### 2. `get_trending_cryptos`

Get the top 7 trending cryptocurrencies with their current prices.

**Parameters:**
- None

**Example:**
```
Tool: get_trending_cryptos
Arguments: {}
```

**Output:**
```
Top 7 Trending Cryptocurrencies:

1. Bitcoin (bitcoin)
   Price: $43,250.50

2. Ethereum (ethereum)
   Price: $2,650.75

...
```

## Example Invocation Flow

1. Start Claude Desktop or Cursor IDE
2. The MCP server should automatically connect
3. Ask a question like:
   - "What's the current price of Bitcoin?"
   - "Show me the trending cryptocurrencies"
   - "Get the price for Ethereum"
4. The AI will automatically call the appropriate tool and display results

## Error Handling

The server handles:
- **Timeouts**: 10-second timeout for API requests
- **Rate Limits**: Detects 429 errors and provides helpful messages
- **Invalid Coin IDs**: Returns clear error messages
- **Network Errors**: Graceful error messages for connection issues
- **Empty Results**: Handles cases where no data is returned

## Rate Limits

CoinGecko free tier allows approximately 10-30 calls per minute. The server will return a clear error message if rate limits are exceeded. Wait a minute before making more requests.

## Project Structure

```
week3/
├── assignment.md
├── README.md
├── requirements.txt
├── test_tools.py      # Test script to get API data directly
├── venv/              # Virtual environment (created during setup)
└── server/
    └── main.py
```

## Testing

### Quick Test with Direct API Calls

Test the tools and get API data directly:
```bash
# Quick tests (one-time run)
python test_tools.py test
# or with virtual environment:
venv/bin/python test_tools.py test

# Interactive mode (query multiple times)
python test_tools.py interactive
```

This will:
- Call the CoinGecko API
- Test both tools (get_crypto_price and get_trending_cryptos)
- Display real cryptocurrency data

### MCP Inspector

You can also test the server using the MCP Inspector tool:
```bash
npx @modelcontextprotocol/inspector python server/main.py
# or with virtual environment:
npx @modelcontextprotocol/inspector venv/bin/python server/main.py
```
