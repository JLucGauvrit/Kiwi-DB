"""
MCP Gateway - Routes requests from orchestrator to MCP servers.

Ce module implémente la passerelle MCP qui sert d'intermédiaire entre
l'orchestrateur et les serveurs MCP. Elle expose une interface WebSocket
pour recevoir les requêtes et les transmet aux serveurs MCP appropriés.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
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


# Configuration des serveurs MCP disponibles
MCP_SERVERS = {
    "postgres": {
        "url": "http://mcp-postgres:8000/sse",
        "type": "postgres",
        "transport": "sse"
    }
}

mcp_pool: Optional[MCPClientPool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie pour initialiser et nettoyer le pool MCP.
    
    Initialise le pool de clients MCP au démarrage de l'application
    et le ferme à l'arrêt.
    """
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
    """
    Endpoint de vérification de santé du service.
    
    @return: Statut de santé et liste des serveurs disponibles
    @rtype: dict
    """
    return {
        "status": "healthy",
        "servers": list(MCP_SERVERS.keys())
    }


@app.get("/servers")
async def list_servers():
    """
    Lister tous les serveurs MCP disponibles et leur statut de connexion.
    
    @return: Liste des serveurs avec leurs statuts de connexion
    @rtype: dict
    @return_value:
        - servers (list): Liste des serveurs avec:
            - name (str): Nom du serveur
            - type (str): Type de serveur
            - connected (bool): Statut de connexion
    """
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
    Endpoint WebSocket pour l'orchestrateur pour envoyer des requêtes MCP.

    Format de message attendu :
    ```json
    {
        "type": "call_tool" | "list_tools" | "get_resource" | "list_resources",
        "server": "postgres",  # Serveur MCP cible
        "tool": "query",       # Pour call_tool
        "arguments": {},       # Pour call_tool
        "resource": "schema"   # Pour get_resource
    }
    ```
    
    @param websocket: Connexion WebSocket avec l'orchestrateur
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
    Traiter une requête entrante et la router vers le serveur MCP approprié.
    
    Routage intelligent des requêtes en fonction du type et du serveur cible.
    Les types de requêtes supportées sont :
    - list_tools : Lister les outils disponibles
    - call_tool : Appeler un outil spécifique
    - list_resources : Lister les ressources disponibles
    - get_resource : Récupérer une ressource spécifique
    
    @param request: Requête à traiter
    @type request: dict
    @return: Réponse formatée pour l'orchestrateur
    @rtype: dict
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
            """
            Traiter une requête list_tools.
            
            @return: Réponse contenant la liste des outils disponibles
            """
            result = await mcp_pool.list_tools(server_name)
            return {
                "success": True,
                "server": server_name,
                "tools": result
            }

        elif request_type == "call_tool":
            """
            Traiter une requête call_tool.
            
            Requiert les champs supplémentaires :
            - tool (str): Nom de l'outil à appeler
            - arguments (dict): Arguments de l'outil
            
            @return: Réponse contenant le résultat de l'appel de l'outil
            """
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
            """
            Traiter une requête list_resources.
            
            @return: Réponse contenant la liste des ressources disponibles
            """
            result = await mcp_pool.list_resources(server_name)
            return {
                "success": True,
                "server": server_name,
                "resources": result
            }

        elif request_type == "get_resource":
            """
            Traiter une requête get_resource.
            
            Requiert le champ supplémentaire :
            - resource (str): URI de la ressource à récupérer
            
            @return: Réponse contenant le contenu de la ressource
            """
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
