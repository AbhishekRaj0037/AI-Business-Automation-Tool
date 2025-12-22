from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import imaplib
import email
import os
from sqlalchemy.orm import declarative_base
Base=declarative_base()
import model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


url="postgresql+asyncpg://localhost:5432/ai_business_automation_assistant"
engine=create_async_engine(url)
Session=sessionmaker(engine)
session=Session()

async def init_db():
    async with AsyncSessionLocal() as session:
        # await conn.run_sync(Base.metadata.create_all)
        yield session

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield


app=FastAPI(lifespan=lifespan)

imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")

mail= imaplib.IMAP4_SSL(imap_server)

mail.login(username,password)



@app.get("/")
async def read_root():
    mail.select("inbox")
    # status,messages=mail.search(None,"ALL")
    status,messages=mail.uid('search', None, 'UNSEEN')
    messages=messages[0].decode('utf-8')
    messages=messages.split()
    report_data=model.ReportData(reportUrl="reported_url",processed=True)
    session.add(report_data)
    await session.commit()
    print("Added to DB")
    for ele in messages:
        msg=mail.fetch(ele,'RFC822')
        raw=msg[1][0][1]
        raw_message=email.message_from_bytes(raw)
        for part in raw_message.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            filename=part.get_filename()
            if bool(filename):
                filePath =os.path.join('/Users/abhishekraj/desktop/AI Business Automation Assistant/Downloaded Files',filename)
                with open(filePath,'wb') as f:
                    f.write(part.get_payload(decode=True))



   
