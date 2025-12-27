
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import declarative_base
Base=declarative_base()

class ReportData(Base):
    __tablename__="Report Data"
    id=Column(Integer,primary_key=True)
    uid=Column(String)
    reportUrl=Column(String)
    processed=Column(Boolean)
