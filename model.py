
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime,BigInteger
from sqlalchemy.ext.asyncio import AsyncEngine
from enum import Enum
from sqlalchemy.orm import declarative_base,mapped_column,Mapped
Base=declarative_base()

class StatusEnum(str, Enum):
    pending = "pending"
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    incomplete = "incomplete"
    failed = "failed"
    rejected = "rejected"
    approved = "approved"


class User(Base):
    __tablename__="User"
    id=Column(Integer,primary_key=True)
    username=Column(String,nullable=False)
    password=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    disabed=Column(Boolean,default=False)

    def __repr__(self):
        return (
            f"<email_metadata("
            f"id={self.id}, "
            f"username={self.username}, "
            f"password={self.password})>"
            f"email={self.email}, "
            f"disabed={self.disabed}, "
        )
    
class Token(Base):
    __tablename__="Tokens"

    id=Column(Integer,primary_key=True)
    token=Column(String,nullable=False)
    user_id=Column(Integer,ForeignKey("User.id"))

    def __repr__(self):
        return (
            f"<Tokens("
            f"id={self.id}, "
            f"token={self.token}, "
            f"user_id={self.user_id})>"
        )


class email_metadata(Base):
    __tablename__="EmailData"
    id=Column(Integer,primary_key=True)
    imap_uid=Column(Integer,unique=True,nullable=False)
    subject=Column(String)
    mail_from=Column(String,nullable=False)
    received_at = mapped_column(DateTime,nullable=False)
    status:Mapped[StatusEnum]=mapped_column(default=StatusEnum.incomplete)
    # total_pdfs=Column(Integer)
    # processed_pdfs=Column(Integer,default=0)
    

    def __repr__(self):
        return (
            f"<email_metadata("
            f"id={self.id}, "
            f"imap_uid={self.imap_uid}, "
            f"subject={self.subject})>"
            f"mail_from={self.mail_from},"
            f"received_at={self.received_at}, "
            f"status={self.status},"
        )

class email_attachments_metadata(Base):
    __tablename__="AttachmentData"
    id=Column(Integer,primary_key=True)
    email_id=Column(Integer,ForeignKey("EmailData.id"))
    file_name=Column(String)
    file_size=Column(BigInteger)
    cloudinary_reportUrl=Column(String)
    status: Mapped[StatusEnum]=mapped_column(default=StatusEnum.pending)
    checksum_sha256: Mapped[str]=mapped_column()      

    def __repr__(self):
        return (
            f"<AttachmentData("
            f"id={self.id}, "
            f"email_id={self.email_id}, "
            f"file_name={self.file_name})>"
            f"file_size={self.file_size},"
            f"cloudinary_reportUrl={self.cloudinary_reportUrl}, "
            f"status={self.status},"
            f"checksum_sha256={self.checksum_sha256},"
        )