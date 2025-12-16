"""WebSocket client for MCP Gateway communication."""
import json
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MCPGatewayClient:
    """Client for communicating with MCP Gateway via WebSocket."""
    
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url.replace("ws://", "")
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """Establish WebSocket connection to MCP Gateway."""
        try:
            self.ws = await websockets.connect(f"ws://{self.gateway_url}/ws")
            logger.info(f"Connected to MCP Gateway at {self.gateway_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Gateway: {e}")
            raise
    
    async def disconnect(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.ws = None
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP Gateway and wait for response."""
        async with self._lock:
            if not self.ws:
                await self.connect()
            
            try:
                await self.ws.send(json.dumps(request))
                response_text = await self.ws.recv()
                return json.loads(response_text)
            except Exception as e:
                logger.error(f"Error communicating with MCP Gateway: {e}")
                # Try to reconnect
                await self.disconnect()
                raise
    
    async def list_tools(self, server: str = "postgres") -> Dict[str, Any]:
        """List available tools from MCP server."""
        request = {
            "type": "list_tools",
            "server": server
        }
        return await self.send_request(request)
    
    async def call_tool(self, tool: str, arguments: Dict[str, Any], server: str = "postgres") -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        request = {
            "type": "call_tool",
            "server": server,
            "tool": tool,
            "arguments": arguments
        }
        return await self.send_request(request)
    
    async def list_resources(self, server: str = "postgres") -> Dict[str, Any]:
        """List available resources from MCP server."""
        request = {
            "type": "list_resources",
            "server": server
        }
        return await self.send_request(request)
    
    async def get_resource(self, resource: str, server: str = "postgres") -> Dict[str, Any]:
        """Get a resource from the MCP server."""
        request = {
            "type": "get_resource",
            "server": server,
            "resource": resource
        }
        return await self.send_request(request)
