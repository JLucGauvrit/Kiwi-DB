"""MCP Gateway - HTTP bridge to database MCP servers."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Dict, Any

app = FastAPI(title="MCP Gateway")


class QueryRequest(BaseModel):
    query: str


class SchemaRequest(BaseModel):
    action: str = "list_tables"


# Database connections configuration
DB_CONFIGS = {
    "postgres": {
        "host": "postgres",
        "port": 5432,
        "database": "dbname",
        "user": "user",
        "password": "password"
    }
}


@app.get("/")
async def root():
    return {"status": "ok", "service": "mcp-gateway"}


@app.post("/postgres/schema")
async def get_postgres_schema(request: SchemaRequest):
    """Get PostgreSQL schema information."""
    try:
        conn = psycopg2.connect(**DB_CONFIGS["postgres"])
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get columns for each table
        table_schemas = {}
        for table in tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            
            columns = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
            table_schemas[table] = columns
        
        cursor.close()
        conn.close()
        
        return {
            "tables": tables,
            "schemas": table_schemas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/postgres/query")
async def execute_postgres_query(request: QueryRequest):
    """Execute query on PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIGS["postgres"])
        cursor = conn.cursor()
        
        cursor.execute(request.query)
        
        # Check if it's a SELECT query
        if request.query.strip().upper().startswith("SELECT"):
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            data = {"affected_rows": cursor.rowcount}
        
        cursor.close()
        conn.close()
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
