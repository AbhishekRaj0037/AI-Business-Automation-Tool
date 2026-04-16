from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime
from sqlalchemy.orm import mapped_column,Mapped,mapped_column,Mapped
from app.db.enums import ScheduleEnum
from app.db.base import Base

class dashboard_schedules(Base):
    __tablename__="dashboard_update"
    id=Column(Integer,primary_key=True)
    user_id=Column(String,ForeignKey("User.id"))
    schedule_frequency:Mapped[ScheduleEnum]=mapped_column(default=ScheduleEnum.disabled)
    schedule_time=Column(DateTime, nullable=True, default=None)
    last_run_at=Column(DateTime, nullable=True, default=None)
    next_run_at=Column(DateTime, nullable=True, default=None)
    is_active=Column(Boolean,default=False)

    def __repr__(self):
        return (
            f"<dashboard_update("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"schedule_frequency={self.schedule_frequency})>"
            f"schedule_time={self.schedule_time},"
            f"last_run_at={self.last_run_at},"
            f"next_run_at={self.next_run_at},"
            f"is_active={self.is_active})>"
        )
    