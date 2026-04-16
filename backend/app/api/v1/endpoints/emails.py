from fastapi import APIRouter,Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session
from app.services.email_service import process_dashboard
import app.websockets.dashboard as websckt

router=APIRouter()

@router.get("/")
async def read_root(request:Request,session:AsyncSession= Depends(get_session)):
    await process_dashboard(request.state.userId,request.state.username,session)

@router.get("/stop-fetching")
async def stop_fetching(request:Request,session:AsyncSession= Depends(get_session)):
    await websckt.set_task_status(request.state.userId,"false")
    return {"status":"stopped"}

@router.get("/fetch-status")
async def fetch_status(request:Request,session:AsyncSession= Depends(get_session)):
    status=await websckt.websocket_dashboard.get_task_status(request.state.userId)
    return {"is_fetching":status=="true"}