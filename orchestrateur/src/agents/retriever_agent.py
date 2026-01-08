"""Schema retrieval agent via MCP."""
from src.agents.base_agent import BaseAgent
from src.mcp_client import MCPGatewayClient
import asyncio

#
class RetrieverAgent(BaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.mcp_client = MCPGatewayClient(config.get("mcp_gateway_url"))
    
    def run(self, intent: dict) -> list:
        """Retrieve relevant schemas via MCP Gateway."""
        databases = intent.get("databases", [])
        
        schemas = []
        for db in databases:
            if db == "postgres":
                # Use a simple approach - create new event loop in thread
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                schema_info = loop.run_until_complete(self._get_schema_from_mcp(db))
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
    
    async def _get_schema_from_mcp(self, database: str) -> dict:
        """Get schema information from MCP server via gateway."""
        try:
            # List objects in the public schema
            objects_response = await self.mcp_client.call_tool(
                tool="list_objects",
                arguments={"schema_name": "public", "object_type": "table"},
                server=database
            )
            
            tables = []
            schema_description = ""
            
            if objects_response.get("success"):
                result = objects_response.get("result", [])
                if result and len(result) > 0:
                    text = result[0].get("text", "")
                    schema_description = text
                    
                    # Parse the JSON response
                    import json
                    try:
                        table_list = json.loads(text)
                        if isinstance(table_list, list):
                            for item in table_list:
                                if isinstance(item, dict) and 'name' in item:
                                    tables.append(item['name'])
                    except json.JSONDecodeError:
                        # Fallback: parse as text
                        import re
                        matches = re.findall(r"'name':\s*'([^']+)'", text)
                        tables = matches if matches else []
            
            return {
                "tables": tables,
                "schema_description": schema_description
            }
        except Exception as e:
            return {"tables": [], "error": str(e)}
        finally:
            await self.mcp_client.disconnect()
