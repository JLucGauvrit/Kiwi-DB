"""
MCP Client Pool - Manages connections to multiple MCP servers.

Ce module implémente un pool de clients MCP pour gérer les connexions
à plusieurs serveurs MCP via le transport SSE (Server-Sent Events).

@author: PROCOM Team
@version: 2.0
@since: 2026-01-19
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client pour une connexion unique à un serveur MCP.
    
    Gère la connexion SSE et la session MCP pour un serveur MCP spécifique.
    Maintient la connexion alive dans une tâche de fond.
    
    @param name: Nom identifiant le serveur MCP
    @type name: str
    @param url: URL du serveur MCP
    @type url: str
    @param server_type: Type de serveur (ex: "postgres")
    @type server_type: str
    @param transport: Type de transport ("sse" par défaut)
    @type transport: str
    
    @ivar name: Nom du serveur
    @ivar url: URL du serveur
    @ivar server_type: Type de serveur
    @ivar transport: Type de transport utilisé
    @ivar session: Session MCP active
    @ivar _connected: Statut de connexion
    @ivar _connection_task: Tâche asynchrone de maintien de connexion
    """

    def __init__(self, name: str, url: str, server_type: str, transport: str = "sse"):
        """
        Initialiser le client MCP.
        
        @param name: Identifiant unique du client
        @param url: URL du serveur MCP
        @param server_type: Type de serveur (ex: "postgres")
        @param transport: Protocole de transport ("sse" par défaut)
        """
        self.name = name
        self.url = url
        self.server_type = server_type
        self.transport = transport
        self.session: Optional[ClientSession] = None
        self._connected = False
        self._sse_context = None
        self._session_context = None
        self._connection_task: Optional[asyncio.Task] = None

    async def _maintain_connection(self):
        """
        Maintenir la connexion SSE dans une tâche de fond.
        
        Établit et maintient une connexion SSE avec le serveur MCP,
        en créant une session MCP et en la gardant active indéfiniment.
        
        @raise asyncio.CancelledError: Si la tâche est annulée
        @raise Exception: En cas d'erreur lors de la connexion
        """
        try:
            logger.info(f"Starting connection task for '{self.name}' at {self.url}")

            async with sse_client(self.url) as (read, write):
                logger.info(f"SSE connection established for '{self.name}'")

                async with ClientSession(read, write) as session:
                    logger.info(f"MCP ClientSession created for '{self.name}'")

                    self.session = session

                    # Initialiser la session
                    init_result = await session.initialize()
                    logger.info(
                        f"MCP session initialized for '{self.name}' - "
                        f"Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}"
                    )

                    self._connected = True

                    # Garder la connexion vivante indéfiniment
                    await asyncio.Event().wait()

        except asyncio.CancelledError:
            logger.info(f"Connection task cancelled for '{self.name}'")
            raise
        except Exception as e:
            logger.error(f"Connection task failed for '{self.name}': {e}", exc_info=True)
            raise
        finally:
            self._connected = False
            self.session = None

    async def connect(self):
        """
        Établir une connexion au serveur MCP via SSE.
        
        Lance une tâche de fond qui maintient la connexion SSE
        et attend que la connexion soit établie.
        
        @raise TimeoutError: Si la connexion n'est pas établie dans le délai imparti
        @raise Exception: En cas d'erreur lors de la connexion
        """
        try:
            if self.transport != "sse":
                raise ValueError(f"Unsupported transport: {self.transport}")

            # Lancer la tâche de maintien de connexion
            self._connection_task = asyncio.create_task(self._maintain_connection())

            # Attendre un peu pour que la connexion soit établie
            for _ in range(300):  # Attendre jusqu'à 30 secondes
                if self._connected:
                    logger.info(f"Successfully connected to MCP server '{self.name}'")
                    return
                await asyncio.sleep(0.1)

            raise TimeoutError(f"Timeout connecting to MCP server '{self.name}'")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{self.name}': {e}")
            if self._connection_task:
                self._connection_task.cancel()
                try:
                    await self._connection_task
                except asyncio.CancelledError:
                    pass
            raise

    async def disconnect(self):
        """
        Déconnecter du serveur MCP.
        
        Annule la tâche de maintien de connexion et ferme la session.
        """
        try:
            self._connected = False
            if self._connection_task:
                self._connection_task.cancel()
                try:
                    await self._connection_task
                except asyncio.CancelledError:
                    pass
                self._connection_task = None
            self.session = None
            logger.info(f"Disconnected from MCP server '{self.name}'")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server '{self.name}': {e}")

    def is_connected(self) -> bool:
        """
        Vérifier si le client est connecté au serveur MCP.
        
        @return: True si connecté, False sinon
        @rtype: bool
        """
        return self._connected and self.session is not None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lister les outils disponibles sur le serveur MCP.
        
        @return: Liste des outils avec leurs descriptions et schémas
        @rtype: list of dict
        @return_keys:
            - name (str): Nom de l'outil
            - description (str): Description de l'outil
            - inputSchema (dict): Schéma des paramètres d'entrée
        @raise ConnectionError: Si le client n'est pas connecté
        """
        if not self.is_connected():
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            result = await self.session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in result.tools
            ]
        except Exception as e:
            logger.error(f"Error listing tools from '{self.name}': {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Appeler un outil sur le serveur MCP.
        
        @param tool_name: Nom de l'outil à appeler
        @type tool_name: str
        @param arguments: Arguments à passer à l'outil
        @type arguments: dict
        @return: Résultat de l'appel de l'outil
        @rtype: list of dict
        @return_value:
            - type (str): Type de contenu
            - text (str): Contenu textuel de la réponse
        @raise ConnectionError: Si le client n'est pas connecté
        """
        if not self.is_connected():
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            result = await self.session.call_tool(tool_name, arguments)
            # Extraire le contenu de CallToolResult
            return [
                {
                    "type": content.type,
                    "text": content.text if hasattr(content, "text") else None,
                }
                for content in result.content
            ]
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{self.name}': {e}")
            raise

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        Lister les ressources disponibles sur le serveur MCP.
        
        @return: Liste des ressources disponibles
        @rtype: list of dict
        @return_keys:
            - uri (str): URI de la ressource
            - name (str): Nom de la ressource
            - description (str): Description de la ressource
            - mimeType (str): Type MIME de la ressource
        @raise ConnectionError: Si le client n'est pas connecté
        """
        if not self.is_connected():
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            result = await self.session.list_resources()
            return [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                }
                for resource in result.resources
            ]
        except Exception as e:
            logger.error(f"Error listing resources from '{self.name}': {e}")
            raise

    async def get_resource(self, uri: str) -> Any:
        """
        Récupérer une ressource du serveur MCP.
        
        @param uri: URI de la ressource à récupérer
        @type uri: str
        @return: Contenu de la ressource
        @raise ConnectionError: Si le client n'est pas connecté
        """
        if not self.is_connected():
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            result = await self.session.read_resource(uri)
            return result
        except Exception as e:
            logger.error(f"Error reading resource '{uri}' from '{self.name}': {e}")
            raise


class MCPClientPool:
    """
    Pool de clients MCP pour gérer les connexions à plusieurs serveurs.
    
    Gère un ensemble de clients MCP et fournit des méthodes pour
    interagir avec tous les serveurs via une interface unifiée.
    
    @param servers_config: Configuration des serveurs MCP
    @type servers_config: dict of (str -> dict)
    
    @ivar servers_config: Configuration stockée des serveurs
    @ivar clients: Dictionnaire des clients MCP connectés
    """

    def __init__(self, servers_config: Dict[str, Dict[str, Any]]):
        """
        Initialiser le pool de clients MCP.
        
        @param servers_config: Configuration de chaque serveur MCP
        @type servers_config: dict
        """
        self.servers_config = servers_config
        self.clients: Dict[str, MCPClient] = {}

    async def initialize(self):
        """
        Initialiser les connexions à tous les serveurs MCP.
        
        Crée et connecte un client pour chaque serveur configuré.
        Les erreurs de connexion n'arrêtent pas le processus,
        permettant une initialisation partielle.
        """
        logger.info("Initializing MCP client pool...")

        for name, config in self.servers_config.items():
            try:
                client = MCPClient(
                    name=name,
                    url=config["url"],
                    server_type=config["type"],
                    transport=config.get("transport", "sse")
                )
                await client.connect()
                self.clients[name] = client
                logger.info(f"✓ Initialized MCP client for '{name}'")
            except Exception as e:
                logger.error(f"✗ Failed to initialize MCP client for '{name}': {e}")
                # Ne pas lever, continuer avec les autres serveurs

        if self.clients:
            logger.info(f"MCP client pool initialized with {len(self.clients)} client(s)")
        else:
            logger.warning("MCP client pool initialized but no clients connected!")

    async def close_all(self):
        """
        Fermer toutes les connexions des clients MCP.
        """
        logger.info("Closing all MCP client connections...")

        for name, client in list(self.clients.items()):
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error closing client '{name}': {e}")

        self.clients.clear()
        logger.info("All MCP client connections closed")

    async def is_connected(self, server_name: str) -> bool:
        """
        Vérifier si un serveur spécifique est connecté.
        
        @param server_name: Nom du serveur MCP
        @type server_name: str
        @return: True si le serveur est connecté, False sinon
        @rtype: bool
        """
        if server_name not in self.clients:
            return False
        return self.clients[server_name].is_connected()

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Lister les outils d'un serveur MCP spécifique.
        
        @param server_name: Nom du serveur MCP
        @type server_name: str
        @return: Liste des outils disponibles
        @rtype: list of dict
        @raise ValueError: Si le serveur n'existe pas
        """
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].list_tools()

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Appeler un outil sur un serveur MCP spécifique.
        
        @param server_name: Nom du serveur MCP
        @type server_name: str
        @param tool_name: Nom de l'outil à appeler
        @type tool_name: str
        @param arguments: Arguments pour l'outil
        @type arguments: dict
        @return: Résultat de l'appel de l'outil
        @raise ValueError: Si le serveur n'existe pas
        """
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].call_tool(tool_name, arguments)

    async def list_resources(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Lister les ressources d'un serveur MCP spécifique.
        
        @param server_name: Nom du serveur MCP
        @type server_name: str
        @return: Liste des ressources disponibles
        @rtype: list of dict
        @raise ValueError: Si le serveur n'existe pas
        """
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].list_resources()

    async def get_resource(self, server_name: str, uri: str) -> Any:
        """
        Récupérer une ressource d'un serveur MCP spécifique.
        
        @param server_name: Nom du serveur MCP
        @type server_name: str
        @param uri: URI de la ressource
        @type uri: str
        @return: Contenu de la ressource
        @raise ValueError: Si le serveur n'existe pas
        """
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].get_resource(uri)
