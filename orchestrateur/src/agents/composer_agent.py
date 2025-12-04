"""Response composition agent."""
from src.agents.base_agent import BaseAgent


class ComposerAgent(BaseAgent):
    def run(self, query: str, execution_results: dict, sql_queries: dict) -> str:
        """Compose final response from execution results."""
        prompt = f"""Compose a natural language response based on:
Original Query: {query}
SQL Queries: {sql_queries}
Results: {execution_results}

Provide a clear, concise answer.
"""
        response = self.llm.invoke(prompt)
        return response.content
