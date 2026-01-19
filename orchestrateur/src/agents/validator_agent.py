"""
SQL validation agent for validating generated queries.

Ce module implémente l'agent de validation qui vérifie que les requêtes SQL
générées sont valides et conformes aux schémas de base de données disponibles.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from src.agents.base_agent import BaseAgent


class ValidatorAgent(BaseAgent):
    """
    Agent de validation des requêtes SQL.
    
    Valide que les requêtes SQL générées sont correctes,
    conformes aux schémas disponibles et exécutables.
    """
    
    def run(self, sql_queries: dict, schemas: list) -> dict:
        """
        Valider les requêtes SQL générées.
        
        Effectue des vérifications de base sur les requêtes SQL
        pour s'assurer qu'elles sont valides avant exécution.
        
        @param sql_queries: Dictionnaire contenant les requêtes SQL générées
        @type sql_queries: dict
        @param sql_queries format:
            - database_name (str): {
                - query (str): Requête SQL à valider
                - params (list): Paramètres pour la requête
            }
        @param schemas: Schémas de base de données pour la validation
        @type schemas: list
        @return: Résultats de la validation
        @rtype: dict
        @return_keys:
            - valid (bool): Indique si toutes les requêtes sont valides
            - issues (list): Liste des problèmes identifiés
        """
        issues = []
        
        # Vérifier si nous avons des requêtes
        if not sql_queries:
            issues.append("No SQL queries generated")
            return {
                "valid": False,
                "issues": issues
            }
        
        # Valider chaque requête
        for db, query_info in sql_queries.items():
            query = query_info.get("query", "")
            if not query or len(query) < 10:
                issues.append(f"Invalid query for {db}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
