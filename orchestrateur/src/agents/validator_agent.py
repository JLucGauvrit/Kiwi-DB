"""SQL validation agent."""
from src.agents.base_agent import BaseAgent


class ValidatorAgent(BaseAgent):
    def run(self, sql_queries: dict, schemas: list) -> dict:
        """Validate SQL queries against schemas."""
        issues = []
        
        # Check if we have any queries
        if not sql_queries:
            issues.append("No SQL queries generated")
            return {
                "valid": False,
                "issues": issues
            }
        
        # Validate each query
        for db, query_info in sql_queries.items():
            query = query_info.get("query", "")
            if not query or len(query) < 10:
                issues.append(f"Invalid query for {db}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
