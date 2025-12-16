"""Query execution across federated databases via MCP."""
import httpx
from typing import Dict, Any


class QueryRunner:
    def __init__(self, config: dict):
        self.config = config
        self.mcp_servers = {
            "postgres": "http://mcp-postgres:7000"
        }

    def execute_federated(self, sql_queries: dict) -> dict:
        """Execute queries across multiple databases via MCP servers."""
        results = {}
        
        for db, query_info in sql_queries.items():
            try:
                result = self._execute_via_mcp(db, query_info)
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

    def _execute_via_mcp(self, database: str, query_info: dict) -> list:
        """Execute query via MCP server."""
        if database not in self.mcp_servers:
            raise ValueError(f"No MCP server configured for: {database}")
        
        mcp_url = self.mcp_servers[database]
        query = query_info.get("query", "")
        
        try:
            response = httpx.post(
                f"{mcp_url}/{database}/query",
                json={"query": query},
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                raise Exception(f"MCP server returned {response.status_code}: {response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to MCP server: {str(e)}")
