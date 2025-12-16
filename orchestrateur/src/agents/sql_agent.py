"""SQL generation agent."""
from src.agents.base_agent import BaseAgent


class SQLAgent(BaseAgent):
    def run(self, intent: dict, schemas: list) -> dict:
        """Generate SQL queries for each database."""
        query_text = intent.get("raw_response", "")
        
        prompt = f"""Generate SQL queries based on:
Intent: {intent}
Schemas: {schemas}

Return SQL queries for each database.
Generate a valid SELECT query based on the available tables.
"""
        response = self.invoke(prompt)
        
        # Generate SQL for each schema
        sql_queries = {}
        for schema in schemas:
            db = schema["database"]
            tables = schema.get("tables", [])
            
            if tables:
                # Use the first table as default
                sql_queries[db] = {
                    "query": f"SELECT * FROM {tables[0]} LIMIT 10;",
                    "params": []
                }
            else:
                sql_queries[db] = {
                    "query": "SELECT 1;",  # Fallback query
                    "params": []
                }
        
        return sql_queries
