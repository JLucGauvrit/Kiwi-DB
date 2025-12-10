#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to list available tools for MongoDB MCP server"""
import asyncio
import json
import sys
import websockets


async def list_mongo_tools():
    """List all available tools for MongoDB MCP server"""
    uri = "ws://localhost:9000/ws"

    print("=" * 60)
    print("MongoDB MCP Server - Available Tools")
    print("=" * 60)
    print(f"\nConnecting to MCP Gateway: {uri}\n")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected to gateway\n")

            # Request to list tools for mongo server
            request = {
                "type": "list_tools",
                "server": "mongo"
            }

            print(f"Requesting tools for 'mongo' server...")
            await websocket.send(json.dumps(request))

            # Receive response
            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Successfully retrieved tools\n")
                tools = response_data.get("tools", [])

                if not tools:
                    print("[WARNING] No tools available for MongoDB server")
                    return

                print(f"Found {len(tools)} tool(s):\n")
                print("-" * 60)

                for i, tool in enumerate(tools, 1):
                    name = tool.get("name", "Unknown")
                    description = tool.get("description", "No description")
                    input_schema = tool.get("inputSchema", {})

                    print(f"\n{i}. {name}")
                    print(f"   Description: {description}")

                    # Display input parameters if available
                    properties = input_schema.get("properties", {})
                    if properties:
                        print(f"   Parameters:")
                        for param_name, param_info in properties.items():
                            param_type = param_info.get("type", "unknown")
                            param_desc = param_info.get("description", "")
                            required = param_name in input_schema.get("required", [])
                            req_mark = "*" if required else ""
                            print(f"     - {param_name}{req_mark} ({param_type}): {param_desc}")
                    else:
                        print(f"   Parameters: None")

                print("\n" + "-" * 60)
                print(f"Total: {len(tools)} tool(s)")
                print("=" * 60)
                print("\n* = required parameter")

            else:
                error = response_data.get("error", "Unknown error")
                print(f"[ERROR] Failed to retrieve tools: {error}")

                # Check if server is available
                available_servers = response_data.get("available_servers", [])
                if available_servers:
                    print(f"Available servers: {', '.join(available_servers)}")

    except websockets.exceptions.WebSocketException as e:
        print(f"[ERROR] WebSocket connection failed: {e}")
        print("Make sure the MCP Gateway is running on localhost:9000")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(list_mongo_tools())
