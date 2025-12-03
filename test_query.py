#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for executing SQL queries via MCP Gateway"""
import asyncio
import json
import sys
import websockets


async def test_sql_query():
    """Test SQL query execution via MCP gateway"""
    uri = "ws://localhost:9000/ws"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected to gateway\n")

            print("=== Test 1: List Database Schemas ===")
            request = {
                "type": "call_tool",
                "server": "postgres",
                "tool": "list_schemas",
                "arguments": {}
            }
            print(f"Sending: {json.dumps(request, indent=2)}")
            await websocket.send(json.dumps(request))

            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Successfully listed schemas")
                result = response_data.get("result", [])
                print(f"Result: {json.dumps(result, indent=2)}\n")
            else:
                print(f"[ERROR] Error: {response_data.get('error')}\n")

            print("=== Test 2: List Tables in 'public' Schema ===")
            request = {
                "type": "call_tool",
                "server": "postgres",
                "tool": "list_objects",
                "arguments": {
                    "schema_name": "public",
                    "object_type": "table"
                }
            }
            print(f"Sending: {json.dumps(request, indent=2)}")
            await websocket.send(json.dumps(request))

            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Successfully listed tables")
                result = response_data.get("result", [])
                print(f"Result: {json.dumps(result, indent=2)}\n")
            else:
                print(f"[ERROR] Error: {response_data.get('error')}\n")

            print("=== Test 3: Execute SQL Query ===")
            sql_query = "SELECT version() as postgres_version;"
            request = {
                "type": "call_tool",
                "server": "postgres",
                "tool": "execute_sql",
                "arguments": {
                    "sql": sql_query
                }
            }
            print(f"SQL Query: {sql_query}")
            print(f"Sending: {json.dumps(request, indent=2)}")
            await websocket.send(json.dumps(request))

            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Query executed successfully")
                result = response_data.get("result", {})
                print(f"Result: {json.dumps(result, indent=2)}\n")
            else:
                print(f"[ERROR] Error: {response_data.get('error')}\n")

            print("=== Test 4: Get Current Database Time ===")
            sql_query = "SELECT NOW() as current_time, CURRENT_DATABASE() as database_name;"
            request = {
                "type": "call_tool",
                "server": "postgres",
                "tool": "execute_sql",
                "arguments": {
                    "sql": sql_query
                }
            }
            print(f"SQL Query: {sql_query}")
            print(f"Sending: {json.dumps(request, indent=2)}")
            await websocket.send(json.dumps(request))

            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data.get("success"):
                print("[OK] Query executed successfully")
                result = response_data.get("result", {})
                print(f"Result: {json.dumps(result, indent=2)}\n")
            else:
                print(f"[ERROR] Error: {response_data.get('error')}\n")

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sql_query())
