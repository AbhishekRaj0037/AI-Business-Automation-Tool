from fastapi import WebSocket,WebSocketDisconnect
from app.websockets.manager import r,manager
import time as time_module
from app.config import settings
from datetime import date
import asyncio
import json
import jwt

async def get_dashboard_stats(userId: str):
    today =date.today()
    queue_key = f"userId:{userId}:queue"
    stats_key = f"userId:{userId}:stats:{today}"

    queue = await r.hgetall(queue_key)
    stats = await r.hgetall(stats_key)
    return {
        "queue": queue,
        "stats": stats
    }

async def redis_listener():
    pubsub =r.pubsub()
    await pubsub.psubscribe("userId:*:updates")
    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            data = json.loads(message["data"])
            userId = data["userId"]
            button= await get_task_status(userId)

            # fetch latest stats from Redis
            stats = await get_dashboard_stats(userId)
            # push to correct websocket user
            try:
                await manager.send(userId, stats,button)
            except Exception:
                print("redis_listener iteration failed")

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
    await r.publish(
        f"userId:{user_id}:updates",
        json.dumps({"userId": user_id})
    )
    

async def get_task_status(user_id: str) -> str | None:
    return await r.get(f"fetching:{user_id}")



async def dashboard_ws(websocket:WebSocket):
    jwt_token = websocket.cookies.get("jwt_token")
    await websocket.accept()
    if not jwt_token:
        await websocket.close(code=1008)
        return
    try:
        payload=jwt.decode(jwt_token,settings.JWT_SECRET_KEY,algorithms=settings.ALGORITHM)
        userId=payload.get("user_id")
        exp=payload.get("exp")
    except jwt.ExpiredSignatureError:
        await websocket.close(code=1008)
        return
    await manager.connect(userId,websocket)
    data=await get_dashboard_stats(userId)
    buttonStatus=await get_task_status(userId)
    await websocket.send_json({
        'userId':userId,'data':data,'button':buttonStatus
    })
    async def token_monitor():
        try:
            remaining = exp - int(time_module.time())
            if remaining > 0:
                await asyncio.sleep(remaining)
            await websocket.send_json({"error": "token expired"})
            await websocket.close(code=1008)
        except Exception as e:
            print("monitor error:", e)

    async def receive_loop():
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
                pass
        except Exception as e:
            print("WS error for user %s", userId)
        finally:
            manager.disconnect(userId, websocket)

    monitor_task = asyncio.create_task(token_monitor())
    receive_task = asyncio.create_task(receive_loop())
    done, pending = await asyncio.wait(
        [monitor_task, receive_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    manager.disconnect(userId, websocket)

