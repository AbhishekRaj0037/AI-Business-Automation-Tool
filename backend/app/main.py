from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import AuthMiddleware
from app.websockets.dashboard import dashboard_ws
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from app.workers.scheduler import scheduler
from app.websockets.dashboard import redis_listener
from app.websockets.dashboard import clear_all_fetch_status
import asyncio
import os
from app.api.v1.router import api_router

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

app=FastAPI()
app.include_router(api_router)
app.state.limiter = limiter

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

@app.on_event("startup")
async def on_start():
    try:
        scheduler.start()
        print("Started scheduler successfully")
        asyncio.create_task(redis_listener())
        await clear_all_fetch_status()
    except Exception as err:
        print("Scheduler giving error: ", err)


app.websocket("/ws/dashboard")(dashboard_ws)
