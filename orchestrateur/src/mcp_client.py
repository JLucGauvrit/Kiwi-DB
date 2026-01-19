"""
WebSocket client for MCP Gateway communication.

Ce module implémente un client WebSocket pour communiquer avec la passerelle MCP.
Il permet l'envoi de requêtes et la réception de réponses via WebSocket.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
import json
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MCPGatewayClient:
    """
    Client WebSocket pour la communication avec la passerelle MCP.
    
    Établit une connexion WebSocket avec la passerelle MCP et fournit
    des méthodes pour appeler les outils et ressources des serveurs MCP.
    
    @param gateway_url: URL de la passerelle MCP (format: host:port)
    @type gateway_url: str
    
    @ivar gateway_url: URL de la passerelle MCP
    @ivar ws: Connexion WebSocket active (ou None)
    @ivar _lock: Lock pour les opérations asynchrones
    """
    
    def __init__(self, gateway_url: str):
        """
        Initialiser le client de passerelle MCP.
        
        @param gateway_url: URL de la passerelle MCP (avec ou sans ws://)
        @type gateway_url: str
        """
        self.gateway_url = gateway_url.replace("ws://", "")
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """
        Établir une connexion WebSocket avec la passerelle MCP.
        
        @raise Exception: Si la connexion échoue
        """
        try:
            self.ws = await websockets.connect(f"ws://{self.gateway_url}/ws")
            logger.info(f"Connected to MCP Gateway at {self.gateway_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Gateway: {e}")
            raise
    
    async def disconnect(self):
        """Fermer la connexion WebSocket avec la passerelle MCP."""
        if self.ws:
            await self.ws.close()
            self.ws = None
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envoyer une requête à la passerelle MCP et attendre la réponse.
        
        @param request: Dictionnaire de requête à envoyer
        @type request: dict
        @return: Réponse de la passerelle MCP
        @rtype: dict
        @raise Exception: En cas d'erreur lors de la communication
        """
        async with self._lock:
            if not self.ws:
                await self.connect()
            
            try:
                await self.ws.send(json.dumps(request))
                response_text = await self.ws.recv()
                return json.loads(response_text)
            except Exception as e:
                logger.error(f"Error communicating with MCP Gateway: {e}")
                # Essayer de se reconnecter
                await self.disconnect()
                raise
    
    async def list_tools(self, server: str = "postgres") -> Dict[str, Any]:
        """
        Lister les outils disponibles sur le serveur MCP.
        
        @param server: Nom du serveur MCP cible
        @type server: str
        @return: Liste des outils disponibles
        @rtype: dict
        """
        request = {
            "type": "list_tools",
            "server": server
        }
        return await self.send_request(request)
    
    async def call_tool(self, tool: str, arguments: Dict[str, Any], server: str = "postgres") -> Dict[str, Any]:
        """
        Appeler un outil sur le serveur MCP.
        
        @param tool: Nom de l'outil à appeler
        @type tool: str
        @param arguments: Arguments pour l'outil
        @type arguments: dict
        @param server: Nom du serveur MCP cible
        @type server: str
        @return: Résultat de l'appel de l'outil
        @rtype: dict
        """
        request = {
            "type": "call_tool",
            "server": server,
            "tool": tool,
            "arguments": arguments
        }
        return await self.send_request(request)
    
    async def list_resources(self, server: str = "postgres") -> Dict[str, Any]:
        """
        Lister les ressources disponibles sur le serveur MCP.
        
        @param server: Nom du serveur MCP cible
        @type server: str
        @return: Liste des ressources disponibles
        @rtype: dict
        """
        request = {
            "type": "list_resources",
            "server": server
        }
        return await self.send_request(request)
    
    async def get_resource(self, resource: str, server: str = "postgres") -> Dict[str, Any]:
        """
        Récupérer une ressource du serveur MCP.
        
        @param resource: URI de la ressource à récupérer
        @type resource: str
        @param server: Nom du serveur MCP cible
        @type server: str
        @return: Contenu de la ressource
        @rtype: dict
        """
        request = {
            "type": "get_resource",
            "server": server,
            "resource": resource
        }
        return await self.send_request(request)
