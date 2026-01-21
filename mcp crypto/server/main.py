#!/usr/bin/env python3
"""MCP Server for Crypto Finance Data using CoinGecko API"""

import asyncio
import logging
import sys
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Logging to stderr (not stdout for STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("crypto-mcp")

# CoinGecko API configuration
API_BASE = "https://api.coingecko.com/api/v3"
TIMEOUT = 10.0

server = Server("crypto-finance-mcp")


async def call_api(endpoint: str, params: dict = None) -> dict:
    """Call CoinGecko API with error handling."""
    url = f"{API_BASE}{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise Exception("Request timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise Exception("Rate limit exceeded. Please wait a minute and try again.")
        raise Exception(f"API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise Exception(f"Failed to fetch data: {str(e)}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_crypto_price",
            description="Get current price for a cryptocurrency in USD",
            inputSchema={
                "type": "object",
                "properties": {
                    "coin_id": {
                        "type": "string",
                        "description": "Cryptocurrency ID (e.g., 'bitcoin', 'ethereum', 'solana')"
                    }
                },
                "required": ["coin_id"]
            }
        ),
        Tool(
            name="get_trending_cryptos",
            description="Get top 7 trending cryptocurrencies with prices",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "get_crypto_price":
            coin_id = arguments.get("coin_id", "").strip().lower()
            
            if not coin_id:
                return [TextContent(type="text", text="Error: coin_id is required")]
            
            logger.info(f"Fetching price for {coin_id}")
            
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_change": "true"
            }
            
            data = await call_api("/simple/price", params)
            
            if not data or coin_id not in data:
                return [TextContent(
                    type="text",
                    text=f"Error: No data found for '{coin_id}'. Check the coin ID is correct."
                )]
            
            coin_data = data[coin_id]
            price = coin_data.get("usd", "N/A")
            market_cap = coin_data.get("usd_market_cap", "N/A")
            change_24h = coin_data.get("usd_24h_change", "N/A")
            
            result = f"{coin_id.upper()} Price Information:\n"
            result += f"Current Price: ${price:,.2f}\n" if isinstance(price, (int, float)) else f"Current Price: {price}\n"
            result += f"Market Cap: ${market_cap:,.0f}\n" if isinstance(market_cap, (int, float)) else f"Market Cap: {market_cap}\n"
            result += f"24h Change: {change_24h:+.2f}%\n" if isinstance(change_24h, (int, float)) else f"24h Change: {change_24h}\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_trending_cryptos":
            logger.info("Fetching trending cryptocurrencies")
            
            data = await call_api("/search/trending")
            
            if not data or "coins" not in data:
                return [TextContent(type="text", text="Error: No trending data available")]
            
            # Get coin IDs for price lookup
            coin_ids = [coin["item"]["id"] for coin in data["coins"][:7]]
            
            # Fetch prices
            price_params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
                "include_market_cap": "true"
            }
            
            price_data = await call_api("/simple/price", price_params)
            
            result = "Top 7 Trending Cryptocurrencies:\n\n"
            for idx, coin in enumerate(data["coins"][:7], 1):
                coin_info = coin["item"]
                coin_id = coin_info["id"]
                coin_name = coin_info.get("name", coin_id)
                
                result += f"{idx}. {coin_name} ({coin_id})\n"
                
                if coin_id in price_data:
                    price = price_data[coin_id].get("usd", "N/A")
                    result += f"   Price: ${price:,.2f}\n" if isinstance(price, (int, float)) else f"   Price: {price}\n"
                
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
    
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
