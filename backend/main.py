from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Query,HTTPException,Depends,Request,WebSocket,Response,Cookie,UploadFile,File
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from websocket_dashboard import ConnectionManager,update_user_dashboard,r
from fastapi_sa_orm_filter.operators import Operators as ops
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sa_orm_filter.main import FilterCore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import timezone,datetime,timedelta,time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,desc
from email.utils import parsedate_to_datetime
from DataBase import get_session,Session
import parse_files
from typing import Annotated
import websocket_dashboard
from model import StatusEnum,ScheduleEnum
from schemas import EmailMetaDataOut
from pwdlib import PasswordHash
from datetime import date,time
import cloudinary
import cloudinary.uploader
from pathlib import Path
from typing import List
from io import BytesIO
import uuid
import hashlib
import imaplib
import model
import email
import json
import asyncio
import pypdf
import boto3
import jwt
import os

from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
import langchain_community.document_loaders as docloader
from langchain_openai import OpenAIEmbeddings
from langchain_classic.vectorstores import FAISS

from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI

from email.message import Message

SQLAlchemyJobStoreURL=os.getenv("SQLAlchemyJobStore")
file_download_path=os.getenv("file_download_path")
GPT_MINI=os.getenv("GPT_MINI")
EMB3_SMALL=os.getenv("EMB3_SMALL")

JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")

aws_access_key=os.getenv("aws_access_key")
aws_secret_key=os.getenv("aws_secret_key")
aws_region=os.getenv("aws_region")

cloud_name=os.getenv("cloud_name")
api_key=os.getenv("api_key")
api_secret=os.getenv("api_secret")

SessionDep = Annotated[AsyncSession, Depends(get_session)]

cloudinary.config( 
  cloud_name = cloud_name,
  api_key = api_key,
  api_secret = api_secret,
)


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
            userId=payload.get("user_id")
            username=payload.get("username")
            if userId is None:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid credentials"}
                )
            request.state.userId = userId
            request.state.username=username
        except Exception as err:
            print("Error authenticating user: ",err)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

       
        response = await call_next(request)
        
        return response
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager=ConnectionManager()

mail= imaplib.IMAP4_SSL(imap_server)
mail.login(username,password)
mail.select("inbox")


VECTOR_DB=os.getenv("VECTOR_DB")

llm = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    api_key=GPT_MINI,
    base_url="https://models.github.ai/inference",
)
 
splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=EMB3_SMALL,
    base_url="https://models.github.ai/inference",
    tiktoken_model_name="text-embedding-3-small",
    check_embedding_ctx_length=False,
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


async def get_dashboard_stats(userId: str):
    today = date.today().isoformat()
    queue_key = f"userId:{userId}:queue"
    stats_key = f"userId:{userId}:stats:{today}"

    queue = await websocket_dashboard.r.hgetall(queue_key)
    stats = await websocket_dashboard.r.hgetall(stats_key)
    return {
        "queue": queue,
        "stats": stats
    }

async def redis_listener():
    pubsub =r.pubsub()
    await pubsub.psubscribe("userId:*:updates")

    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            data = json.loads(message["data"])
            userId = data["userId"]
            
            # fetch latest stats from Redis
            stats = await get_dashboard_stats(userId)
            
            # push to correct websocket user
            await manager.send(userId, stats)
            

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
async def read_root(request:Request,session: SessionDep):
    await websocket_dashboard.set_task_status(request.state.userId,"true")
    await process_dashboard(request.state.userId,session,"manual")

@app.get("/stop-fetching")
async def stop_fetching(request:Request,session: SessionDep):
    await websocket_dashboard.set_task_status(request.state.userId,"false")
    return {"status":"stopped"}

@app.get("/fetch-status")
async def fetch_status(request:Request,session: SessionDep):
    status=await websocket_dashboard.get_task_status(request.state.userId)
    return {"is_fetching":status=="true"}

async def process_dashboard(userId,session,fetch_type):
    print("Welcome ",userId)
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)).limit(1))
    result=result.scalars().first()
    starting_uid_range=0
    if result is not None:
         starting_uid_range=result.imap_uid
    uids=mail.uid('search', None, f'UID {starting_uid_range + 1}:*')
    uid_list=uids[1][0].split()
    for uid in uid_list:
        status=await websocket_dashboard.get_task_status(userId)
        if fetch_type== "manual" and status != "true":
            print(f"Stopped fetching for {userId}")
            break
        print(f"Fetching emails for {userId}...")
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
                        ext=Path(filename).suffix
                        unique_id=uuid.uuid4().hex
                        s3_key=f"uploads/{userId}/{unique_id}{ext}"
                        s3.put_object(Bucket="amzn-s3-bucket-ai-business-automation-assistant",Key=f"{s3_key}",Body=file_bytes)
                        print("File uploaded succesfully on aws bucket")
                        file_data=None
                        content_type = part.get_content_type()
                        file_data=model.email_attachments_metadata(imap_uid=int(uid),file_name=filename,file_type=content_type,file_size=len(file_bytes),status=StatusEnum.incomplete,checksum_sha256="!231231231231!",s3_key=s3_key)
                        session.add(file_data)
                    except Exception as e:
                        print("Error:  ",e)
            await update_user_dashboard(username,stats_changes={
                "fetch_today":1
            })
            print("Added to DB")


@app.get("/get-all-reports")
async def get_all_reports(session: SessionDep,request:Request,page:int=Query(1),limit:int=Query(4)):
    print("Welcome ",request.state.userId)
    offset=(page-1)*limit
    result=await session.execute(select(model.email_metadata).offset(offset).order_by(desc(model.email_metadata.imap_uid)).limit(limit))
    result=result.scalars().all()
    return result
   
@app.get("/get-reports-by-id")
async def get_all_reports(session: SessionDep,request:Request,imap_uid:int=Query(1),page:int=Query(1),limit:int=Query(4)):
    print("Welcome ",request.state.userId)
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
            'Key': result.s3_key,
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
    session: SessionDep,
    request:Request,
    objects_filter: str =Query(default=''),
) -> List[EmailMetaDataOut]:
    print("Welcome ",request.state.userId)
    filter_result=FilterCore(model.email_metadata,my_objects_filter)
    query=filter_result.get_query(objects_filter)
    db_obj=await session.execute(query)
    instance=db_obj.scalars().all()
    return instance



@app.post("/fetch-mail-data")
async def get_mail(
    session: SessionDep,
    imap_uid:str,
    request:Request,
):  
    print("Welcome ",request.state.userId)
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
    if is_uid_already_present:
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
async def create_user(session: SessionDep,request: Request):
    body = await request.json()
    result=await session.execute(select(model.User).where(model.User.email==body['email']))
    result=result.scalars().all()
    if result != []:
        print("User already exsist")
        return
    hashed_password= password_hash.hash(body['password'])
    user=model.User(username=body['name'],password=hashed_password,email=body['email'])
    session.add(user)
    await session.commit()
    await session.refresh(user)
    schedule_update=model.dashboard_schedules(user_id=int(user.id),schedule_frequency=ScheduleEnum.disabled,is_active=False)
    session.add(schedule_update)
    await session.commit()
    print("User Added to DB")
    return {"Status":200,"details":"User Added successfully"}

@app.post("/login-user")
async def login_user(session: SessionDep,request:Request,response:Response):
    body=await request.json()
    result=await session.execute(select(model.User).where(model.User.email==body['email']))
    result=result.scalars().first()
    if result is None:
        print("User doesn't exsist")
        raise HTTPException(status_code=404,detail="User doesn't exsist")
    if password_hash.verify(body['password'],result.password)==False:
        print("Password Incorrect")
        raise HTTPException(status_code=401,detail="Password Incorrect")
    
    access_token_expires=datetime.now(timezone.utc)+timedelta(minutes=30)
    user={"user_id":result.id,"username":result.username,"email_id":result.email}
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


@app.post("/change-password")
async def change_password(session: SessionDep,request: Request):
    body = await request.json()
    result=await session.execute(select(model.User).where(model.User.id==int(request.state.userId)))
    result=result.scalars().first()
    if result is None:
        print("User doesn't exsist")
        return
    if body["new_password"] != body["confirm_new_password"]:
        print("New password and confirm new password don't match")
        raise HTTPException(status_code=401,detail="Password missmatch")
    if password_hash.verify(body['current_password'],result.password)==False:
        print("Password Incorrect")
        raise HTTPException(status_code=401,detail="Password Incorrect")
    hashed_password= password_hash.hash(body['new_password'])
    result=update(model.User).where(model.User.id == request.state.userId).values(password=hashed_password)
    await session.execute(result)
    await session.commit()
    print("Password changed successfully")
    return {"Status":200,"details":"Password changed successfully"}

@app.get("/user-details")
async def user_details(session: SessionDep,request:Request):
    result=await session.execute(select(model.User).where(model.User.id==request.state.userId))
    result=result.scalars().first()
    dashboard_detail=await session.execute(select(model.dashboard_schedules).where(model.dashboard_schedules.user_id==result.id))
    dashboard_detail=dashboard_detail.scalars().first()
    user={
        "email":result.email,
        "profile_photo_url": result.profile_photo,
        "username":result.username,
        "schedule":dashboard_detail
    }
    
    return user

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("jwt_token")
    return {"message": "Logged out"}

@app.post("/upload-file")
async def update_file(session: SessionDep,request: Request,file:UploadFile=File(...)):
    try:
        file_bytes = await file.read()
        file_stream = BytesIO(file_bytes)
        result = cloudinary.uploader.upload(
            file_stream,
            asset_folder="AI Business Automation Assistant",
            public_id=file.filename,
            overwrite=True,
            resource_type="auto"
        )
        url = result["url"]
        result=update(model.User).where(model.User.id == int(request.state.userId)).values(profile_photo=url)
        await session.execute(result)
        await session.commit()
        return {"url": url}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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
async def update_report_status(session: SessionDep,request:Request):
    print("Welcome ",request.state.userId)
    body=await request.json()
    report_id=body["report_id"]
    report_status=StatusEnum[body["report_status"]]
    report=update(model.email_attachments_metadata).where(model.email_attachments_metadata.id==int(report_id)).values(status=report_status)
    await session.execute(report)
    await session.commit()

@app.get("/get-all-ai-reports")
async def get_all_ai_reports(session: SessionDep,request:Request,page:int=Query(1),limit:int=Query(4)):
    print("Welcome ",request.state.userId)
    offset=(page-1)*limit
    result=await session.execute(select(model.reports).offset(offset).order_by(desc(model.reports.id)).limit(limit))
    result=result.scalars().all()
    return result

@app.get("/get-ai-reports-by-id")
async def get_all_ai_reports(session: SessionDep,request:Request,report_id:str):
    print("Welcome ",request.state.userId)
    report_result=await session.execute(select(model.reports).where(model.reports.id==int(report_id)))
    report_result=report_result.scalars().first()
    url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': "amzn-s3-bucket-ai-business-automation-assistant",
        'Key': report_result.report_name,
        'ResponseContentDisposition': 'inline',
        'ResponseContentType': report_result.report_type
    },
    ExpiresIn=300
)
    result={"report_url":url}
    return result

@app.post("/analyse-report")
async def analyse_report(session: SessionDep,request:Request):
    print("Welcome ",request.state.username)
    body=await request.json()
    file_name=body["file_name"]
    s3_key=body["s3_key"]
    report_id=body["report_id"]
    report_result=await session.execute(select(model.email_attachments_metadata).where(model.email_attachments_metadata.id==int(report_id)))
    report_result=report_result.scalars().first()
    if report_result.status==StatusEnum.completed:
        return {"status":"Report already analysed"}
    try:
        await update_user_dashboard(request.state.userId,queue_changes={
                    "pending":1,
                })
        response=s3.get_object(
            Bucket="amzn-s3-bucket-ai-business-automation-assistant",
            Key=s3_key
        )
        file_bytes=response["Body"].read()
        loaded_docs=parse_files.parse_file(file_bytes,file_name,s3_key)
        doc_chunks=splitter.split_documents(loaded_docs)
        if os.path.exists(VECTOR_DB):
            vectorstore=FAISS.load_local(
                VECTOR_DB,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("Loaded existing vector DB!")
            vectorstore.add_documents(doc_chunks)
            print("Updated vector DB!")
        else:
            vectorstore = FAISS.from_documents(doc_chunks, embeddings)
            print("Created new vector DB!")
        vectorstore.save_local(VECTOR_DB)
        result=update(model.email_attachments_metadata).where(model.email_attachments_metadata.id == report_id).values(status=StatusEnum.completed)
        await session.execute(result)
        await session.commit()
        await update_user_dashboard(request.state.userId,stats_changes={
                    "completed":1,
                    "pending":-1
                })
    except Exception as err:
        await update_user_dashboard(request.state.userId,queue_changes={
                    "pending":-1,
                })
        raise HTTPException(status_code=500, detail=str(err))
    return {"status": "done", "chunks": len(doc_chunks)}


@app.post("/query-document")
async def search_document(session: SessionDep,request:Request):
    print("Welcome ",request.state.userId)
    body=await request.json()
    query=body["query"]
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
    try:
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k":10}
        )
        retrieved_docs=retriever.invoke(query)
        context_parts = []
        source_map = {}
        for i, doc in enumerate(retrieved_docs):
            chunk_id = f"chunk_{i}"
            context_parts.append(f"[SOURCE:{chunk_id}]\n{doc.page_content}")
            # doc.metadata comes from how you ingested the documents
            for i, doc in enumerate(retrieved_docs):
                chunk_id = f"chunk_{i}"
                context_parts.append(f"[SOURCE:{chunk_id}]\n{doc.page_content}")
                file_type = doc.metadata.get("file_type", "")
                source = {
                    "s3_key": doc.metadata.get("s3_key", ""),
                    "file_name": doc.metadata.get("file_name", "unknown"),
                    "file_type": file_type,
                }
                if file_type == "pdf":
                    source["page"] = doc.metadata.get("page", None)

                elif file_type == "excel":
                    source["sheet"] = doc.metadata.get("sheet", None)
                    source["row_count"] = doc.metadata.get("row_count", None)

                elif file_type == "docx":
                    source["section"] = doc.metadata.get("section", None)

                source_map[chunk_id] = source
        context = "\n\n".join(context_parts)
        system_prompt = """You are a report generator. Given context from source documents,
    generate a structured report. Respond ONLY with valid JSON, no markdown, no backticks.

    The JSON must have this exact structure:
    {
    "report_name": "short descriptive filename like food_order_analysis.pdf",
    "report_type": "one of: order_report, policy_report, financial_report, general_report",
    "report_summary": "2-3 sentence summary of what this report contains",
    "tiptap_json": {
        "type": "doc",
        "content": [
        {
            "type": "heading",
            "attrs": {"level": 2, "sources": ["chunk_0"]},
            "content": [{"type": "text", "text": "Your heading here"}]
        },
        {
            "type": "paragraph",
            "attrs": {"sources": ["chunk_0", "chunk_1"]},
            "content": [{"type": "text", "text": "Your paragraph here"}]
        },
        {
            "type": "table",
            "attrs": {"sources": ["chunk_2"]},
            "content": [
            {
                "type": "tableRow",
                "content": [
                {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Column Name"}]}]}
                ]
            },
            {
                "type": "tableRow",
                "content": [
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Cell value"}]}]}
                ]
            }
            ]
        }
        ]
    }
    }

    RULES:
    - Every node (heading, paragraph, table) MUST have attrs.sources with the chunk IDs used
    - Tables MUST wrap text inside paragraph nodes within cells
    - Use the SOURCE IDs provided in the context (like chunk_0, chunk_1)
    - report_name should be a clean filename with no spaces (use underscores)
    """

        response = await llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nGenerate a report for: {query}"}
        ])
        result = json.loads(response.content)
        breakpoint()
        report_data=model.reports(
            user_id=request.state.userId,
            report_name=result["report_name"],
            report_type=result["report_type"],
            report_summary=result["report_summary"],
            tiptap_json=result["tiptap_json"],
            source_map=source_map,
            generated_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(report_data)
        await session.commit()
        print("Added to DB")
        print(response)
    except Exception as e:
        print("Error occured: ",e)
        return 
    return {
        "report_id": report_data.id,
        "report_name": report_data.report_name,
        "report_type": report_data.report_type,
        "report_summary": report_data.report_summary,
        "tiptap_json": report_data.tiptap_json,
        "source_map": report_data.source_map,
    }



@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket:WebSocket):
    jwt_token = websocket.cookies.get("jwt_token")
    await websocket.accept()
    if not jwt_token:
        await websocket.close(code=1008)
        return
    try:
        payload=jwt.decode(jwt_token,JWT_SECRET_KEY,algorithms=ALGORITHM)
        userId=payload.get("user_id")
        exp=payload.get("exp")
    except jwt.ExpiredSignatureError:
        await websocket.close(code=1008)
        return
    await manager.connect(userId,websocket)
    data=await get_dashboard_stats(userId)
    await websocket.send_json({
        'userId':userId,'data':data
    })
    async def token_monitor():
        try:
            remaining = exp - int(time.time())
            if remaining > 0:
                await asyncio.sleep(remaining)
            await websocket.send_json({"error": "token expired"})
            await websocket.close(code=1008)
        except Exception as e:
            print("monitor error:", e)

    async def receive_loop():
        try:
            while True:
                await websocket.receive_text()
        except Exception as e:
            print("Data receive error:", e)

    monitor_task = asyncio.create_task(token_monitor())
    receive_task = asyncio.create_task(receive_loop())

    done, pending = await asyncio.wait(
        [monitor_task, receive_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    manager.disconnect(userId, websocket)



@app.post("/schedule-jobs")
async def search_document(session: SessionDep,request:Request):
    print("Welcome ",request.state.userId)
    body=await request.json()
    hour = int(body["hour"])
    minute = int(body["minute"])
    if body["period"] == "PM" and hour != 12:
        hour += 12
    if body["period"]== "AM" and hour == 12:
        hour = 0
    schedule_time=time(hour=hour, minute=minute)
    now = datetime.now()
    next_run_at = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=schedule_time.hour,
        minute=schedule_time.minute,
        second=0,
        microsecond=0
)
    schedule_time = datetime.combine(datetime.now().date(), schedule_time)
    # schedule_update=update(model.dashboard_schedules).where(model.dashboard_schedules.user_id==model.User.id).where(model.User.username==request.state.username).values(schedule_frequency=ScheduleEnum(body['frequency']),schedule_time=schedule_time,next_run_at=next_run_at,is_active=True)
    schedule_update = (
    update(model.dashboard_schedules)
    .where(
        model.dashboard_schedules.user_id == (
            select(model.User.id)
            .where(model.User.username == request.state.username)
            .scalar_subquery()
        )
    )
    .values(
        schedule_frequency=ScheduleEnum(body['frequency']),
        schedule_time=schedule_time,
        next_run_at=next_run_at,
        is_active=True
    )
)
    await session.execute(schedule_update)
    await session.commit()
    print("Successful time update")

async def run_scheduled_jobs():
    async with Session() as session:
        async with session.begin():
            now = datetime.now()
            result = await session.execute(
                select(model.dashboard_schedules)
                .where(
                    model.dashboard_schedules.next_run_at <= now,
                    model.dashboard_schedules.is_active == True
                )
            )

            schedules = result.scalars().all()

            for schedule in schedules:
                user_id=schedule.user_id
                result=await session.execute(select(model.User).where(model.User.id==int(user_id))) 
                result=result.scalars().one()
                # await process_dashboard(result.username,session,"auto")
                next_run_at=schedule.next_run_at
                if schedule.schedule_frequency==ScheduleEnum.everyday:
                    next_run_at=next_run_at+timedelta(hours=24)
                if schedule.schedule_frequency==ScheduleEnum.weekly:
                    next_run_at=next_run_at+timedelta(hours=168)
                if schedule.schedule_frequency==ScheduleEnum.every_twelve_hours:
                    next_run_at=next_run_at+timedelta(hours=12)
                if schedule.schedule_frequency==ScheduleEnum.every_six_hours:
                    next_run_at=next_run_at+timedelta(hours=6)  
                next_run=update(model.dashboard_schedules).where(model.dashboard_schedules.id==schedule.id).values(last_run_at=schedule.next_run_at,next_run_at=next_run_at)
                await session.execute(next_run)



try:
    scheduler.add_job(run_scheduled_jobs,"cron",minute="*",id="dashboard_scheduler",replace_existing=True)
    print("Successfully added job in job store.")
except Exception as err:
    print("You have error scheduling jobs:    ",err)