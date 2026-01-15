from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Query,HTTPException
from contextlib import asynccontextmanager
import imaplib
import email
import os
import model
from FileUpload import cloudinary
import cloudinary.uploader
from DataBase import session,get_session
from sqlalchemy import select,update,desc
from model import StatusEnum
from email.utils import parsedate_to_datetime
from datetime import timezone,datetime,timedelta
from schemas import EmailMetaDataOut
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,Request
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from DataBase import DBUrl
import asyncio

from fastapi_sa_orm_filter.main import FilterCore
from fastapi_sa_orm_filter.operators import Operators as ops

from pwdlib import PasswordHash
import jwt

SQLAlchemyJobStoreURL=os.getenv("SQLAlchemyJobStore")

password_hash=PasswordHash.recommended()

my_objects_filter={
    'status': [ops.eq, ops.in_],
    'mail_from': [ops.eq, ops.in_, ops.like, ops.startswith, ops.contains],
    'received_at': [ops.between, ops.eq, ops.gt, ops.lt, ops.in_],
}

jobstores={
    'default' : SQLAlchemyJobStore(url=SQLAlchemyJobStoreURL)
}

executors={
    'default' : AsyncIOExecutor()
}

job_defaults={
    'coalesce' : True,
    'max_instance' : 3
}


app=FastAPI()
scheduler=AsyncIOScheduler(jobstores=jobstores,executors=executors,job_defaults=job_defaults)

SECRET_KEY="7e3fa174ea94139b8f08e6dbfbe75d1e9ecd4cd7a2958a743b8d3cbcd4302bdc"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_MINUTES=30*60




@app.on_event("startup")
def on_start():
    try:
        scheduler.start()
        print("Started scheduler successfully")
    except Exception as err:
        print("Scheduler giving error which is: ", err)

def checksum_from_part(part, algo="sha256", chunk_size=8192):
    hasher = hashlib.new(algo)

    payload = part.get_payload(decode=True)  # bytes
    if payload is None:
        return None

    # Stream in chunks (safe for large files)
    for i in range(0, len(payload), chunk_size):
        hasher.update(payload[i:i + chunk_size])

    return hasher.hexdigest()

# @asynccontextmanager
# async def lifespan(app:FastAPI):
#     # DataBase.init_db()
#     yield

# Removed lifespan=lifespan from app=FastAPI() line for the manual creation of table.


imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")

file_download_path=os.getenv("file_download_path")

mail= imaplib.IMAP4_SSL(imap_server)
mail.login(username,password)
mail.select("inbox")


@app.get("/")
async def read_root():
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)).limit(1))
    result=result.scalars().first()
    starting_uid_range=0
    if result is not None:
         starting_uid_range=result.imap_uid
    status,uids=mail.uid('search', None, f'UID {starting_uid_range + 1}:*')
    uids=uids[0].decode('utf-8')
    uid_list=uids.split()
    for uid in uid_list:
        mail_data=mail.fetch(uid,'RFC822')
        raw=mail_data[1][0][1]
        raw_message=email.message_from_bytes(raw)
        mail_from=raw_message["from"]
        subject=raw_message["Subject"]
        received_at=raw_message["Date"]
        aware = parsedate_to_datetime(received_at)
        received_at = aware.astimezone(timezone.utc).replace(tzinfo=None)
        # for part in raw_message.walk():
        #     if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
        #         continue
        #     filename=part.get_filename()
        #     if filename:
        #         count_of_document_file=count_of_document_file+1

        is_uid_already_synced=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(uid)))
        is_uid_already_synced=is_uid_already_synced.scalars().first()
        if is_uid_already_synced is None:
            report_data=None
            report_data=model.email_metadata(imap_uid=int(uid),mail_from=mail_from,subject=subject,received_at=received_at)
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


@app.get("/get-all-reports")
async def get_all_reports():
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)))
    result=result.scalars().all()
    pass
   

# Query parameters will be like
# For Example status__eq=incomplete&mail_from__like=%Abhishek%&received_at__between=2020-01-01,2020-01-01

@app.post("/get-reports")
async def get_reports(
    objects_filter: str =Query(default=''),
    db:AsyncSession=Depends(get_session),
) -> List[EmailMetaDataOut]:
    filter_result=FilterCore(model.email_metadata,my_objects_filter)
    query=filter_result.get_query(objects_filter)
    db_obj=await session.execute(query)
    instance=db_obj.scalars().all()
    return instance



@app.post("/fetch-mail-data")
async def get_mail(
    imap_uid:str,
    request:Request
):  
    request=await request.json()
    token=request['token']
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username=payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401,detail="Incorrect credential")
    except Exception as err:
        print("Error authenticating user: ",err)
        return {"Error":err}
    print("Welcome, ",username)
    mail_data=mail.fetch(imap_uid,'RFC822')
    raw=mail_data[1][0][1]
    raw_message=email.message_from_bytes(raw)
    mail_from=raw_message["from"]
    subject=raw_message["Subject"]
    received_at=raw_message["Date"]
    aware = parsedate_to_datetime(received_at)
    received_at = aware.astimezone(timezone.utc).replace(tzinfo=None)
    is_uid_already_present=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(imap_uid)))
    is_uid_already_present=is_uid_already_present.scalars().first()
    if is_uid_already_present.status==StatusEnum.completed:
        print("Triggered:      ",is_uid_already_present)
        return
    for part in raw_message.walk():
        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
            continue
        filename=part.get_filename()
        if filename:
            checksum = checksum_from_part(part)
            is_uid_already_present=await session.execute(select(model.email_attachments_metadata).join(model.email_metadata,model.email_attachments_metadata.email_id==model.email_metadata.id).where(model.email_metadata.imap_uid==int(imap_uid) and model.email_attachments_metadata.checksum_sha256==checksum))
            is_uid_already_present=is_uid_already_present.scalars().all()
            if is_uid_already_present == []:
                result=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(imap_uid))) 
                result=result.scalars().one()
                mail_data=model.email_attachments_metadata(email_id=result.id,file_name=filename,file_size=len(part.get_payload(decode=True)),cloudinary_reportUrl="cloudinary_URL",status=StatusEnum.pending,checksum_sha256=checksum)
                session.add(mail_data)
                await session.commit()
                print("Added to DB")
    result=update(model.email_metadata).where(model.email_metadata.imap_uid == int(imap_uid)).values(status=StatusEnum.completed)
    await session.execute(result)
    await session.commit()


    is_uid_already_present=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(imap_uid)))
    is_uid_already_present=is_uid_already_present.scalars().first()
    if is_uid_already_present.status==StatusEnum.completed:
        print("Triggered:      ",is_uid_already_present)
        return


    
    return


@app.post("/create-user")
async def create_user(request: Request):
    body = await request.json()
    result=await session.execute(select(model.User).where(model.User.email==body['email']))
    result=result.scalars().all()
    if result != []:
        print("User already exsist")
        return
    hashed_password= password_hash.hash(body['password'])
    user=model.User(username=body['email'],password=hashed_password,email=body['email'],disabed=body['disable'])
    session.add(user)
    await session.commit()
    print("User Added to DB")
    return {"Status":200,"details":"User Added successfully"}

@app.post("/login-user")
async def login_user(request:Request):
    body=await request.json()
    result=await session.execute(select(model.User).where(model.User.email==body['email']))
    result=result.scalars().first()
    if result == []:
        print("User doesn't exsist")
        return HTTPException(status_code=404,detail="User doesn't exsist")
    hashed_password= password_hash.hash(body['password'])
    if password_hash.verify(body['password'],result.password)==False:
        print("Password Incorrect")
        return HTTPException(status_code=401,detail="Password Incorrect")
    
    access_token_expires=datetime.now(timezone.utc)+timedelta(minutes=3)
    user={"sub":result.username}
    user.update({"exp":access_token_expires})
    encode_jwt_token=jwt.encode(user,SECRET_KEY,algorithm=ALGORITHM)
    user=model.Token(token=encode_jwt_token,user_id=result.id)
    session.add(user)
    await session.commit()
    print("Added to DB")
    return {"Toke": encode_jwt_token,"Type":"Bearer"}



# try:
#     job=scheduler.add_job(get_mail,trigger='interval',seconds=30,id="Call_Fetch_mail_with_the_id_28",kwargs={"imap_uid":"28"})
#     print("Successfully added job in job store.")
# except Exception as err:
#     print("You have error scheduling jobs:    ",err)