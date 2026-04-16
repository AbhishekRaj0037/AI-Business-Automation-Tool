from fastapi import APIRouter,Depends,Request,HTTPException,BackgroundTasks
from app.db.models import user as userModel
from app.services.email_service import process_dashboard
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session
from app.websockets.manager import r
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy import update
from fastapi.responses import RedirectResponse
import app.websockets.dashboard as websckt
import asyncio

router=APIRouter()


@router.get("/auth/gmail")
async def gmail_auth(request:Request,session:AsyncSession= Depends(get_session)):
    flow=Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=["https://mail.google.com/","https://www.googleapis.com/auth/userinfo.email","openid"],
        redirect_uri="http://localhost:8000/api/auth/gmail/callback"
    )
    auth_url,state=flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )
    await r.set(f"oauth_verifier:{state}", flow.code_verifier, ex=600)
    return auth_url

@router.get("/api/auth/gmail/callback")
async def gmail_callback(code:str,state:str,request:Request,session:AsyncSession= Depends(get_session)):
    code_verifier = await r.get(f"oauth_verifier:{state}")
    if not code_verifier:
        raise HTTPException(400, "Invalid or expired state")
    await r.delete(f"oauth_verifier:{state}")
    flow=Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=["https://mail.google.com/"],
        redirect_uri="http://localhost:8000/api/auth/gmail/callback"
    )
    flow.code_verifier = code_verifier
    await asyncio.to_thread(flow.fetch_token,code=code)
    credentials=flow.credentials
    service = await asyncio.to_thread(build,"gmail", "v1", credentials=credentials)
    profile = await asyncio.to_thread(service.users().getProfile(userId="me").execute)
    user=update(userModel.User).where(userModel.User.id==request.state.userId).values(email=profile["emailAddress"],refresh_token=credentials.refresh_token,access_token=credentials.token,token_expiry=credentials.expiry)
    await session.execute(user)
    await session.commit()
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        process_dashboard,
        userId=request.state.userId,
        username=request.state.username,
        session=session

    )
    await websckt.set_task_status(request.state.userId,"true")
    return RedirectResponse(
        url="http://localhost:3000/home?gmail=connected",
        status_code=302,
        background=background_tasks
    )
