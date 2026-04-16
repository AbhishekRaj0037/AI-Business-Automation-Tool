from app.dependencies import Session
from app.db.enums import ScheduleEnum
from sqlalchemy import select,update
from app.db.models import user as userModel
from app.db.models.schedule import dashboard_schedules as dashboardModel
from app.services.email_service import process_dashboard
from datetime import datetime,timedelta
import asyncio


async def process_single_schedule(schedule):
    async with Session() as session:
        result = await session.execute(
            select(userModel.User).where(userModel.User.id == schedule.user_id)
        )
        user = result.scalars().one()
        
        await process_dashboard(user.id, user.username, session)
        
        freq_hours = {
            ScheduleEnum.everyday: 24,
            ScheduleEnum.weekly: 168,
            ScheduleEnum.every_twelve_hours: 12,
            ScheduleEnum.every_six_hours: 6,
        }
        next_run_at = schedule.next_run_at + timedelta(
            hours=freq_hours[schedule.schedule_frequency]
        )
        try:
            await session.execute(
                update(dashboardModel)
                .where(dashboardModel.id == schedule.id, dashboardModel.user_id==user.id,)
                .values(last_run_at=schedule.next_run_at, next_run_at=next_run_at)
            )
            await session.commit()
        except Exception as e:
            print("Error occurred while saving",e)
        
        

async def run_scheduled_jobs():
    async with Session() as session:
        now = datetime.now()
        result = await session.execute(
            select(dashboardModel)
            .where(
                dashboardModel.next_run_at <= now,
                dashboardModel.is_active == True
            )
        )

        schedules = result.scalars().all()

    await asyncio.gather(
        *[process_single_schedule(s) for s in schedules],
        return_exceptions=True
    )