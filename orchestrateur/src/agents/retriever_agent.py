"""
Schema retrieval agent for fetching database schemas via MCP.

Ce module implémente l'agent de récupération de schémas qui interroge
les serveurs MCP pour obtenir les structures de bases de données
et les informations sur les tables et colonnes.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from src.agents.base_agent import BaseAgent
from src.mcp_client import MCPGatewayClient
import asyncio
import json
import re


class RetrieverAgent(BaseAgent):
    """
    Agent de récupération de schémas de base de données.
    
    Utilise la passerelle MCP pour interroger les serveurs MCP
    et récupérer les informations de schéma des bases de données.
    """
    
    def __init__(self, config: dict):
        """
        Initialiser l'agent de récupération.
        
        @param config: Configuration contenant l'URL de la passerelle MCP
        @type config: dict
        """
        super().__init__(config)
        self.mcp_client = MCPGatewayClient(config.get("mcp_gateway_url"))
    
    def run(self, intent: dict) -> list:
        """
        Récupérer les schémas de base de données pertinents.
        
        Utilise les informations d'intention pour déterminer quelles
        bases de données consulter, puis récupère leurs schémas via MCP.
        
        @param intent: Dictionnaire contenant les informations d'intention
        @type intent: dict
        @param intent['databases']: Liste des bases de données cibles
        @type intent['databases']: list
        @return: Liste des schémas de base de données avec tables et colonnes
        @rtype: list of dict
        @return_value:
            - database (str): Nom de la base de données
            - tables (list): Liste des noms de tables
            - columns (dict): Mapping table_name -> list of columns
            - schema (dict): Information complète du schéma
        """
        databases = intent.get("databases", [])
        
        schemas = []
        for db in databases:
            if db == "postgres":
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                schema_info = loop.run_until_complete(self._get_schema_from_mcp(db))
                schemas.append({
                    "database": db,
                    "tables": schema_info.get("tables", []),
                    "columns": schema_info.get("columns", {}),
                    "schema": schema_info
                })
            else:
                schemas.append({
                    "database": db,
                    "tables": [],
                    "columns": {},
                    "schema": "unknown"
                })
        
        return schemas
    
    async def _get_schema_from_mcp(self, database: str) -> dict:
        """
        Récupérer les informations de schéma du serveur MCP.
        
        Appelle les outils MCP pour lister les tables et colonnes
        de la base de données spécifiée.
        
        @param database: Nom de la base de données cible
        @type database: str
        @return: Dictionnaire contenant les informations de schéma
        @rtype: dict
        @return_keys:
            - tables (list): Liste des noms de tables
            - columns (dict): Mapping table_name -> list of columns
            - schema_description (str): Description des tables disponibles
        """
        try:
            # Lister les tables du schéma public
            objects_response = await self.mcp_client.call_tool(
                tool="list_objects",
                arguments={"schema_name": "public", "object_type": "table"},
                server=database
            )
            
            tables = []
            columns_by_table = {}
            
            if objects_response.get("success"):
                result = objects_response.get("result", [])
                if result and len(result) > 0:
                    text = result[0].get("text", "")
                    
                    # Essayer de parser en JSON d'abord
                    try:
                        table_list = json.loads(text)
                        if isinstance(table_list, list):
                            for item in table_list:
                                if isinstance(item, dict) and 'name' in item:
                                    table_name = item['name']
                                    tables.append(table_name)
                                    
                                    # Récupérer les détails de colonne pour chaque table
                                    columns_by_table[table_name] = await self._get_table_columns(database, table_name)
                    except json.JSONDecodeError:
                        # Fallback : parser en tant que texte
                        matches = re.findall(r"'name':\s*'([^']+)'", text)
                        tables = matches if matches else []
                        
                        # Récupérer les colonnes pour chaque table
                        for table_name in tables:
                            columns_by_table[table_name] = await self._get_table_columns(database, table_name)
            
            return {
                "tables": tables,
                "columns": columns_by_table,
                "schema_description": f"Available tables: {', '.join(tables)}"
            }
        except Exception as e:
            return {"tables": [], "columns": {}, "error": str(e)}
        finally:
            await self.mcp_client.disconnect()
    
    async def _get_table_columns(self, database: str, table_name: str) -> list:
        """
        Récupérer les détails des colonnes pour une table spécifique.
        
        Appelle l'outil MCP pour obtenir la définition de la table
        et en extraire les informations de colonne.
        
        @param database: Nom de la base de données
        @type database: str
        @param table_name: Nom de la table
        @type table_name: str
        @return: Liste des colonnes avec leurs propriétés
        @rtype: list of dict
        @return_value:
            - name (str): Nom de la colonne
            - type (str): Type de données SQL
            - nullable (bool): Indique si la colonne accepte NULL
        """
        try:
            details_response = await self.mcp_client.call_tool(
                tool="get_object_details",
                arguments={
                    "schema_name": "public",
                    "object_name": table_name,
                    "object_type": "table"
                },
                server=database
            )
            
            if details_response.get("success"):
                result = details_response.get("result", [])
                if result:
                    text = result[0].get("text", "")
                    
                    # Essayer de parser les informations de colonne
                    columns = []
                    try:
                        # Essayer le parsing JSON
                        col_data = json.loads(text)
                        if isinstance(col_data, list):
                            for col in col_data:
                                if isinstance(col, dict):
                                    columns.append({
                                        "name": col.get("name", ""),
                                        "type": col.get("type", ""),
                                        "nullable": col.get("nullable", True)
                                    })
                    except json.JSONDecodeError:
                        # Fallback : parser en tant que texte
                        for line in text.split("\n"):
                            if "|" in line:
                                parts = [p.strip() for p in line.split("|")]
                                if len(parts) >= 2 and parts[0] and parts[0] != "Column":
                                    columns.append({
                                        "name": parts[0],
                                        "type": parts[1] if len(parts) > 1 else "unknown"
                                    })
                    
                    return columns
        except Exception:
            pass
        
        return []
