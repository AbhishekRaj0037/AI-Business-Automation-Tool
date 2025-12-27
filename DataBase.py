from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
import os
from model import Base

DBUrl=os.getenv("DBUrl")
engine=create_async_engine(DBUrl)


Session=async_sessionmaker(engine)
session=Session()

async def init_db():
    async with session() as session:
        await session.run_sync(Base.metadata.create_all)
        yield session
