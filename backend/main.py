from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Query,HTTPException,Depends,Request,WebSocket,Response,Cookie
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from websocket_dashboard import ConnectionManager,update_user_dashboard,r
from fastapi_sa_orm_filter.operators import Operators as ops
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sa_orm_filter.main import FilterCore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import timezone,datetime,timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,desc
from email.utils import parsedate_to_datetime
from DataBase import session,get_session
from FileUpload import cloudinary
import websocket_dashboard
from model import StatusEnum
from schemas import EmailMetaDataOut
from pwdlib import PasswordHash
from datetime import date
import cloudinary.uploader
from typing import List

import hashlib
import imaplib
import model
import email
import json
import asyncio
import time
import boto3
import jwt
import os

from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
import langchain_community.document_loaders as docloader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_classic.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import OpenAI
from langchain_openai import AzureChatOpenAI

from email.message import Message

SQLAlchemyJobStoreURL=os.getenv("SQLAlchemyJobStore")
file_download_path=os.getenv("file_download_path")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")

aws_access_key=os.getenv("aws_access_key")
aws_secret_key=os.getenv("aws_secret_key")
aws_region=os.getenv("aws_region")


s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_MINUTES=30*60

password_hash=PasswordHash.recommended()

app=FastAPI()

EXCLUDED_PATHS = ["/login-user", "/create-user"]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)
        jwt_token = request.cookies.get("jwt_token")
        if not jwt_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )
        try:
            payload=jwt.decode(jwt_token,JWT_SECRET_KEY,algorithms=ALGORITHM)
            username=payload.get("sub")
            if username is None:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid credentials"}
                )
            
            request.state.user = username
        except Exception as err:
            print("Error authenticating user: ",err)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

       
        response = await call_next(request)
        
        return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

manager=ConnectionManager()

mail= imaplib.IMAP4_SSL(imap_server)
mail.login(username,password)
mail.select("inbox")


VECTOR_DB=os.getenv("VECTOR_DB")



llm= AzureChatOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://azure-open-ai-business-automation-tool.openai.azure.com/",
    api_key=OPENAI_API_KEY,
    azure_deployment="gpt-4.1-mini"
)

splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

embeddings=AzureOpenAIEmbeddings(
    api_version="2024-02-01",
    azure_endpoint="https://azure-open-ai-business-automation-tool.openai.azure.com/",
    api_key=OPENAI_API_KEY,
    azure_deployment="text-embedding-3-small"
)


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

scheduler=AsyncIOScheduler(jobstores=jobstores,executors=executors,job_defaults=job_defaults)

async def get_dashboard_stats(username: str):
    today = date.today().isoformat()
    queue_key = f"user:{username}:queue"
    stats_key = f"user:{username}:stats:{today}"

    queue = await websocket_dashboard.r.hgetall(queue_key)
    stats = await websocket_dashboard.r.hgetall(stats_key)

    return {
        "queue": queue,
        "stats": stats
    }

async def redis_listener():
    pubsub =r.pubsub()
    await pubsub.psubscribe("user:*:updates")

    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            data = json.loads(message["data"])
            username = data["username"]
            
            # fetch latest stats from Redis
            stats = await get_dashboard_stats(username)
            
            # push to correct websocket user
            await manager.send(username, stats)
            

@app.on_event("startup")
def on_start():
    try:
        scheduler.start()
        print("Started scheduler successfully")
        asyncio.create_task(redis_listener())
    except Exception as err:
        print("Scheduler giving error: ", err)

def checksum_from_part(part, algo="sha256", chunk_size=8192):
    hasher = hashlib.new(algo)

    payload = part.get_payload(decode=True)
    if payload is None:
        return None

    for i in range(0, len(payload), chunk_size):
        hasher.update(payload[i:i + chunk_size])

    return hasher.hexdigest()

def get_email_body(msg: Message) -> str:
    """
    Extracts the plain text body from an email message object.
    """
    if msg.is_multipart():
        for part in msg.walk():
            # Find the first plain text part
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
            # If no plain text, find the first HTML part as a fallback
            elif part.get_content_type() == 'text/html':
                # You may want to use a library like html2text to convert HTML to text
                return part.get_payload(decode=True).decode()
    else:
        # Not a multipart message, return the payload directly
        return msg.get_payload(decode=True).decode()
    

@app.get("/")
async def read_root(request:Request):
    print("Welcome ",request.state.user)
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)).limit(1))
    result=result.scalars().first()
    starting_uid_range=0
    if result is not None:
         starting_uid_range=result.imap_uid
    uids=mail.uid('search', None, f'UID {starting_uid_range + 1}:*')
    # uids=uids[0].decode('utf-8')
    uid_list=uids[1][0].split()
    for uid in uid_list:
        mail_data=mail.fetch(uid,'RFC822')
        raw=mail_data[1][0][1]
        raw_message=email.message_from_bytes(raw)
        mail_from=raw_message["from"]
        subject=raw_message["Subject"]
        received_at=raw_message["Date"]
        body=get_email_body(raw_message)
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        formatted_body = "\n".join(lines)
        aware = parsedate_to_datetime(received_at)
        received_at = aware.astimezone(timezone.utc).replace(tzinfo=None)
        is_uid_already_synced=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(uid)))
        is_uid_already_synced=is_uid_already_synced.scalars().first()
        if is_uid_already_synced is None:
            report_data=None
            report_data=model.email_metadata(imap_uid=int(uid),mail_from=mail_from,subject=subject,received_at=received_at,body=formatted_body)
            session.add(report_data)
            await session.commit()
            for part in raw_message.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                filename = part.get_filename()
                if filename:
                    try:
                        file_bytes = part.get_payload(decode=True)
                        s3.put_object(Bucket="amzn-s3-bucket-ai-business-automation-assistant",Key=f"{filename}",Body=file_bytes)
                        print("File uploaded succesfully on aws bucket")
                        file_data=None
                        content_type = part.get_content_type()
                        file_data=model.email_attachments_metadata(imap_uid=int(uid),file_name=filename,file_type=content_type,file_size=len(file_bytes),status=StatusEnum.incomplete,checksum_sha256="!231231231231!")
                        session.add(file_data)
                        await session.commit()
                    except Exception as e:
                        print("Error:  ",e)
            await update_user_dashboard(username,stats_changes={
                "fetch_today":1
            })
            print("Added to DB")


@app.get("/get-all-reports")
async def get_all_reports(request:Request,page:int=Query(1),limit:int=Query(4)):
    print("Welcome ",request.state.user)
    offset=(page-1)*limit
    result=await session.execute(select(model.email_metadata).offset(offset).order_by(desc(model.email_metadata.imap_uid)).limit(limit))
    result=result.scalars().all()
    return result
   
@app.get("/get-reports-by-id")
async def get_all_reports(request:Request,imap_uid:int=Query(1),page:int=Query(1),limit:int=Query(4)):
    print("Welcome ",request.state.user)
    mail_result=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(imap_uid)))
    mail_result=mail_result.scalars().first()
    offset=(page-1)*limit
    attachment_result=await session.execute(select(model.email_attachments_metadata).offset(offset).where(model.email_attachments_metadata.imap_uid==int(imap_uid)).limit(limit))
    attachment_result=attachment_result.scalars().all()
    list_of_file_url=[]
    for result in attachment_result:
        url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': "amzn-s3-bucket-ai-business-automation-assistant",
            'Key': result.file_name,
            'ResponseContentDisposition': 'inline',
            'ResponseContentType': result.file_type
        },
        ExpiresIn=300
    )
        list_of_file_url.append(url)
    result={"mail_result":mail_result,"attachment_result":attachment_result,"list_of_file_presigned_url":list_of_file_url}
    return result


@app.post("/get-reports")
async def get_reports(
    request:Request,
    objects_filter: str =Query(default=''),
    db:AsyncSession=Depends(get_session),
) -> List[EmailMetaDataOut]:
    print("Welcome ",request.state.user)
    filter_result=FilterCore(model.email_metadata,my_objects_filter)
    query=filter_result.get_query(objects_filter)
    db_obj=await session.execute(query)
    instance=db_obj.scalars().all()
    return instance



@app.post("/fetch-mail-data")
async def get_mail(
    imap_uid:str,
    request:Request,
):  
    print("Welcome ",request.state.user)
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
    print("Welcome ",request.state.user)
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
async def login_user(request:Request,response:Response):
    body=await request.json()
    result=await session.execute(select(model.User).where(model.User.email==body['email']))
    result=result.scalars().first()
    if result is None:
        print("User doesn't exsist")
        raise HTTPException(status_code=404,detail="User doesn't exsist")
    if password_hash.verify(body['password'],result.password)==False:
        print("Password Incorrect")
        raise HTTPException(status_code=401,detail="Password Incorrect")
    
    access_token_expires=datetime.now(timezone.utc)+timedelta(minutes=3)
    user={"sub":result.username}
    user.update({"exp":access_token_expires})
    encode_jwt_token=jwt.encode(user,JWT_SECRET_KEY,algorithm=ALGORITHM)
    user=model.Token(token=encode_jwt_token,user_id=result.id)
    session.add(user)
    await session.commit()
    response.set_cookie(
        key="jwt_token",
        value=encode_jwt_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    print("Added to DB")
    print("Login successfully")
    return {"Toke": encode_jwt_token,"Type":"Bearer","message":"Login Successful"}

# @app.get("/me")
# async def get_current_user(jwt_token:str=Cookie(None)):
#     breakpoint()
#     if not jwt_token:
#         raise HTTPException(status_code=401,detail="Not authenticated")
#     try:
#         payload=jwt.decode(jwt_token,JWT_SECRET_KEY,algorithms=ALGORITHM)
#         username=payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401,detail="Incorrect credential")
#     except Exception as err:
#         print("Error authenticating user: ",err)
#         raise HTTPException(status_code=401,detail="Unauthorized credential")
#     print("Welcome ",username)
    
#     return {"message":f"{username} authenticated"}

@app.post("/update-report-status")
async def update_report_status(request:Request):
    print("Welcome ",request.state.user)
    body=await request.json()
    report_id=body["report_id"]
    report_status=StatusEnum[body["report_status"]]
    report=update(model.email_attachments_metadata).where(model.email_attachments_metadata.id==int(report_id)).values(status=report_status)
    await session.execute(report)
    await session.commit()


@app.post("/analyse-report")
async def analyse_report(request:Request):
    print("Welcome ",request.state.user)
    try:
        await update_user_dashboard(username,queue_changes={
                    "pending":1,
                })
        loader=docloader.PyPDFLoader("Policy-P000188666627.pdf")
        loaded_doc=loader.load()
        doc_chunks=splitter.split_documents(loaded_doc)
        if os.path.exists(VECTOR_DB):
            vectorstore=FAISS.load_local(
                VECTOR_DB,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("Loaded existing vector DB!")
            vectorstore.add_documents(doc_chunks)
            vectorstore.save_local(VECTOR_DB)
            print("Updated vector DB!")
        else:
            vectorstore = FAISS.from_documents(doc_chunks, embeddings)
            vectorstore.save_local(VECTOR_DB)
            print("Created new vector DB!")
        await update_user_dashboard(username,stats_changes={
                    "completed":1,
                    "pending":-1
                })
    except Exception as err:
        await update_user_dashboard(username,queue_changes={
                    "pending":-1,
                })
        return {"Error ",err}
    return {"Done analysing file!"}


@app.post("/query-document")
async def search_document(request:Request):
    print("Welcome ",request.state.user)
    body=await request.json()
    if os.path.exists(VECTOR_DB):
        vectorstore=FAISS.load_local(
            VECTOR_DB,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("Loaded existing vector DB!")
    else:
        print("No files to query!")
        return 
    retriever=vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k":5}
    )
    qa_chain=RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
    )
    query=body["query"]
    response=qa_chain.invoke({"query":query})
    print(response)
    return {"response":response}



@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket:WebSocket):
    jwt_token = websocket.cookies.get("jwt_token")
    await manager.connect(username,websocket)
    if not jwt_token:
        await websocket.close(code=1008)
        return
    
    try:
        payload=jwt.decode(jwt_token,JWT_SECRET_KEY,algorithms=ALGORITHM)
        sername=payload.get("sub")
        exp=payload.get("exp")
    except jwt.ExpiredSignatureError:
        await websocket.close(code=1008)
        return
    data=await get_dashboard_stats(username)
    await websocket.send_json({
        'username':username,'data':data
    })
    async def receive_loop():
        try:
            while True:
                msg = await websocket.receive_text()
        except Exception:
            pass

    async def token_monitor():
        try:
            remaining = exp - int(time.time())
            if remaining > 0:
                await asyncio.sleep(remaining)
            await websocket.send_json({"error": "token expired"})
            await websocket.close(code=1008)
        except Exception:
            pass

    receive_task = asyncio.create_task(receive_loop())
    monitor_task = asyncio.create_task(token_monitor())

    done, pending = await asyncio.wait(
        [receive_task, monitor_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    manager.disconnect(username, websocket)



@app.post("/schedule-jobs")
async def search_document(request:Request):
    print("Welcome ",request.state.user)
    body=await request.json()
    hour = int(body["hour"])
    minute = int(body["minute"])
    if body["period"] == "PM" and hour != 12:
        hour += 12
    if body["period"]== "AM" and hour == 12:
        hour = 0
    try:
        if body["frequency"]=="Every day":
            scheduler.add_job(read_root,trigger="cron",hour=hour,minute=minute,id="daily_job",kwargs={"username": username})
        elif body["frequency"]=="Every 6 hours":
            scheduler.add_job(read_root,trigger="interval",hours=6,start_date=datetime.now().replace(hour=hour, minute=minute, second=0),id="6hour_job",kwargs={"username": username})
        elif body["frequency"]=="Every 12 hours":
            scheduler.add_job(read_root,trigger="interval",hours=12,start_date=datetime.now().replace(hour=hour, minute=minute, second=0),id="12hour_job",kwargs={"username": username})
        elif body["frequency"]=="Weekly":
            scheduler.add_job(read_root,trigger="cron",day_of_week="mon",hour=hour,minute=minute,id="weekly_job",kwargs={"username": username})
        print("Successfully added job in job store.")
    except Exception as err:
        print("You have error scheduling jobs:    ",err)