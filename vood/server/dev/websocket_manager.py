"""
WebSocket connection management for development server.

Manages multiple WebSocket connections and broadcasts updates to all clients.
"""

from typing import Set
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages to all connected clients.
    """

    def __init__(self):
        """Initialize connection manager with empty connection set."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
        """
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients.

        Failed sends (disconnected clients) are handled gracefully.

        Args:
            message: Dictionary to send as JSON to all clients
        """
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection is dead, mark for removal
                disconnected.add(connection)

        # Clean up dead connections
        for connection in disconnected:
            self.disconnect(connection)

    async def send_update(self, html: str, frame_count: int):
        """
        Send a preview update to all connected clients.

        Args:
            html: The updated preview HTML
            frame_count: Number of frames in the animation
        """
        message = {"type": "update", "html": html, "frame_count": frame_count, "error": None}
        await self.broadcast(message)

    async def send_error(self, error: str, traceback: str = ""):
        """
        Send an error message to all connected clients.

        Args:
            error: Error message
            traceback: Optional traceback string
        """
        message = {"type": "error", "error": error, "traceback": traceback}
        await self.broadcast(message)
