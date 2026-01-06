from pydantic import ConfigDict, BaseModel, Field
from model import StatusEnum
from datetime import date,datetime

class EmailMetaDataOut(BaseModel):
    title: str
    status: StatusEnum
    received_at: datetime
    
    model_config = ConfigDict(from_attributes=True)