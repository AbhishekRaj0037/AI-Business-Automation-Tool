from fastapi import WebSocket
import redis.asyncio as redis
import json
from datetime import date

r=redis.Redis(host='localhost',port=6379,decode_responses=True)


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, userId: str, websocket: WebSocket):
        if userId not in self.active_connections:
            self.active_connections[userId] = []
        self.active_connections[userId].append(websocket)

    def disconnect(self, userId: str, websocket: WebSocket):
        if userId in self.active_connections:
            self.active_connections[userId].remove(websocket)

    async def send(self, userId: str, data: dict,button:str):
        
        if userId in self.active_connections:
            
            for ws in self.active_connections[userId]:
                await ws.send_json({'userId':userId,'data':data,'button':button})




async def update_user_dashboard(
    userId: str,
    queue_changes: dict = None,
    stats_changes: dict = None
):

    today = date.today().isoformat()

    queue_key = f"userId:{userId}:queue"
    stats_key = f"userId:{userId}:stats:{today}"

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
        f"userId:{userId}:updates",
        json.dumps({"userId": userId})
    )

async def clear_all_fetch_status():
    keys = await r.keys("fetching:*")
    for key in keys:
        await r.set(key, "false")


async def set_task_status(user_id: str, status: str):
    await r.set(f"fetching:{user_id}", status)

async def get_task_status(user_id: str) -> str | None:
    return await r.get(f"fetching:{user_id}")
