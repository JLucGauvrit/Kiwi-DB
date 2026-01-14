"""SQL generation agent."""
from src.agents.base_agent import BaseAgent


class SQLAgent(BaseAgent):
    def run(self, intent: dict, schemas: list) -> dict:
        """Generate SQL queries for each database."""
        
        # Check if database access is needed
        if not intent.get("requires_database", True):
            return {}
        
        # Build schema context
        schema_context = self._build_schema_context(schemas)
        
        if not schema_context:
            return {}
        
        entities = intent.get("entities", [])
        reason = intent.get("reason", "")
        intent_type = intent.get("intent_type", "search")
        
        # Try LLM-based generation first
        try:
            return self._generate_with_llm(reason, entities, schema_context, schemas)
        except Exception as e:
            # Fallback to rule-based generation
            return self._generate_rule_based(entities, intent_type, schemas)
    
    def _generate_with_llm(self, reason: str, entities: list, schema_context: str, schemas: list) -> dict:
        """Generate SQL using LLM."""
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
        
        # Clean up the response
        sql_query = response.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.split("```")[1].split("```")[0].strip()
        
        # Check if query is invalid
        if "NO_MATCH" in sql_query or "NULL" in sql_query.upper() or not sql_query or len(sql_query) < 10:
            return {}
        
        # Generate SQL for each schema
        sql_queries = {}
        for schema in schemas:
            db = schema["database"]
            sql_queries[db] = {
                "query": sql_query,
                "params": []
            }
        
        return sql_queries
    
    def _generate_rule_based(self, entities: list, intent_type: str, schemas: list) -> dict:
        """Generate SQL using simple rules (fallback when LLM fails)."""
        sql_queries = {}
        
        for schema in schemas:
            db = schema["database"]
            tables = schema.get("tables", [])
            
            if not tables:
                continue
            
            # Try to match entities to table names
            matched_table = None
            for entity in entities:
                entity_lower = entity.lower()
                for table in tables:
                    if entity_lower in table.lower() or table.lower() in entity_lower:
                        matched_table = table
                        break
                if matched_table:
                    break
            
            # If no match, use first table
            if not matched_table and tables:
                matched_table = tables[0]
            
            if matched_table:
                # Generate simple query based on intent type
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
        """Build a formatted schema context for the LLM."""
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
        
        # If we have tables but no column details, still provide table names
        if not context_parts:
            return ""
        
        return "\n".join(context_parts)
