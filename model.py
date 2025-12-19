from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
from sqlalchemy.engine import URL




# url=URL.create(
#     drivername="postgresql",
#     host="localhost",
#     database="ai_business_automation_assistant",
#     port=5432
# )

url="postgresql+asyncpg://localhost:5432/ai_business_automation_assistant"
engine=create_async_engine(url)
Session=sessionmaker(bind=engine)
session=Session()

Base=declarative_base()

class ReportData(Base):
    __tablename__="Report Data"

    id=Column(Integer,primary_key=True)
    reportUrl=Column(String)
    processed=Column(Boolean)


# Base.metadata.create_all(engine)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

init_db()