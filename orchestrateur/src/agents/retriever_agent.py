"""Schema retrieval agent."""
from src.agents.base_agent import BaseAgent


class RetrieverAgent(BaseAgent):
    def run(self, intent: dict) -> list:
        """Retrieve relevant schemas based on intent."""
        # In production, this would query MCP servers for schemas
        databases = intent.get("databases", [])
        
        schemas = []
        for db in databases:
            schemas.append({
                "database": db,
                "tables": ["users", "products", "orders"],
                "schema": "mock_schema"
            })
        
        return schemas
