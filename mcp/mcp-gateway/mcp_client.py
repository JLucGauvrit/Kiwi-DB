"""
MCP Client Pool - Manages connections to multiple MCP servers (Version 2 - Sans AsyncExitStack)
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for a single MCP server"""

    def __init__(self, name: str, url: str, server_type: str, transport: str = "sse"):
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
        """Maintain the SSE connection in a background task"""
        try:
            logger.info(f"Starting connection task for '{self.name}' at {self.url}")

            async with sse_client(self.url) as (read, write):
                logger.info(f"SSE connection established for '{self.name}'")

                async with ClientSession(read, write) as session:
                    logger.info(f"MCP ClientSession created for '{self.name}'")

                    self.session = session

                    # Initialize the session
                    init_result = await session.initialize()
                    logger.info(
                        f"MCP session initialized for '{self.name}' - "
                        f"Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}"
                    )

                    self._connected = True

                    # Keep the connection alive indefinitely
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
        """Connect to the MCP server via SSE"""
        try:
            if self.transport != "sse":
                raise ValueError(f"Unsupported transport: {self.transport}")

            # Start the connection maintenance task
            self._connection_task = asyncio.create_task(self._maintain_connection())

            # Wait a bit for the connection to be established
            for _ in range(50):  # Wait up to 5 seconds
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
        """Disconnect from the MCP server"""
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
        """Check if connected to the MCP server"""
        return self._connected and self.session is not None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the MCP server"""
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
        """Call a tool on the MCP server"""
        if not self.is_connected():
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{self.name}': {e}")
            raise

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources on the MCP server"""
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
        """Get a resource from the MCP server"""
        if not self.is_connected():
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            result = await self.session.read_resource(uri)
            return result
        except Exception as e:
            logger.error(f"Error reading resource '{uri}' from '{self.name}': {e}")
            raise


class MCPClientPool:
    """Pool of MCP clients for managing multiple server connections"""

    def __init__(self, servers_config: Dict[str, Dict[str, Any]]):
        self.servers_config = servers_config
        self.clients: Dict[str, MCPClient] = {}

    async def initialize(self):
        """Initialize all MCP client connections"""
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
                # Don't raise, continue with other servers

        if self.clients:
            logger.info(f"MCP client pool initialized with {len(self.clients)} client(s)")
        else:
            logger.warning("MCP client pool initialized but no clients connected!")

    async def close_all(self):
        """Close all MCP client connections"""
        logger.info("Closing all MCP client connections...")

        for name, client in list(self.clients.items()):
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error closing client '{name}': {e}")

        self.clients.clear()
        logger.info("All MCP client connections closed")

    async def is_connected(self, server_name: str) -> bool:
        """Check if a specific server is connected"""
        if server_name not in self.clients:
            return False
        return self.clients[server_name].is_connected()

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List tools from a specific MCP server"""
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].list_tools()

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on a specific MCP server"""
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].call_tool(tool_name, arguments)

    async def list_resources(self, server_name: str) -> List[Dict[str, Any]]:
        """List resources from a specific MCP server"""
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].list_resources()

    async def get_resource(self, server_name: str, uri: str) -> Any:
        """Get a resource from a specific MCP server"""
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")

        return await self.clients[server_name].get_resource(uri)
