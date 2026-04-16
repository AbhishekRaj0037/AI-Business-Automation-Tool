from sqlalchemy import select
from app.db.models.user import User
from datetime import datetime
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
import imaplib
import os



async def get_imap_connection(userId: str, session):
    result = await session.execute(select(User).where(User.id == userId))
    user = result.scalars().first()
    if user.email is None:
        return None
    
    if user.token_expiry and user.token_expiry < datetime.utcnow():
        credentials = Credentials(
            token=user.access_token,
            refresh_token=user.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret")
        )
        credentials.refresh(google.auth.transport.requests.Request())

        user.access_token = credentials.token
        user.token_expiry = credentials.expiry
        await session.commit()
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    auth_string = f"user={user.email}\x01auth=Bearer {user.access_token}\x01\x01"
    imap.authenticate("XOAUTH2", lambda x: auth_string.encode())
    return imap