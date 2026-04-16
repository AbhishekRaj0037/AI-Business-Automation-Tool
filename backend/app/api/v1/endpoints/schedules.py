from dotenv import load_dotenv
load_dotenv()
from fastapi import Depends,Request
from datetime import datetime,time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from app.dependencies import get_session
from app.db.models import schedule,user as userModel
from fastapi import APIRouter
from app.db import enums


router=APIRouter()

@router.post("/schedule-jobs")
async def search_document(request:Request,session:AsyncSession= Depends(get_session)):
    print("Welcome ",request.state.username)
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
    schedule_update = (
    update(schedule.dashboard_schedules)
    .where(
        schedule.dashboard_schedules.user_id == (
            select(userModel.User.id)
            .where(userModel.User.username == request.state.username)
            .scalar_subquery()
        )
    )
    .values(
        schedule_frequency=enums.ScheduleEnum(body['frequency']),
        schedule_time=schedule_time,
        next_run_at=next_run_at,
        is_active=True
    )
)
    await session.execute(schedule_update)
    await session.commit()
    print("Successful time update")