#!/usr/bin/env python3
"""Direct test of MCP SSE connection"""
import asyncio
import sys
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_mcp_connection():
    """Test direct connection to MCP server via SSE"""
    url = "http://localhost:8000/sse"

    print(f"Connecting to MCP server at {url}...")

    try:
        async with sse_client(url) as (read, write):
            print("[OK] SSE connection established")

            async with ClientSession(read, write) as session:
                print("[OK] MCP session created")

                init_result = await session.initialize()
                print(f"[OK] Session initialized")
                print(f"  Server name: {init_result.serverInfo.name}")
                print(f"  Server version: {init_result.serverInfo.version}")
                print(f"  Protocol version: {init_result.protocolVersion}")

                print("\n--- Listing Tools ---")
                tools_result = await session.list_tools()
                print(f"[OK] Found {len(tools_result.tools)} tools:")

                for i, tool in enumerate(tools_result.tools[:10], 1):
                    print(f"  {i}. {tool.name}")
                    if tool.description:
                        print(f"     {tool.description[:80]}...")

                if len(tools_result.tools) > 10:
                    print(f"  ... and {len(tools_result.tools) - 10} more tools")

                print("\n--- Listing Resources ---")
                resources_result = await session.list_resources()
                print(f"[OK] Found {len(resources_result.resources)} resources")

                print("\n[SUCCESS] MCP connection test completed!")

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_mcp_connection())
    sys.exit(exit_code)
