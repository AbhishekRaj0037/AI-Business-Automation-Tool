from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,BigInteger
from sqlalchemy.orm import mapped_column,Mapped
from app.db.enums import StatusEnum
from app.db.base import Base


class email_metadata(Base):
    __tablename__="EmailData"
    id=Column(Integer,primary_key=True)
    user_id=Column(String,ForeignKey("User.id"))
    imap_uid=Column(Integer,unique=True,nullable=False)
    subject=Column(String)
    body=Column(String)
    mail_from=Column(String,nullable=False)
    received_at = mapped_column(DateTime,nullable=False)
    status:Mapped[StatusEnum]=mapped_column(default=StatusEnum.incomplete)
    
    def __repr__(self):
        return (
            f"<email_metadata("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"imap_uid={self.imap_uid}, "
            f"subject={self.subject}"
            f"body={self.body})>"
            f"mail_from={self.mail_from},"
            f"received_at={self.received_at}, "
            f"status={self.status})>"
        )

class email_attachments_metadata(Base):
    __tablename__="AttachmentData"
    id=Column(Integer,primary_key=True)
    user_id=Column(String,ForeignKey("User.id"))
    imap_uid=Column(Integer,ForeignKey("EmailData.imap_uid"))
    s3_key=Column(String)
    file_name=Column(String)
    file_type=Column(String)
    file_size=Column(BigInteger)
    status: Mapped[StatusEnum]=mapped_column(default=StatusEnum.pending)
    checksum_sha256: Mapped[str]=mapped_column()      

    def __repr__(self):
        return (
            f"<AttachmentData("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"imap_uid={self.imap_uid}, "
            f"s3_key={self.s3_key}, "
            f"file_name={self.file_name})>"
            f"file_size={self.file_size},"
            f"status={self.status},"
            f"checksum_sha256={self.checksum_sha256})>"
        )
    
