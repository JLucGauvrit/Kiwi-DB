"""Orchestrateur utilisant un agent LLM avec tool calling MCP."""
from typing import Dict, Any
import logging
from src.agents.mcp_agent import MCPAgent
from src.agents.intent_agent import IntentAgent

logger = logging.getLogger(__name__)


class FederatedRAGOrchestrator:
    """Orchestrateur qui utilise un LLM avec tool calling pour interagir avec MCP."""

    def __init__(self, config: dict):
        self.config = config
        self.intent_agent = IntentAgent(config)
        self.mcp_agent = MCPAgent(config)

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
        # Étape 1: Classifier l'intention de la requête
        logger.info(f"Classifying intent for query: {query}")
        intent_result = self.intent_agent.run(query)
        logger.info(f"Intent classification result: {intent_result}")

        # Vérifier si la requête nécessite un accès à la base de données
        requires_database = intent_result.get("requires_database", False)

        if not requires_database:
            # Requête de type connaissance générale
            logger.info("Query is general knowledge, not database-related")
            return {
                "success": True,
                "query": query,
                "intent": intent_result,
                "answer": (
                    "Je suis un assistant spécialisé dans l'interrogation de bases de données. "
                    "Votre question semble concerner des connaissances générales plutôt que des données "
                    "stockées dans une base de données.\n\n"
                    f"Raison: {intent_result.get('reason', 'Question de type connaissance générale')}\n\n"
                    "Pour obtenir des informations sur vos données, veuillez poser une question concernant "
                    "vos utilisateurs, produits, commandes ou autres données de votre base de données."
                ),
                "tool_calls": [],
                "iterations": 0
            }

        # Étape 2: Requête nécessite un accès à la base de données - utiliser MCP Agent
        logger.info("Query requires database access, proceeding with MCP Agent")
        result = await self.mcp_agent.process_query(query)

        # Ajouter les informations d'intention au résultat
        result["intent"] = intent_result

        return result
