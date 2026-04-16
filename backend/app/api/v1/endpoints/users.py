from fastapi import APIRouter,Depends,Request,HTTPException,UploadFile,File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update,select
from app.dependencies import get_session
from app.db.models import schedule,user as userModel
from io import BytesIO
from fastapi import APIRouter
import asyncio
import cloudinary
from  app.services.storage_service import cloudinary
import uuid

router=APIRouter()

@router.get("/user-details")
async def user_details(request:Request,session:AsyncSession= Depends(get_session)):
    result=await session.execute(select(userModel.User).where(userModel.User.id==request.state.userId))
    result=result.scalars().first()
    dashboard_detail=await session.execute(select(schedule.dashboard_schedules).where(schedule.dashboard_schedules.user_id==result.id))
    dashboard_detail=dashboard_detail.scalars().first()
    user={
        "email":result.email,
        "profile_photo_url": result.profile_photo,
        "username":result.username,
        "schedule":dashboard_detail
    }
    
    return user



@router.post("/upload-file")
async def update_file(request: Request,file:UploadFile=File(...),session:AsyncSession= Depends(get_session)):
    try:
        file_bytes = await file.read()
        file_stream = BytesIO(file_bytes)
        result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        file_stream,
        asset_folder="AI Business Automation Assistant",
        public_id=uuid.uuid4().hex,
        overwrite=True,
        resource_type="auto"
        )
        url = result["url"]
        result=update(userModel.User).where(userModel.User.id == request.state.userId).values(profile_photo=url)
        await session.execute(result)
        await session.commit()
        return {"url": url}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))