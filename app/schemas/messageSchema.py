from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    receiver_id: str
    text: str

class MessageResponse(BaseModel):
    id: int
    sender_id: str
    receiver_id: str
    text: str
    timestamp: datetime

    class Config:
        from_attributes = True