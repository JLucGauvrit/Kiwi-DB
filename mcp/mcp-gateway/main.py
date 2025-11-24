"""
MCP Gateway - Routes requests from orchestrator to MCP servers
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from mcp_client import MCPClientPool


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


MCP_SERVERS = {
    "postgres": {
        "host": "mcp-postgres",
        "port": 7000,
        "type": "postgres"
    }
}

mcp_pool: Optional[MCPClientPool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup MCP client pool"""
    global mcp_pool
    logger.info("Initializing MCP Gateway...")
    mcp_pool = MCPClientPool(MCP_SERVERS)
    await mcp_pool.initialize()
    logger.info("MCP Gateway initialized successfully")

    yield

    logger.info("Shutting down MCP Gateway...")
    await mcp_pool.close_all()
    logger.info("MCP Gateway shutdown complete")


app = FastAPI(title="MCP Gateway", lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "servers": list(MCP_SERVERS.keys())
    }


@app.get("/servers")
async def list_servers():
    """List available MCP servers"""
    if not mcp_pool:
        return {"servers": []}

    return {
        "servers": [
            {
                "name": name,
                "type": config["type"],
                "connected": await mcp_pool.is_connected(name)
            }
            for name, config in MCP_SERVERS.items()
        ]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for orchestrator to send MCP requests

    Expected message format:
    {
        "type": "call_tool" | "list_tools" | "get_resource" | "list_resources",
        "server": "postgres",  # Target MCP server
        "tool": "query",       # For call_tool
        "arguments": {},       # For call_tool
        "resource": "schema"   # For get_resource
    }
    """
    await websocket.accept()
    logger.info("Orchestrator connected via WebSocket")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received request: {data}")

            try:
                request = json.loads(data)
                if "type" not in request:
                    await websocket.send_json({
                        "error": "Missing 'type' field in request"
                    })
                    continue

                if "server" not in request:
                    await websocket.send_json({
                        "error": "Missing 'server' field in request"
                    })
                    continue

                response = await handle_request(request)

                await websocket.send_json(response)
                logger.info(f"Sent response: {response}")

            except json.JSONDecodeError:
                await websocket.send_json({
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                await websocket.send_json({
                    "error": str(e)
                })

    except WebSocketDisconnect:
        logger.info("Orchestrator disconnected")


async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming request and route to appropriate MCP server
    """
    if not mcp_pool:
        return {"error": "MCP pool not initialized"}

    request_type = request["type"]
    server_name = request["server"]

    if server_name not in MCP_SERVERS:
        return {
            "error": f"Unknown server: {server_name}",
            "available_servers": list(MCP_SERVERS.keys())
        }

    try:
        if request_type == "list_tools":
            result = await mcp_pool.list_tools(server_name)
            return {
                "success": True,
                "server": server_name,
                "tools": result
            }

        elif request_type == "call_tool":
            # Call a specific tool on the MCP server
            if "tool" not in request:
                return {"error": "Missing 'tool' field for call_tool request"}

            tool_name = request["tool"]
            arguments = request.get("arguments", {})

            result = await mcp_pool.call_tool(
                server_name,
                tool_name,
                arguments
            )
            return {
                "success": True,
                "server": server_name,
                "tool": tool_name,
                "result": result
            }

        elif request_type == "list_resources":
            result = await mcp_pool.list_resources(server_name)
            return {
                "success": True,
                "server": server_name,
                "resources": result
            }

        elif request_type == "get_resource":
            if "resource" not in request:
                return {"error": "Missing 'resource' field for get_resource request"}

            resource_uri = request["resource"]
            result = await mcp_pool.get_resource(server_name, resource_uri)
            return {
                "success": True,
                "server": server_name,
                "resource": resource_uri,
                "result": result
            }

        else:
            return {
                "error": f"Unknown request type: {request_type}",
                "supported_types": ["list_tools", "call_tool", "list_resources", "get_resource"]
            }

    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        return {
            "error": str(e),
            "server": server_name,
            "type": request_type
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
