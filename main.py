from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import imaplib
import email
import os
import model

load_dotenv()

@asynccontextmanager
async def lifespan(app:FastAPI):
    await model.init_db()
    yield


app=FastAPI(lifespan=lifespan)

imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")
session=model.session

mail= imaplib.IMAP4_SSL(imap_server)

mail.login(username,password)
print("Main is executed")



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



   
