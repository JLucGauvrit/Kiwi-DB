"""
Query execution engine for federated database queries via MCP.

Ce module implémente le moteur d'exécution des requêtes qui execute
les requêtes SQL sur les bases de données via la passerelle MCP.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from src.mcp_client import MCPGatewayClient
import asyncio
from typing import Dict, Any


class QueryRunner:
    """
    Moteur d'exécution de requêtes SQL fédérées.
    
    Exécute les requêtes SQL sur plusieurs bases de données
    via la passerelle MCP, en gestion asynchrone.
    
    @param config: Configuration contenant l'URL de la passerelle MCP
    @type config: dict
    
    @ivar config: Configuration de l'exécuteur
    @ivar mcp_client: Client pour communiquer avec la passerelle MCP
    """
    
    def __init__(self, config: dict):
        """
        Initialiser le moteur d'exécution de requêtes.
        
        @param config: Configuration contenant les paramètres de connexion
        @type config: dict
        """
        self.config = config
        self.mcp_client = MCPGatewayClient(config.get("mcp_gateway_url"))

    def execute_federated(self, sql_queries: dict) -> dict:
        """
        Exécuter les requêtes SQL sur plusieurs bases de données.
        
        Exécute chaque requête SQL sur sa base de données cible
        et retourne les résultats ou les erreurs.
        
        @param sql_queries: Dictionnaire contenant les requêtes SQL
        @type sql_queries: dict
        @param sql_queries format:
            - database_name (str): {
                - query (str): Requête SQL à exécuter
                - params (list): Paramètres pour la requête préparée
            }
        @return: Résultats d'exécution pour chaque base de données
        @rtype: dict
        @return_value:
            - database_name (str): {
                - success (bool): Indique si l'exécution a réussi
                - data (list): Données retournées par la requête
                - rows (int): Nombre de lignes retournées
                - error (str): Message d'erreur si l'exécution a échoué
            }
        """
        results = {}
        
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        
        for db, query_info in sql_queries.items():
            try:
                result = loop.run_until_complete(self._execute_via_mcp(db, query_info))
                results[db] = {
                    "success": True,
                    "data": result,
                    "rows": len(result) if isinstance(result, list) else 0
                }
            except Exception as e:
                results[db] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results

    async def _execute_via_mcp(self, database: str, query_info: dict) -> list:
        """
        Exécuter une requête sur une base de données via la passerelle MCP.
        
        @param database: Nom de la base de données cible
        @type database: str
        @param query_info: Dictionnaire contenant la requête et ses paramètres
        @type query_info: dict
        @param query_info keys:
            - query (str): Requête SQL à exécuter
            - params (list): Paramètres pour la requête
        @return: Résultats de la requête
        @rtype: list
        @raise Exception: En cas d'échec de l'exécution via MCP
        """
        query = query_info.get("query", "")
        
        try:
            # Appeler l'outil execute_sql sur le serveur MCP
            response = await self.mcp_client.call_tool(
                tool="execute_sql",
                arguments={"sql": query},
                server=database
            )
            
            if response.get("success"):
                result = response.get("result", [])
                if result and len(result) > 0:
                    # Extraire le contenu textuel de la réponse MCP
                    text = result[0].get("text", "")
                    # Le serveur MCP retourne les résultats en tant que texte
                    return [{"result": text}]
                return []
            else:
                raise Exception(f"MCP query failed: {response.get('error', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Failed to execute query via MCP: {str(e)}")
        finally:
            await self.mcp_client.disconnect()
