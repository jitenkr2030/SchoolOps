"""
Chat Manager for WebSocket Communication
"""
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime
from collections import defaultdict


class ConnectionManager:
    """
    Manages WebSocket connections for real-time chat
    """
    
    def __init__(self):
        # active_connections: user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        # user_rooms: user_id -> set of room_ids
        self.user_rooms: Dict[int, set] = defaultdict(set)
        # room_connections: room_id -> set of WebSocket
        self.room_connections: Dict[int, set] = defaultdict(set)
    
    async def connect(self, websocket: WebSocket, user_id: int, room_id: Optional[int] = None):
        """
        Accept WebSocket connection and register user
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        if room_id:
            self.user_rooms[user_id].add(room_id)
            self.room_connections[room_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Disconnect WebSocket and cleanup
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove from all rooms
        for room_id in self.user_rooms[user_id]:
            if websocket in self.room_connections[room_id]:
                self.room_connections[room_id].discard(websocket)
        
        del self.user_rooms[user_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send message to single connection
        """
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def send_personal_json(self, data: dict, websocket: WebSocket):
        """
        Send JSON message to single connection
        """
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"Error sending personal JSON: {e}")
    
    async def broadcast_to_room(self, room_id: int, message: str, exclude_user_id: Optional[int] = None):
        """
        Broadcast message to all connections in a room
        """
        connections = self.room_connections.get(room_id, set()).copy()
        for websocket in connections:
            # Get user_id from inverse mapping
            for user_id, ws in self.active_connections.items():
                if ws == websocket:
                    if user_id != exclude_user_id:
                        await self.send_personal_message(message, websocket)
                    break
    
    async def broadcast_to_room_json(
        self, 
        room_id: int, 
        data: dict, 
        exclude_user_id: Optional[int] = None
    ):
        """
        Broadcast JSON message to all connections in a room
        """
        connections = self.room_connections.get(room_id, set()).copy()
        for websocket in connections:
            # Get user_id from inverse mapping
            for user_id, ws in self.active_connections.items():
                if ws == websocket:
                    if user_id != exclude_user_id:
                        await self.send_personal_json(data, websocket)
                    break
    
    async def broadcast_to_all(self, message: str, exclude_user_id: Optional[int] = None):
        """
        Broadcast message to all active connections
        """
        for user_id, websocket in self.active_connections.items():
            if user_id != exclude_user_id:
                await self.send_personal_message(message, websocket)
    
    async def broadcast_to_all_json(self, data: dict, exclude_user_id: Optional[int] = None):
        """
        Broadcast JSON message to all active connections
        """
        for user_id, websocket in self.active_connections.items():
            if user_id != exclude_user_id:
                await self.send_personal_json(data, websocket)
    
    def get_online_users(self, room_id: Optional[int] = None) -> List[int]:
        """
        Get list of online user IDs
        """
        if room_id:
            online_users = []
            for user_id, rooms in self.user_rooms.items():
                if room_id in rooms:
                    online_users.append(user_id)
            return online_users
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: int) -> bool:
        """
        Check if user is online
        """
        return user_id in self.active_connections
    
    def get_room_participants(self, room_id: int) -> List[int]:
        """
        Get all user IDs in a room
        """
        return list(self.user_rooms.get(room_id, set()))
    
    async def join_room(self, user_id: int, room_id: int, websocket: WebSocket):
        """
        Add user to a room
        """
        self.user_rooms[user_id].add(room_id)
        self.room_connections[room_id].add(websocket)
        
        # Notify room
        await self.broadcast_to_room_json(
            room_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "message": f"User {user_id} joined the room",
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user_id=user_id
        )
    
    async def leave_room(self, user_id: int, room_id: int, websocket: WebSocket):
        """
        Remove user from a room
        """
        self.user_rooms[user_id].discard(room_id)
        self.room_connections[room_id].discard(websocket)
        
        # Notify room
        await self.broadcast_to_room_json(
            room_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "message": f"User {user_id} left the room",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def leave_all_rooms(self, user_id: int, websocket: WebSocket):
        """
        Remove user from all rooms
        """
        for room_id in self.user_rooms[user_id]:
            self.room_connections[room_id].discard(websocket)
        self.user_rooms[user_id].clear()


class ChatMessageFormatter:
    """
    Utility class for formatting chat messages
    """
    
    @staticmethod
    def format_chat_message(
        message_id: int,
        room_id: int,
        sender_id: int,
        content: str,
        message_type: str = "text",
        timestamp: Optional[datetime] = None,
        sender_name: Optional[str] = None
    ) -> dict:
        """
        Format a chat message for sending
        """
        return {
            "type": "chat",
            "message_id": message_id,
            "room_id": room_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "message_type": message_type,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        }
    
    @staticmethod
    def format_system_message(
        content: str,
        room_id: Optional[int] = None
    ) -> dict:
        """
        Format a system message
        """
        return {
            "type": "system",
            "content": content,
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_typing_indicator(user_id: int, room_id: int, is_typing: bool) -> dict:
        """
        Format typing indicator
        """
        return {
            "type": "typing",
            "user_id": user_id,
            "room_id": room_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_read_receipt(
        user_id: int,
        room_id: int,
        last_read_message_id: int
    ) -> dict:
        """
        Format read receipt
        """
        return {
            "type": "read_receipt",
            "user_id": user_id,
            "room_id": room_id,
            "last_read_message_id": last_read_message_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_error_message(error: str) -> dict:
        """
        Format error message
        """
        return {
            "type": "error",
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global chat manager instance
chat_manager = ConnectionManager()
message_formatter = ChatMessageFormatter()
