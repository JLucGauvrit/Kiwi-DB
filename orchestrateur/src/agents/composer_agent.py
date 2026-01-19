"""
Response composition agent for generating natural language responses.

Ce module implémente l'agent de composition qui génère des réponses
en langage naturel basées sur les résultats de l'exécution des requêtes SQL.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from src.agents.base_agent import BaseAgent


class ComposerAgent(BaseAgent):
    """
    Agent de composition de réponse finale.
    
    Prend les résultats de l'exécution des requêtes SQL et génère
    une réponse naturelle et compréhensible pour l'utilisateur.
    """
    
    def run(self, query: str, execution_results: dict, sql_queries: dict) -> str:
        """
        Composer une réponse naturelle basée sur les résultats d'exécution.
        
        Utilise le modèle de langage pour transformer les résultats SQL
        bruts en une réponse en langage naturel cohérente et lisible.
        
        @param query: Requête utilisateur originale
        @type query: str
        @param execution_results: Résultats de l'exécution des requêtes SQL
        @type execution_results: dict
        @param execution_results format:
            - database_name (str): {
                - success (bool): Indique si l'exécution a réussi
                - data (list): Données retournées par la requête
                - error (str): Message d'erreur si l'exécution a échoué
            }
        @param sql_queries: Requêtes SQL qui ont été exécutées (pour le contexte)
        @type sql_queries: dict
        @return: Réponse en langage naturel
        @rtype: str
        """
        prompt = f"""Compose a natural language response based on:
Original Query: {query}
SQL Queries: {sql_queries}
Results: {execution_results}

Provide a clear, concise answer.
"""
        response = self.invoke(prompt)
        return response
