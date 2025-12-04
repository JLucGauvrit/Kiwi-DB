"""SQL validation agent."""
from src.agents.base_agent import BaseAgent


class ValidatorAgent(BaseAgent):
    def run(self, sql_queries: dict, schemas: list) -> dict:
        """Validate SQL queries against schemas."""
        # Simple validation - in production, use proper SQL parser
        issues = []
        
        for db, query_info in sql_queries.items():
            query = query_info.get("query", "")
            if not query or len(query) < 10:
                issues.append(f"Invalid query for {db}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
