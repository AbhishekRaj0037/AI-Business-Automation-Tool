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
from sqlalchemy import select,desc
from model import StatusEnum

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
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)).limit(1))
    result=result.scalars().first()
    starting_uid_range=0
    if result is not None:
         starting_uid_range=result.imap_uid
    starting_uid_range=int(starting_uid_range) 
    status,uids=mail.uid('search', None, f'UID {starting_uid_range + 1}:*')
    uids=uids[0].decode('utf-8')
    uid_list=uids.split()
    for uid in uid_list:
        mail_data=mail.fetch(uid,'RFC822')
        raw=mail_data[1][0][1]
        raw_message=email.message_from_bytes(raw)
        count_of_document_file=0
        for part in raw_message.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            filename=part.get_filename()
            if filename:
                count_of_document_file=count_of_document_file+1
        is_uid_already_synced=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==uid))
        is_uid_already_synced=is_uid_already_synced.scalars().first()
        if is_uid_already_synced is None:
            is_uid_already_synced=False
        else:
            is_uid_already_synced=True
        if is_uid_already_synced == False:
            report_data=None
            if count_of_document_file==0:
                report_data=model.email_metadata(imap_uid=uid,total_pdfs=count_of_document_file,processed_pdfs=0,status=StatusEnum.completed)
            else:
                report_data=model.email_metadata(imap_uid=uid,total_pdfs=count_of_document_file,processed_pdfs=0,status=StatusEnum.incomplete)
            session.add(report_data)
            await session.commit()
            print("Added to DB")
            # try:
            #     result=await session.execute(select(model.email_metadata).where(model.email_metadata.uid==uid))
            #     result=result.scalars().first()
            #     if result is None or result.processed is True:
            #         continue
            #     filename=part.get_filename()
            #     if filename:
            #         filePath =os.path.join(file_download_path,filename)
            #         with open(filePath,'wb') as f:
            #             f.write(part.get_payload(decode=True))
            #         result=cloudinary.uploader.upload(filePath, 
            #         asset_folder = "AI Business Automation Assistant", 
            #         public_id = filename,
            #         overwrite = True, 
            #         resource_type = "raw")
            #         print("File uploaded successfully")
            #         url=result["url"]
            #         report_data=model.email_metadata(uid=uid,reportUrl=url,processed=True)
            #         session.add(report_data)
            #         await session.commit()
            #         print("Added to DB")
            # except Exception as E:
            #         print(E)



   
