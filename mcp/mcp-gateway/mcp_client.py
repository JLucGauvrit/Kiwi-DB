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
    """Client for a single MCP server.

    Supports two connection modes:
    - persistent: maintains a long-lived SSE connection (good for stable servers)
    - per_request: opens a fresh connection for each operation (good for supergateway-wrapped servers)
    """

    def __init__(self, name: str, url: str, server_type: str, transport: str = "sse", per_request: bool = False):
        self.name = name
        self.url = url
        self.server_type = server_type
        self.transport = transport
        self.per_request = per_request
        self.session: Optional[ClientSession] = None
        self._connected = False
        self._connection_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------ #
    #  Persistent mode helpers                                             #
    # ------------------------------------------------------------------ #

    async def _maintain_connection(self):
        """Maintain the SSE connection in a background task, with auto-reconnect."""
        retry_delay = 5
        while True:
            try:
                logger.info(f"Starting connection task for '{self.name}' at {self.url}")
                async with sse_client(self.url) as (read, write):
                    async with ClientSession(read, write) as session:
                        self.session = session
                        init_result = await session.initialize()
                        logger.info(
                            f"MCP session initialized for '{self.name}' - "
                            f"Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}"
                        )
                        self._connected = True
                        retry_delay = 5
                        await asyncio.Event().wait()
            except asyncio.CancelledError:
                self._connected = False
                self.session = None
                raise
            except Exception as e:
                self._connected = False
                self.session = None
                logger.warning(f"Connection to '{self.name}' lost: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

    async def connect(self):
        """Establish connection (persistent mode only)."""
        if self.per_request:
            self._connected = True
            logger.info(f"'{self.name}' configured in per-request mode")
            return
        try:
            self._connection_task = asyncio.create_task(self._maintain_connection())
            for _ in range(300):
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
        """Disconnect from the MCP server."""
        self._connected = False
        self.session = None
        if self._connection_task:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass
            self._connection_task = None
        logger.info(f"Disconnected from MCP server '{self.name}'")

    def is_connected(self) -> bool:
        if self.per_request:
            return True
        return self._connected and self.session is not None

    # ------------------------------------------------------------------ #
    #  Per-request connection helper                                       #
    # ------------------------------------------------------------------ #

    async def _run_with_fresh_session(self, fn):
        """Open a fresh SSE connection, run fn(session), return result."""
        try:
            async with sse_client(self.url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await fn(session)
        except BaseException as e:
            # Unwrap ExceptionGroup (Python 3.11 / anyio TaskGroup errors)
            inner = e
            if hasattr(e, "exceptions"):
                inner = e.exceptions[0]
            logger.error(f"[{self.name}] SSE session error: {type(inner).__name__}: {inner}", exc_info=True)
            raise

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def list_tools(self) -> List[Dict[str, Any]]:
        async def _list(session):
            result = await session.list_tools()
            return [
                {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                for t in result.tools
            ]
        try:
            if self.per_request:
                return await self._run_with_fresh_session(_list)
            if not self.is_connected():
                raise ConnectionError(f"Not connected to MCP server '{self.name}'")
            return await _list(self.session)
        except Exception as e:
            logger.error(f"Error listing tools from '{self.name}': {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        async def _call(session):
            result = await session.call_tool(tool_name, arguments)
            return [
                {"type": c.type, "text": c.text if hasattr(c, "text") else None}
                for c in result.content
            ]
        try:
            if self.per_request:
                return await self._run_with_fresh_session(_call)
            if not self.is_connected():
                raise ConnectionError(f"Not connected to MCP server '{self.name}'")
            return await _call(self.session)
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{self.name}': {e}")
            raise

    async def list_resources(self) -> List[Dict[str, Any]]:
        async def _list(session):
            result = await session.list_resources()
            return [
                {"uri": r.uri, "name": r.name, "description": r.description, "mimeType": r.mimeType}
                for r in result.resources
            ]
        try:
            if self.per_request:
                return await self._run_with_fresh_session(_list)
            if not self.is_connected():
                raise ConnectionError(f"Not connected to MCP server '{self.name}'")
            return await _list(self.session)
        except Exception as e:
            logger.error(f"Error listing resources from '{self.name}': {e}")
            raise

    async def get_resource(self, uri: str) -> Any:
        async def _get(session):
            return await session.read_resource(uri)
        try:
            if self.per_request:
                return await self._run_with_fresh_session(_get)
            if not self.is_connected():
                raise ConnectionError(f"Not connected to MCP server '{self.name}'")
            return await _get(self.session)
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
                    transport=config.get("transport", "sse"),
                    per_request=config.get("per_request", False)
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
