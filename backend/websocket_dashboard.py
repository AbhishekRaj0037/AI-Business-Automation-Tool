from fastapi import WebSocket
import redis.asyncio as redis
import json
from datetime import date

r=redis.Redis(host='localhost',port=6379,decode_responses=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, username: str, websocket: WebSocket):
        # await websocket.accept()
        if username not in self.active_connections:
            self.active_connections[username] = []
        self.active_connections[username].append(websocket)

    def disconnect(self, username: str, websocket: WebSocket):
        if username in self.active_connections:
            self.active_connections[username].remove(websocket)

    async def send(self, username: str, data: dict):
        
        if username in self.active_connections:
    
            for ws in self.active_connections[username]:
                await ws.send_json({'username':username,'data':data})




async def update_user_dashboard(
    username: str,
    queue_changes: dict = None,
    stats_changes: dict = None
):
    today = date.today().isoformat()

    queue_key = f"user:{username}:queue"
    stats_key = f"user:{username}:stats:{today}"

    # 🔹 Update Queue Counters
    if queue_changes:
        for field, value in queue_changes.items():
            await r.hincrby(queue_key, field, value)

    # 🔹 Update Daily Stats
    if stats_changes:
        for field, value in stats_changes.items():
            await r.hincrby(stats_key, field, value)

        # expire after 2 days
        await r.expire(stats_key, 172800)

    # 🔹 Publish update event
    await r.publish(
        f"user:{username}:updates",
        json.dumps({"username": username})
    )
