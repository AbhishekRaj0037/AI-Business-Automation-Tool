from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.websockets.dashboard import clear_all_fetch_status
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import AuthMiddleware
from app.websockets.dashboard import dashboard_ws
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from app.workers.scheduler import scheduler
from app.websockets.dashboard import redis_listener
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
import asyncio
import os

from arq import create_pool
from arq.connections import RedisSettings

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    listener_task = None
    app.state.redis_pool = None
    try:
        scheduler.start()
        print("Started scheduler successfully")
        listener_task = asyncio.create_task(redis_listener())
        app.state.redis_pool= await create_pool(RedisSettings(host="localhost"))
        await clear_all_fetch_status()
    except Exception as err:
        print("Scheduler giving error: ", err)
    try:
        yield
    finally:
        # --- shutdown ---
        if listener_task is not None:
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass
        if app.state.redis_pool is not None:
            await app.state.redis_pool.close()
        if scheduler.running:
            scheduler.shutdown()

app=FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.include_router(api_router)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many attempts, try again later"}
    )

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.websocket("/ws/dashboard")(dashboard_ws)
