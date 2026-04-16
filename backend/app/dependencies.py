from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import ExpiredSignatureError
from sqlalchemy import delete
from app.db.models import user as userModel
from app.config import settings
from app.db.base import Session

EXCLUDED_PATHS = ["/login-user", "/create-user"]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request,call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)
        jwt_token = request.cookies.get("jwt_token")
        if not jwt_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )
        try:
            payload=jwt.decode(jwt_token,settings.JWT_SECRET_KEY,algorithms=settings.ALGORITHM)
            userId=payload.get("user_id")
            username=payload.get("username")
            if userId is None:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid credentials"}
                )
            request.state.userId = userId
            request.state.username=username
        except ExpiredSignatureError:
            payload = jwt.decode(
            jwt_token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.ALGORITHM,
            options={"verify_exp": False}
            )
            user_id = payload.get("user_id")
            async with Session() as session:
                await session.execute(
                delete(userModel.Token).where(userModel.Token.user_id == user_id)
                )
                await session.commit()
            response = JSONResponse(
                status_code=401,
                content={"detail": "Token expired"}
            )
            response.delete_cookie("jwt_token")
            return response
        except Exception as err:
            print("Error authenticating user: ",err)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        response = await call_next(request)
        return response
    


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session