
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime
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

class email_metadata(Base):
    __tablename__="EmailData"
    id=Column(Integer,primary_key=True)
    imap_uid=Column(String,unique=True,nullable=False)
    total_pdfs=Column(Integer)
    processed_pdfs=Column(Integer,default=0)
    status:Mapped[StatusEnum]=mapped_column(default=StatusEnum.incomplete)
    mail_from=Column(String,nullable=False)
    subject=Column(String)
    received_at = mapped_column(DateTime,nullable=False)

class email_attachments_metadata(Base):
    __tablename__="AttachmentData"
    id=Column(Integer,primary_key=True)
    email_id=Column(Integer,ForeignKey("EmailData.id"))
    cloudinary_reportUrl=Column(String)
    status: Mapped[StatusEnum]=mapped_column(default=StatusEnum.pending)        