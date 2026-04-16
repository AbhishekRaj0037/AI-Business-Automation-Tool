from fastapi import APIRouter
from app.api.v1.endpoints import auth,emails,gmail,reports,schedules,users

api_router=APIRouter()

api_router.include_router(auth.router)
api_router.include_router(emails.router)
api_router.include_router(gmail.router)
api_router.include_router(reports.router)
api_router.include_router(schedules.router)
api_router.include_router(users.router)
