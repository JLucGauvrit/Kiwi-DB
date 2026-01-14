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
    "ollama_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
    "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
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
        result = await orchestrator.run_async(request.query)
        return QueryResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
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
