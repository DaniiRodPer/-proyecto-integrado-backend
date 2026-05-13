from pydantic import BaseModel
from datetime import datetime

"""
Clase MessageCreate
propiedades:
    -receiver_id
    -text
    
Defie el esquema para validar al enviar un mensaje
"""
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