"""Intent classification agent."""
from src.agents.base_agent import BaseAgent


class IntentAgent(BaseAgent):
    def run(self, query: str) -> dict:
        """Classify user intent from query."""
        prompt = f"""Analyze this query and extract the intent:
Query: {query}

Return a JSON with:
- intent_type: (search, aggregate, join, filter)
- entities: list of entities mentioned
- databases: list of databases likely needed (use "postgres" for SQL databases)
"""
        response = self.invoke(prompt)
        
        # Simple parsing - in production use structured output
        return {
            "intent_type": "search",
            "entities": [],
            "databases": ["postgres"],
            "raw_response": response
        }
