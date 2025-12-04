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
"""
        response = self.llm.invoke(prompt)
        
        # Mock SQL generation
        sql_queries = {}
        for schema in schemas:
            db = schema["database"]
            sql_queries[db] = {
                "query": "SELECT * FROM users LIMIT 10;",
                "params": []
            }
        
        return sql_queries
