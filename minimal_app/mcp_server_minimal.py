#!/usr/bin/env python3
"""
Minimal MCP Server for OmniTech Support
========================================

This is a simplified version that demonstrates MCP (Model Context Protocol) basics:
- Loads emails and orders from JSON file (no database needed)
- Two simple tools: search_emails and search_orders
- Clear, easy-to-understand code

Perfect for learning how MCP servers work!
"""

import asyncio
import json
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# ═══════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════

# Load data from JSON file
DATA_FILE = Path(__file__).parent / "minimal_data.json"

def load_data():
    """Load emails and orders from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return data.get('emails', []), data.get('orders', [])
    except FileNotFoundError:
        print(f"Warning: Data file not found at {DATA_FILE}")
        return [], []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return [], []

EMAILS, ORDERS = load_data()

# Print status
print(f"Loaded {len(EMAILS)} emails and {len(ORDERS)} orders from {DATA_FILE.name}")

# ═══════════════════════════════════════════════════════════════════════════
# MCP SERVER SETUP
# ═══════════════════════════════════════════════════════════════════════════

app = Server("omnitech-support-minimal")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Tell the LLM what tools are available.
    This is like showing someone a toolbox - they can see what's inside!
    """
    return [
        Tool(
            name="search_emails",
            description="Search customer support emails. You can search by customer email, keywords in subject/body, order ID, or status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for (email address, keywords, order ID, etc.)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_orders",
            description="Search customer orders. You can search by order ID, customer email, product name, or status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for (order ID, email, product name, etc.)"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    When the LLM wants to use a tool, this function is called.
    It's like the LLM asking us to fetch information from our database.
    """

    if name == "search_emails":
        query = arguments.get("query", "").lower()

        # Search through all emails
        results = []
        for email in EMAILS:
            # Check if query matches any field
            if (query in email["customer_email"].lower() or
                query in email["subject"].lower() or
                query in email["body"].lower() or
                query in email.get("status", "").lower()):
                results.append(email)

        if results:
            # Format the results nicely
            formatted = f"Found {len(results)} email(s):\n\n"
            for email in results:
                formatted += f"ID: {email['id']}\n"
                formatted += f"From: {email['customer_email']}\n"
                formatted += f"Subject: {email['subject']}\n"
                formatted += f"Date: {email['date']}\n"
                formatted += f"Status: {email['status']}\n"
                formatted += f"Body: {email['body']}\n"
                formatted += "-" * 50 + "\n\n"

            return [TextContent(type="text", text=formatted)]
        else:
            return [TextContent(type="text", text=f"No emails found matching: {query}")]

    elif name == "search_orders":
        query = arguments.get("query", "").lower()

        # Search through all orders
        results = []
        for order in ORDERS:
            # Check if query matches any field
            if (query in order["order_id"].lower() or
                query in order["customer_email"].lower() or
                query in order["product"].lower() or
                query in order["status"].lower()):
                results.append(order)

        if results:
            # Format the results nicely
            formatted = f"Found {len(results)} order(s):\n\n"
            for order in results:
                formatted += f"Order ID: {order['order_id']}\n"
                formatted += f"Customer: {order['customer_email']}\n"
                formatted += f"Product: {order['product']}\n"
                formatted += f"Price: {order['price']}\n"
                formatted += f"Order Date: {order['order_date']}\n"
                formatted += f"Status: {order['status']}\n"
                formatted += f"Tracking: {order['tracking']}\n"
                formatted += "-" * 50 + "\n\n"

            return [TextContent(type="text", text=formatted)]
        else:
            return [TextContent(type="text", text=f"No orders found matching: {query}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# ═══════════════════════════════════════════════════════════════════════════
# MAIN - START THE SERVER
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Start the MCP server using stdio (standard input/output)"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
