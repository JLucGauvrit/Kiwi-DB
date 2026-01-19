"""
SQL generation agent for creating database queries.

Ce module implémente l'agent de génération SQL qui génère les requêtes SQL
basées sur l'intention de l'utilisateur et les schémas de base de données
disponibles. Il utilise un modèle de langage pour la génération intelligente
avec un fallback sur une génération par règles.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from src.agents.base_agent import BaseAgent


class SQLAgent(BaseAgent):
    """
    Agent de génération de requêtes SQL.
    
    Génère des requêtes SQL valides basées sur l'intention utilisateur
    et les schémas de base de données disponibles. Essaie d'abord une
    génération basée sur le modèle de langage, avec un fallback sur
    une génération par règles simples.
    """
    
    def run(self, intent: dict, schemas: list) -> dict:
        """
        Générer les requêtes SQL pour chaque base de données.
        
        @param intent: Dictionnaire contenant les informations d'intention
        @type intent: dict
        @param intent['requires_database']: Si l'accès à la base est nécessaire
        @param intent['entities']: Entités mentionnées dans la requête
        @param intent['reason']: Raison de la classification
        @param intent['intent_type']: Type d'intention (search, aggregate, etc.)
        @param schemas: Liste des schémas de base de données disponibles
        @type schemas: list
        @return: Dictionnaire contenant les requêtes SQL générées
        @rtype: dict
        @return_value:
            - database_name (str): {
                - query (str): Requête SQL valide
                - params (list): Paramètres pour la requête préparée
            }
        """
        
        # Vérifier si l'accès à la base de données est nécessaire
        if not intent.get("requires_database", True):
            return {}
        
        # Construire le contexte de schéma
        schema_context = self._build_schema_context(schemas)
        
        if not schema_context:
            return {}
        
        entities = intent.get("entities", [])
        reason = intent.get("reason", "")
        intent_type = intent.get("intent_type", "search")
        
        # Essayer la génération basée sur le modèle de langage d'abord
        try:
            return self._generate_with_llm(reason, entities, schema_context, schemas)
        except Exception as e:
            # Fallback : génération basée sur les règles
            return self._generate_rule_based(entities, intent_type, schemas)
    
    def _generate_with_llm(self, reason: str, entities: list, schema_context: str, schemas: list) -> dict:
        """
        Générer les requêtes SQL en utilisant le modèle de langage.
        
        @param reason: Raison de la requête (description de l'intention)
        @type reason: str
        @param entities: Entités mentionnées par l'utilisateur
        @type entities: list
        @param schema_context: Contexte du schéma formaté pour le LLM
        @type schema_context: str
        @param schemas: Schémas de base de données disponibles
        @type schemas: list
        @return: Dictionnaire des requêtes SQL générées
        @rtype: dict
        """
        prompt = f"""You are a SQL query generator. Generate a PostgreSQL query based on the user's request.

USER REQUEST: {reason}
ENTITIES MENTIONED: {entities}

AVAILABLE DATABASE SCHEMA:
{schema_context}

RULES:
1. ONLY use tables and columns from the schema above
2. If the requested data doesn't match any available tables/columns, return: NO_MATCH
3. Generate a valid PostgreSQL SELECT query
4. Use appropriate WHERE, JOIN, and LIMIT clauses
5. Return ONLY the SQL query, nothing else

SQL Query:"""
        
        response = self.invoke(prompt)
        
        # Nettoyer la réponse
        sql_query = response.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.split("```")[1].split("```")[0].strip()
        
        # Vérifier si la requête est invalide
        if "NO_MATCH" in sql_query or "NULL" in sql_query.upper() or not sql_query or len(sql_query) < 10:
            return {}
        
        # Générer SQL pour chaque schéma
        sql_queries = {}
        for schema in schemas:
            db = schema["database"]
            sql_queries[db] = {
                "query": sql_query,
                "params": []
            }
        
        return sql_queries
    
    def _generate_rule_based(self, entities: list, intent_type: str, schemas: list) -> dict:
        """
        Générer les requêtes SQL en utilisant des règles simples.
        
        Fallback utilisé quand la génération par LLM échoue.
        Utilise une correspondance simple entre les entités et les noms de tables.
        
        @param entities: Entités mentionnées par l'utilisateur
        @type entities: list
        @param intent_type: Type d'intention (search, aggregate, etc.)
        @type intent_type: str
        @param schemas: Schémas de base de données disponibles
        @type schemas: list
        @return: Dictionnaire des requêtes SQL générées
        @rtype: dict
        """
        sql_queries = {}
        
        for schema in schemas:
            db = schema["database"]
            tables = schema.get("tables", [])
            
            if not tables:
                continue
            
            # Essayer de faire correspondre les entités aux noms de tables
            matched_table = None
            for entity in entities:
                entity_lower = entity.lower()
                for table in tables:
                    if entity_lower in table.lower() or table.lower() in entity_lower:
                        matched_table = table
                        break
                if matched_table:
                    break
            
            # Si pas de correspondance, utiliser la première table
            if not matched_table and tables:
                matched_table = tables[0]
            
            if matched_table:
                # Générer une requête simple basée sur le type d'intention
                if intent_type == "aggregate":
                    query = f"SELECT COUNT(*) as count FROM {matched_table};"
                else:
                    query = f"SELECT * FROM {matched_table} LIMIT 10;"
                
                sql_queries[db] = {
                    "query": query,
                    "params": []
                }
        
        return sql_queries
    
    def _build_schema_context(self, schemas: list) -> str:
        """
        Construire un contexte de schéma formaté pour le modèle de langage.
        
        Formate les informations de schéma de manière lisible pour aider
        le modèle de langage à générer des requêtes SQL correctes.
        
        @param schemas: Schémas de base de données disponibles
        @type schemas: list
        @return: Contexte du schéma formaté
        @rtype: str
        """
        context_parts = []
        
        for schema in schemas:
            db = schema["database"]
            tables = schema.get("tables", [])
            columns = schema.get("columns", {})
            
            if not tables:
                continue
            
            context_parts.append(f"Database: {db}")
            context_parts.append(f"Available Tables: {', '.join(tables)}")
            
            for table in tables:
                if table in columns and columns[table]:
                    context_parts.append(f"\nTable '{table}' columns:")
                    for col in columns[table]:
                        col_name = col.get("name", "")
                        col_type = col.get("type", "")
                        context_parts.append(f"  - {col_name} ({col_type})")
        
        # Si nous avons des tables mais pas de détails de colonnes, fournir les noms de tables
        if not context_parts:
            return ""
        
        return "\n".join(context_parts)
