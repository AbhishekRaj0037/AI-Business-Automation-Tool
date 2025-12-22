
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.ext.asyncio import AsyncEngine
from main import Base

class ReportData(Base):
    __tablename__="Report Data"

    id=Column(Integer,primary_key=True)
    reportUrl=Column(String)
    processed=Column(Boolean)



