from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime,BigInteger,Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base,mapped_column,Mapped
from enum import Enum
import uuid

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

class ScheduleEnum(str,Enum):
    everyday="everyday"
    every_six_hours="every_six_hours"
    every_twelve_hours="every_twelve_hours"
    weekly="weekly"
    disabled="disabled"


class User(Base):
    __tablename__="User"
    id=Column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    username=Column(String,nullable=False)
    password=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=True)
    profile_photo=Column(String,nullable=True)
    disabed=Column(Boolean,default=False)

    def __repr__(self):
        return (
            f"<email_metadata("
            f"id={self.id}, "
            f"username={self.username}, "
            f"password={self.password} "
            f"email={self.email}, "
            f"email={self.profile_photo}, "
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
    

class dashboard_schedules(Base):
    __tablename__="dashboard_update"
    id=Column(Integer,primary_key=True)
    user_id=Column(String,ForeignKey("User.id"))
    schedule_frequency:Mapped[ScheduleEnum]=mapped_column(default=ScheduleEnum.disabled)
    schedule_time=Column(DateTime, nullable=True, default=None)
    last_run_at=Column(DateTime, nullable=True, default=None)
    next_run_at=Column(DateTime, nullable=True, default=None)
    is_active=Column(Boolean,default=False)

    def __repr__(self):
        return (
            f"<dashboard_update("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"schedule_frequency={self.schedule_frequency})>"
            f"schedule_time={self.schedule_time},"
            f"last_run_at={self.last_run_at},"
            f"next_run_at={self.next_run_at},"
            f"is_active={self.is_active})>"
        )
    
class reports(Base):
    __tablename__="generated_reports"
    id=Column(Integer,primary_key=True)
    user_id=Column(String,ForeignKey("User.id"))
    report_name=Column(String)
    report_type=Column(String, nullable=False)
    tiptap_json=Column(JSONB,nullable=False)
    source_map=Column(JSONB,nullable=True)
    html_cache=Column(Text,nullable=True)
    s3_key=Column(String,nullable=True)
    export_format=Column(String,nullable=True)
    report_summary= Column(Text, nullable=True)
    generated_at= Column(DateTime, default=None)
    updated_at=Column(DateTime,default=None)
    
    def __repr__(self):
        return (
            f"<generated_reports("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"report_name={self.report_name}, "
            f"report_type={self.report_type}, "
            f"tiptap_json={self.tiptap_json}, "
            f"source_map={self.source_map}, "
            f"html_cache={self.html_cache}, "
            f"s3_key={self.s3_key}, "
            f"export_format={self.export_format}, "
            f"report_summary={self.report_summary}, "
            f"generated_at={self.generated_at}, "
            f"updated_at={self.updated_at})>"
        )

