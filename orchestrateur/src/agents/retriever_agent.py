"""Schema retrieval agent via MCP."""
from src.agents.base_agent import BaseAgent
from src.mcp_client import MCPGatewayClient
import asyncio
import json
import re


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
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                schema_info = loop.run_until_complete(self._get_schema_from_mcp(db))
                schemas.append({
                    "database": db,
                    "tables": schema_info.get("tables", []),
                    "columns": schema_info.get("columns", {}),
                    "schema": schema_info
                })
            else:
                schemas.append({
                    "database": db,
                    "tables": [],
                    "columns": {},
                    "schema": "unknown"
                })
        
        return schemas
    
    async def _get_schema_from_mcp(self, database: str) -> dict:
        """Get schema information from MCP server via gateway."""
        try:
            # List tables in the public schema
            objects_response = await self.mcp_client.call_tool(
                tool="list_objects",
                arguments={"schema_name": "public", "object_type": "table"},
                server=database
            )
            
            tables = []
            columns_by_table = {}
            
            if objects_response.get("success"):
                result = objects_response.get("result", [])
                if result and len(result) > 0:
                    text = result[0].get("text", "")
                    
                    # Try to parse as JSON first
                    try:
                        table_list = json.loads(text)
                        if isinstance(table_list, list):
                            for item in table_list:
                                if isinstance(item, dict) and 'name' in item:
                                    table_name = item['name']
                                    tables.append(table_name)
                                    
                                    # Get column details for each table
                                    columns_by_table[table_name] = await self._get_table_columns(database, table_name)
                    except json.JSONDecodeError:
                        # Fallback: parse as text
                        matches = re.findall(r"'name':\s*'([^']+)'", text)
                        tables = matches if matches else []
                        
                        # Get columns for each table
                        for table_name in tables:
                            columns_by_table[table_name] = await self._get_table_columns(database, table_name)
            
            return {
                "tables": tables,
                "columns": columns_by_table,
                "schema_description": f"Available tables: {', '.join(tables)}"
            }
        except Exception as e:
            return {"tables": [], "columns": {}, "error": str(e)}
        finally:
            await self.mcp_client.disconnect()
    
    async def _get_table_columns(self, database: str, table_name: str) -> list:
        """Get column details for a specific table."""
        try:
            details_response = await self.mcp_client.call_tool(
                tool="get_object_details",
                arguments={
                    "schema_name": "public",
                    "object_name": table_name,
                    "object_type": "table"
                },
                server=database
            )
            
            if details_response.get("success"):
                result = details_response.get("result", [])
                if result:
                    text = result[0].get("text", "")
                    
                    # Try to parse column information
                    columns = []
                    try:
                        # Try JSON parsing
                        col_data = json.loads(text)
                        if isinstance(col_data, list):
                            for col in col_data:
                                if isinstance(col, dict):
                                    columns.append({
                                        "name": col.get("name", ""),
                                        "type": col.get("type", ""),
                                        "nullable": col.get("nullable", True)
                                    })
                    except json.JSONDecodeError:
                        # Fallback: parse as text
                        for line in text.split("\n"):
                            if "|" in line:
                                parts = [p.strip() for p in line.split("|")]
                                if len(parts) >= 2 and parts[0] and parts[0] != "Column":
                                    columns.append({
                                        "name": parts[0],
                                        "type": parts[1] if len(parts) > 1 else "unknown"
                                    })
                    
                    return columns
        except Exception:
            pass
        
        return []
