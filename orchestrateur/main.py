"""FastAPI server for orchestrator."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator.orchestrator import FederatedRAGOrchestrator
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG Orchestrator")

# Initialize orchestrator
config = {
    "mcp_gateway_url": os.getenv("MCP_GATEWAY_URL", "ws://mcp-gateway:9000"),
    "google_api_key": os.getenv("GOOGLE_API_KEY")
}

orchestrator = FederatedRAGOrchestrator(config)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    result: dict


@app.get("/")
async def root():
    return {"status": "ok", "service": "orchestrator"}


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a federated RAG query."""
    try:
        result = orchestrator.run(request.query)
        return QueryResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
FastAPI server for orchestrator.

Ce module implémente le serveur FastAPI qui orchestre les requêtes RAG fédérées.
Il reçoit les requêtes utilisateur, les traite via l'orchestrateur RAG fédéré,
et retourne les résultats synthétisés.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator.orchestrator import FederatedRAGOrchestrator
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG Orchestrator")

# Initialisation de l'orchestrateur avec la configuration depuis les variables d'environnement
config = {
    "mcp_gateway_url": os.getenv("MCP_GATEWAY_URL", "ws://mcp-gateway:9000"),
    "ollama_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
    "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
}

orchestrator = FederatedRAGOrchestrator(config)


class QueryRequest(BaseModel):
    """
    Modèle Pydantic pour les requêtes de requête utilisateur.
    
    @param query: La requête utilisateur en texte libre
    @type query: str
    """
    query: str


class QueryResponse(BaseModel):
    """
    Modèle Pydantic pour les réponses de requête.
    
    @param result: Dictionnaire contenant les résultats de l'orchestration RAG
    @type result: dict
    """
    result: dict


@app.get("/")
async def root():
    """
    Point d'entrée racine du serveur.
    
    @return: Statut du service
    @rtype: dict
    """
    return {"status": "ok", "service": "orchestrator"}


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Traiter une requête RAG fédérée.
    
    Reçoit une requête utilisateur, la traite via l'orchestrateur RAG fédéré
    en passant par les agents d'intention, de récupération, de génération SQL,
    de validation, d'exécution et de composition.
    
    @param request: La requête utilisateur
    @type request: QueryRequest
    @return: Réponse contenant les résultats du traitement RAG
    @rtype: QueryResponse
    @raise HTTPException: En cas d'erreur lors du traitement
    """
    try:
        result = await orchestrator.run_async(request.query)
        return QueryResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """
    Endpoint de vérification de santé du service.
    
    @return: Statut de santé du service
    @rtype: dict
    """
    return {"status": "healthy"}


@app.get("/test-mcp")
async def test_mcp():
    """Test MCP connection without using LLM."""
    from src.mcp_client import MCPGatewayClient
    
    try:
        client = MCPGatewayClient(config["mcp_gateway_url"])
        
        # Test listing tools
        tools_response = await client.list_tools("postgres")
        
        # Test calling describe_schema
        schema_response = await client.call_tool(
            tool="describe_schema",
            arguments={},
            server="postgres"
        )
        
        # Test a simple query
        query_response = await client.call_tool(
            tool="query",
            arguments={"sql": "SELECT current_database(), version();"},
            server="postgres"
        )
        
        await client.disconnect()
        
        return {
            "status": "success",
            "tools": tools_response,
            "schema": schema_response,
            "query": query_response
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
