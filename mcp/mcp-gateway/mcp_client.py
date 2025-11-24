"""
MCP Client Pool - Manages connections to multiple MCP servers
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for a single MCP server"""

    def __init__(self, name: str, host: str, port: int, server_type: str):
        self.name = name
        self.host = host
        self.port = port
        self.server_type = server_type
        self.session: Optional[ClientSession] = None
        self.read = None
        self.write = None
        self._connected = False

    async def connect(self):
        """Connect to the MCP server"""
        try:
            logger.info(f"Connecting to MCP server '{self.name}' at {self.host}:{self.port}")
            # regarder comment se connecter
            self._connected = True
            logger.info(f"Connected to MCP server '{self.name}'")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{self.name}': {e}")
            self._connected = False
            raise

    async def disconnect(self):
        """Disconnect from the MCP server"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            self._connected = False
            logger.info(f"Disconnected from MCP server '{self.name}'")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server '{self.name}': {e}")

    def is_connected(self) -> bool:
        """Check if connected to the MCP server"""
        return self._connected

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the MCP server"""
        if not self._connected:
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            if self.session:
                result = await self.session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in result.tools
                ]
            else:
                return []
        except Exception as e:
            logger.error(f"Error listing tools from '{self.name}': {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self._connected:
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            if self.session:
                result = await self.session.call_tool(tool_name, arguments)
                return result
            else:
                raise NotImplementedError("Tool calling not implemented for this server type")
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{self.name}': {e}")
            raise

    async def list_resources(self) -> List[Dict[str, Any]]:
        if not self._connected:
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            if self.session:
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
            else:
                return []
        except Exception as e:
            logger.error(f"Error listing resources from '{self.name}': {e}")
            raise

    async def get_resource(self, uri: str) -> Any:
        if not self._connected:
            raise ConnectionError(f"Not connected to MCP server '{self.name}'")

        try:
            if self.session:
                result = await self.session.read_resource(uri)
                return result
            else:
                raise NotImplementedError("Resource reading not implemented for this server type")
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
                    host=config["host"],
                    port=config["port"],
                    server_type=config["type"]
                )
                await client.connect()
                self.clients[name] = client
                logger.info(f"Initialized MCP client for '{name}'")
            except Exception as e:
                logger.error(f"Failed to initialize MCP client for '{name}': {e}")

        logger.info(f"MCP client pool initialized with {len(self.clients)} clients")

    async def close_all(self):
        """Close all MCP client connections"""
        logger.info("Closing all MCP client connections...")

        for name, client in self.clients.items():
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
