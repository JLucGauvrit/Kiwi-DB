#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for MCP Gateway WebSocket connection"""
import asyncio
import json
import sys
import websockets
import aiohttp


async def test_gateway():
    """Test the MCP gateway WebSocket connection"""

    # Test 1: List servers via HTTP
    print("\n--- Test 1: List Servers (HTTP) ---")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:9000/servers") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"[OK] Successfully listed servers")
                    servers = data.get("servers", [])
                    print(f"  Found {len(servers)} servers:")
                    for server in servers:
                        if isinstance(server, dict):
                            print(f"    - {server.get('name')}: {server.get('type')} (connected: {server.get('connected')})")
                        else:
                            print(f"    - {server}")
                else:
                    print(f"[ERROR] HTTP {response.status}")
    except Exception as e:
        print(f"[ERROR] Failed to list servers: {e}")

    # WebSocket tests
    uri = "ws://localhost:9000/ws"
    print(f"\nConnecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected to gateway")

            print("\n--- Test 2: List Tools ---")
            request = {
                "type": "list_tools",
                "server": "postgres"
            }
            print(f"Sending: {json.dumps(request, indent=2)}")
            await websocket.send(json.dumps(request))

            response = await websocket.recv()
            print(f"Response: {response}")
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Successfully listed tools")
                tools = response_data.get("tools", [])
                print(f"  Found {len(tools)} tools:")
                for tool in tools[:5]:  # Show first 5 tools
                    print(f"    - {tool.get('name')}: {tool.get('description', 'No description')[:60]}...")
            else:
                print(f"[ERROR] Error: {response_data.get('error')}")

            print("\n--- Test 3: List Resources ---")
            request = {
                "type": "list_resources",
                "server": "postgres"
            }
            print(f"Sending: {json.dumps(request, indent=2)}")
            await websocket.send(json.dumps(request))

            response = await websocket.recv()
            print(f"Response: {response}")
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Successfully listed resources")
                resources = response_data.get("resources", [])
                print(f"  Found {len(resources)} resources")
            else:
                print(f"[ERROR] Error: {response_data.get('error')}")

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_gateway())
