from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime
from app.db.base import Base
import uuid

class User(Base):
    __tablename__="User"
    id=Column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    username=Column(String,nullable=False)
    password=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=True)
    profile_photo=Column(String,nullable=True)
    refresh_token=Column(String,nullable=True)
    access_token=Column(String,nullable=True)
    token_expiry=Column(DateTime,nullable=True)
    disabed=Column(Boolean,default=False)

    def __repr__(self):
        return (
            f"<email_metadata("
            f"id={self.id}, "
            f"username={self.username}, "
            f"password={self.password} "
            f"email={self.email}, "
            f"profile_photo={self.profile_photo}, "
            f"refresh_token={self.refresh_token}, "
            f"access_token={self.access_token}, "
            f"token_expiry={self.token_expiry}, "
            f"disabed={self.disabed})>"
        )
    
class Token(Base):
    __tablename__="Tokens"

    id=Column(Integer,primary_key=True)
    token=Column(String,nullable=False)
    user_id=Column(String,ForeignKey("User.id"))

    def __repr__(self):
        return (
            f"<Tokens("
            f"id={self.id}, "
            f"token={self.token}, "
            f"user_id={self.user_id})>"
        )
