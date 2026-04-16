from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,Request,Response,HTTPException
from app.core.limiter import limiter
from pwdlib import PasswordHash
from app.dependencies import get_session
from sqlalchemy import select,update,delete
from app.db.models import schedule,user as userModel
from datetime import timezone,datetime,timedelta
from app.db import enums
from app.config import settings
import jwt


password_hash=PasswordHash.recommended()

router=APIRouter()

@router.post("/create-user")
@limiter.limit("5/minute")
async def create_user(request: Request,session:AsyncSession= Depends(get_session)):
    body = await request.json()
    result=await session.execute(select(userModel.User).where(userModel.User.username==body['name']))
    result=result.scalars().all()
    if result != []:
        print("User already exsist")
        return
    hashed_password= password_hash.hash(body['password'])
    user=userModel.User(username=body['name'],password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    schedule_update=schedule.dashboard_schedules(user_id=user.id,schedule_frequency=enums.ScheduleEnum.disabled,is_active=False)
    session.add(schedule_update)
    await session.commit()
    print("User Added to DB")
    return {"Status":200,"details":"User Added successfully"}

@router.post("/login-user")
@limiter.limit("5/minute")
async def login_user(request:Request,response:Response,session:AsyncSession= Depends(get_session)):
    body=await request.json()
    result=await session.execute(select(userModel.User).where(userModel.User.username==body['name']))
    result=result.scalars().first()
    if result is None:
        print("User doesn't exsist")
        raise HTTPException(status_code=404,detail="User doesn't exsist")
    if password_hash.verify(body['password'],result.password)==False:
        print("Password Incorrect")
        raise HTTPException(status_code=401,detail="Password Incorrect")
    
    access_token_expires=datetime.now(timezone.utc)+timedelta(minutes=30)
    user={"user_id":result.id,"username":result.username}
    user.update({"exp":access_token_expires})
    encode_jwt_token=jwt.encode(user,settings.JWT_SECRET_KEY,algorithm=settings.ALGORITHM)
    existing=await session.execute(
    select(userModel.Token).where(userModel.Token.user_id == result.id)
)
    existing_token=existing.scalars().first()
    if existing_token:
        existing_token.token=encode_jwt_token
    else:
        user=userModel.Token(token=encode_jwt_token,user_id=result.id)
        session.add(user)
    await session.commit()
    response.set_cookie(
        key="jwt_token",
        value=encode_jwt_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    print("Added to DB")
    print("Login successfully")
    return {"Token": encode_jwt_token,"Type":"Bearer","message":"Login Successful"}


@router.post("/change-password")
@limiter.limit("5/minute")
async def change_password(request: Request,response:Response,session:AsyncSession= Depends(get_session)):
    body = await request.json()
    result=await session.execute(select(userModel.User).where(userModel.User.id==request.state.userId))
    result=result.scalars().first()
    if result is None:
        print("User doesn't exsist")
        return
    if body["new_password"] != body["confirm_new_password"]:
        print("New password and confirm new password don't match")
        raise HTTPException(status_code=401,detail="Password missmatch")
    if password_hash.verify(body['current_password'],result.password)==False:
        print("Password Incorrect")
        raise HTTPException(status_code=401,detail="Password Incorrect")
    hashed_password= password_hash.hash(body['new_password'])
    result=update(userModel.User).where(userModel.User.id == request.state.userId).values(password=hashed_password)
    await session.execute(result)
    await session.commit()
    print("Password changed successfully")
    await session.execute(
        delete(userModel.Token).where(userModel.Token.user_id==request.state.userId)
    )
    await session.commit()
    response.delete_cookie("jwt_token")
    return {"Status":200,"details":"Password changed successfully"}


@router.post("/logout")
@limiter.limit("5/minute")
async def logout(request:Request,response: Response,session:AsyncSession= Depends(get_session)):
    await session.execute(
        delete(userModel.Token).where(userModel.Token.user_id==request.state.userId)
    )
    await session.commit()
    response.delete_cookie("jwt_token")
    return {"message": "Logged out"}