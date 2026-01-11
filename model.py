
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
            f"total_pdfs={self.total_pdfs},"
            f"processed_pdfs={self.processed_pdfs},"
            f"status={self.status},"
            f"mail_from={self.mail_from},"
            f"received_at={self.received_at}, "
            f"subject={self.subject})>"
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