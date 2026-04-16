from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Text
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

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

