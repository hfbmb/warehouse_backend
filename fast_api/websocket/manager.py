from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.total_connections = 0  # Initialize total connections counter

    async def get_active_connections(self):
        return {"active_connections": list(self.active_connections.keys())}
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.total_connections += 1  # Increment total connections

    async def disconnect(self, user_id: str):
        websocket = self.active_connections.pop(user_id, None)
        if websocket:
            await websocket.close()
            self.total_connections -= 1  # Decrement total connections

    async def send_message(self, user_id: str, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def send_message_to_all(self, message: str):
        for _,connection in self.active_connections.items():
            await connection.send_text(message)