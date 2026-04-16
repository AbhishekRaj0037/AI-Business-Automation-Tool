from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.workers.email_worker import run_scheduled_jobs
from app.config import settings

jobstores={
    'default' : SQLAlchemyJobStore(url=settings.SQLAlchemyJobStore)
}

executors={
    'default' : AsyncIOExecutor()
}

job_defaults={
    'coalesce' : True,
    'max_instance' : 3
}

scheduler=AsyncIOScheduler(jobstores=jobstores,executors=executors,job_defaults=job_defaults)


try:
    scheduler.add_job(run_scheduled_jobs,"cron",minute="*",id="dashboard_scheduler",replace_existing=True)
    print("Successfully added job in job store.")
except Exception as err:
    print("You have error scheduling jobs:    ",err)