"""
WebSocket connection manager for real-time telemetry broadcasting
"""

import json
import logging
from typing import Dict, List, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time data streaming"""
    
    def __init__(self):
        # connections[session_id] = set of websockets
        self.connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a WebSocket connection and add it to the appropriate session group"""
        await websocket.accept()
        
        if session_id not in self.connections:
            self.connections[session_id] = set()
        
        self.connections[session_id].add(websocket)
        logger.info(f"WebSocket connected for session: {session_id}. "
                   f"Total connections: {self.connection_count()}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.connections:
            self.connections[session_id].discard(websocket)
            
            # Clean up empty session groups
            if not self.connections[session_id]:
                del self.connections[session_id]
        
        logger.info(f"WebSocket disconnected for session: {session_id}. "
                   f"Total connections: {self.connection_count()}")
    
    async def broadcast_to_session(self, session_id: str, data: dict):
        """Send data to all WebSockets connected to a specific session"""
        if session_id not in self.connections:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in self.connections[session_id].copy():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected:
            self.connections[session_id].discard(websocket)
    
    async def broadcast_to_all(self, data: dict):
        """Send data to all connected WebSockets (for session_id="all")"""
        await self.broadcast_to_session("all", data)
    
    async def broadcast_telemetry(self, telemetry_data: dict):
        """
        Broadcast telemetry data to appropriate WebSocket connections
        - Send to session-specific connections if session_id exists
        - Always send to "all" connections
        """
        session_id = telemetry_data.get("session_id")
        
        # Send to "all" subscribers
        await self.broadcast_to_all(telemetry_data)
        
        # Send to session-specific subscribers
        if session_id:
            await self.broadcast_to_session(session_id, telemetry_data)
    
    def connection_count(self) -> int:
        """Get total number of active WebSocket connections"""
        return sum(len(connections) for connections in self.connections.values())
    
    def get_session_connection_count(self, session_id: str) -> int:
        """Get number of connections for a specific session"""
        return len(self.connections.get(session_id, set())) 