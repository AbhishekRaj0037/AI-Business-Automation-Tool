from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine
from sqlalchemy.orm import declarative_base
from app.config import settings


Base=declarative_base()

engine=create_async_engine(settings.DBUrl)
Session=async_sessionmaker(engine,expire_on_commit=False)

import app.db.models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
