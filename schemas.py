from pydantic import ConfigDict, BaseModel
from model import StatusEnum
from datetime import datetime

class EmailMetaDataOut(BaseModel):
    status: StatusEnum
    mail_from: str
    received_at: datetime
    
    model_config = ConfigDict(from_attributes=True)