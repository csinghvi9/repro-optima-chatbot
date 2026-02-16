from typing import Dict
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # { user_id: { session_id: { "websocket": ws, "thread_id": str } } }
        self.connections: Dict[str, Dict[str, Dict[str, any]]] = {}

    async def connect(self, user_id: str, session_id: str, websocket: WebSocket):
        self.connections.setdefault(user_id, {})[session_id] = {
            "websocket": websocket,
            "thread_id": None,
        }

    def set_thread(self, user_id: str, session_id: str, thread_id: str):
        if user_id in self.connections and session_id in self.connections[user_id]:
            self.connections[user_id][session_id]["thread_id"] = thread_id

    def get_thread(self, user_id: str, session_id: str) -> str:
        return self.connections.get(user_id, {}).get(session_id, {}).get("thread_id")

    def disconnect(self, user_id: str, session_id: str):
        if user_id not in self.connections:
            return  # Already removed or never existed

        sessions = self.connections[user_id]

        if session_id in sessions:
            del sessions[session_id]  # remove that session

        if not sessions:  # if no sessions left for this user, clean up
            del self.connections[user_id]

    async def send_to_current_thread(self, user_id: str, session_id: str, message: str):
        conn = self.connections.get(user_id, {}).get(session_id)
        if conn and conn["thread_id"]:
            await conn["websocket"].send_text(message)

    async def broadcast_to_all_sessions(self, user_id: str, message: str):
        for conn in self.connections.get(user_id, {}).values():
            await conn["websocket"].send_text(message)
