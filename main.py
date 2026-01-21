from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Query,HTTPException,Depends,Request
from fastapi_sa_orm_filter.operators import Operators as ops
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
from model import StatusEnum
from schemas import EmailMetaDataOut
from pwdlib import PasswordHash
import cloudinary.uploader
from typing import List
import hashlib
import imaplib
import model
import email
import jwt
import os

from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
import langchain_community.document_loaders as docloader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_classic.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import OpenAI
from langchain_openai import AzureOpenAI




SQLAlchemyJobStoreURL=os.getenv("SQLAlchemyJobStore")
file_download_path=os.getenv("file_download_path")
openai_api_key=os.getenv("OPENAI_API_KEY")
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")


app=FastAPI()

mail= imaplib.IMAP4_SSL(imap_server)
mail.login(username,password)
mail.select("inbox")


ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_MINUTES=30*60

password_hash=PasswordHash.recommended()

llm= AzureOpenAI(
    api_version="2024-02-01",
    azure_endpoint="https://azure-open-ai-business-automation-tool.openai.azure.com/",
    api_key=openai_api_key,
    azure_deployment="text-embedding-3-large"
)

splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

embeddings=AzureOpenAIEmbeddings(
    api_version="2024-02-01",
    azure_endpoint="https://azure-open-ai-business-automation-tool.openai.azure.com/",
    api_key=openai_api_key,
    azure_deployment="text-embedding-3-large"
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


@app.on_event("startup")
def on_start():
    try:
        scheduler.start()
        print("Started scheduler successfully")
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


@app.get("/")
async def read_root():
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)).limit(1))
    result=result.scalars().first()
    starting_uid_range=0
    if result is not None:
         starting_uid_range=result.imap_uid
         uids=mail.uid('search', None, f'UID {starting_uid_range + 1}:*')
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
        is_uid_already_synced=await session.execute(select(model.email_metadata).where(model.email_metadata.imap_uid==int(uid)))
        is_uid_already_synced=is_uid_already_synced.scalars().first()
        if is_uid_already_synced is None:
            report_data=None
            report_data=model.email_metadata(imap_uid=int(uid),mail_from=mail_from,subject=subject,received_at=received_at)
            session.add(report_data)
            await session.commit()
            print("Added to DB")


@app.get("/get-all-reports")
async def get_all_reports():
    result=await session.execute(select(model.email_metadata).order_by(desc(model.email_metadata.imap_uid)))
    result=result.scalars().all()
    pass
   



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
        payload=jwt.decode(token,JWT_SECRET_KEY,algorithms=ALGORITHM)
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
    if password_hash.verify(body['password'],result.password)==False:
        print("Password Incorrect")
        return HTTPException(status_code=401,detail="Password Incorrect")
    
    access_token_expires=datetime.now(timezone.utc)+timedelta(minutes=3)
    user={"sub":result.username}
    user.update({"exp":access_token_expires})
    encode_jwt_token=jwt.encode(user,JWT_SECRET_KEY,algorithm=ALGORITHM)
    user=model.Token(token=encode_jwt_token,user_id=result.id)
    session.add(user)
    await session.commit()
    print("Added to DB")
    return {"Toke": encode_jwt_token,"Type":"Bearer"}


@app.post("/update-report-status")
async def update_report_status(request:Request):
    body=await request.json()
    report_id=body["report_id"]
    report_status=StatusEnum[body["report_status"]]
    report=update(model.email_attachments_metadata).where(model.email_attachments_metadata.id==int(report_id)).values(status=report_status)
    await session.execute(report)
    await session.commit()


@app.post("/analyse-report")
async def analyse_report(request:Request):
    body=await request.json()
    report_id=body["report_id"]
    loader=docloader.PyPDFLoader("Order_ID_7690337666.pdf")
    loaded_doc=loader.load()
    doc_chunks=splitter.split_documents(loaded_doc)
    vector_store=FAISS.from_documents(doc_chunks,embeddings)
    retriever=vector_store.as_retriever(
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


@app.post("/query-document")
async def search_document(request:Request):
    body=await request.json()
    pass


