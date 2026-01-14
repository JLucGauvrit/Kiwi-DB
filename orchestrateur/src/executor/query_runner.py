"""Query execution via MCP Gateway."""
from src.mcp_client import MCPGatewayClient
import asyncio
from typing import Dict, Any


class QueryRunner:
    def __init__(self, config: dict):
        self.config = config
        self.mcp_client = MCPGatewayClient(config.get("mcp_gateway_url"))

    def execute_federated(self, sql_queries: dict) -> dict:
        """Execute queries across multiple databases via MCP Gateway."""
        results = {}
        
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        
        for db, query_info in sql_queries.items():
            try:
                result = loop.run_until_complete(self._execute_via_mcp(db, query_info))
                results[db] = {
                    "success": True,
                    "data": result,
                    "rows": len(result) if isinstance(result, list) else 0
                }
            except Exception as e:
                results[db] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results

    async def _execute_via_mcp(self, database: str, query_info: dict) -> list:
        """Execute query via MCP Gateway."""
        query = query_info.get("query", "")
        
        try:
            # Call the execute_sql tool on the MCP server
            response = await self.mcp_client.call_tool(
                tool="execute_sql",
                arguments={"sql": query},
                server=database
            )
            
            if response.get("success"):
                result = response.get("result", [])
                if result and len(result) > 0:
                    # Extract the text content from MCP response
                    text = result[0].get("text", "")
                    # The MCP server returns results as text
                    return [{"result": text}]
                return []
            else:
                raise Exception(f"MCP query failed: {response.get('error', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Failed to execute query via MCP: {str(e)}")
        finally:
            await self.mcp_client.disconnect()
