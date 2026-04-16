from fastapi import WebSocket
import redis.asyncio as redis
from app.config import settings

r=redis.Redis(host=settings.Redis_DB,port=6379,decode_responses=True)

from fastapi import WebSocket
from starlette.websockets import WebSocketState
import logging

log = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, userId: str, websocket: WebSocket):
        if userId not in self.active_connections:
            self.active_connections[userId] = []
        self.active_connections[userId].append(websocket)

    def disconnect(self, userId: str, websocket: WebSocket):
        if userId in self.active_connections:
            try:
                self.active_connections[userId].remove(websocket)
            except ValueError:
                pass 
            if not self.active_connections[userId]:
                del self.active_connections[userId]

    async def send(self, userId: str, data: dict, button: str):
        if userId not in self.active_connections:
            return

        payload = {"userId": userId, "data": data, "button": button}
        dead_sockets = []

        for ws in self.active_connections[userId]:

            if ws.client_state != WebSocketState.CONNECTED:
                dead_sockets.append(ws)
                continue

            try:
                await ws.send_json(payload)
            except (RuntimeError, Exception) as e:
                log.warning("Dead WS for user %s: %s", userId, e)
                dead_sockets.append(ws)

        for ws in dead_sockets:
            self.disconnect(userId, ws)


manager=ConnectionManager()