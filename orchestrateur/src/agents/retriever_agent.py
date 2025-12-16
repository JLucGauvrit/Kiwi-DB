"""Schema retrieval agent."""
from src.agents.base_agent import BaseAgent
import httpx


class RetrieverAgent(BaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.mcp_servers = {
            "postgres": "http://mcp-postgres:7000"
        }
    
    def run(self, intent: dict) -> list:
        """Retrieve relevant schemas via MCP servers."""
        databases = intent.get("databases", [])
        
        schemas = []
        for db in databases:
            if db in self.mcp_servers:
                schema_info = self._get_schema_from_mcp(db)
                schemas.append({
                    "database": db,
                    "tables": schema_info.get("tables", []),
                    "schema": schema_info
                })
            else:
                schemas.append({
                    "database": db,
                    "tables": [],
                    "schema": "unknown"
                })
        
        return schemas
    
    def _get_schema_from_mcp(self, database: str) -> dict:
        """Get schema information from MCP server."""
        mcp_url = self.mcp_servers.get(database)
        
        try:
            # Call MCP server to get schema
            response = httpx.post(
                f"{mcp_url}/{database}/schema",
                json={"action": "list_tables"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"tables": [], "error": f"MCP returned {response.status_code}"}
        except Exception as e:
            return {"tables": [], "error": str(e)}
