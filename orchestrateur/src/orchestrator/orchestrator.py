"""Orchestrateur utilisant un agent LLM avec tool calling MCP."""
from typing import Dict, Any
from src.agents.mcp_agent import MCPAgent


class FederatedRAGOrchestrator:
    """Orchestrateur qui utilise un LLM avec tool calling pour interagir avec MCP."""

    def __init__(self, config: dict):
        self.config = config
        self.agent = MCPAgent(config)

    def run(self, query: str) -> dict:
        """
        Traite une requête de manière synchrone.
        Note: Utilise l'implémentation asynchrone en interne.
        """
        import asyncio
        return asyncio.run(self.run_async(query))

    async def run_async(self, query: str) -> dict:
        """
        Traite une requête de manière asynchrone.

        Args:
            query: La requête de l'utilisateur

        Returns:
            Dictionnaire contenant les résultats
        """
        result = await self.agent.process_query(query)
        return result
