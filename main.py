from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager
import imaplib
import email
import os
import model
from FileUpload import cloudinary
import cloudinary.uploader
from DataBase import session
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app:FastAPI):
    # DataBase.init_db()
    yield


app=FastAPI(lifespan=lifespan)

imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")

file_download_path=os.getenv("file_download_path")

mail= imaplib.IMAP4_SSL(imap_server)
mail.login(username,password)


@app.get("/")
async def read_root():
    mail.select("inbox")
    # status,uids=mail.uid('search', None, 'UNSEEN')
    status,uids=mail.uid('search', None, f'UID {28841 + 1}:*')
    breakpoint()
    uids=uids[0].decode('utf-8')
    uid_list=uids.split()
    for uid in uid_list:
        mail_data=mail.fetch(uid,'RFC822')
        raw=mail_data[1][0][1]
        raw_message=email.message_from_bytes(raw)
        for part in raw_message.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            try:
                result=await session.execute(select(model.email_metadata).where(model.email_metadata.uid==uid))
                result=result.scalars().first()
                if result is None or result.processed is True:
                    continue
                filename=part.get_filename()
                if filename:
                    filePath =os.path.join(file_download_path,filename)
                    with open(filePath,'wb') as f:
                        f.write(part.get_payload(decode=True))
                    result=cloudinary.uploader.upload(filePath, 
                    asset_folder = "AI Business Automation Assistant", 
                    public_id = filename,
                    overwrite = True, 
                    resource_type = "raw")
                    print("File uploaded successfully")
                    url=result["url"]
                    report_data=model.email_metadata(uid=uid,reportUrl=url,processed=True)
                    session.add(report_data)
                    await session.commit()
                    print("Added to DB")
            except Exception as E:
                    print(E)



   
