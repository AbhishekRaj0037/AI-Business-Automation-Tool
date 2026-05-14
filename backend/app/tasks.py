# app/tasks.py
from arq import create_pool
from arq.connections import RedisSettings
from app.services.email_service import process_dashboard
from app.db.base import Session

async def fetch_emails_task(ctx, user_id: str, username: str):
    """This runs in the worker process, NOT in the web server."""
    async with Session() as session:
        await process_dashboard(user_id, username)

# Worker configuration
class WorkerSettings:
    functions = [fetch_emails_task]
    redis_settings = RedisSettings(host="localhost", port=6379)