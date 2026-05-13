from sqlalchemy import Boolean, Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

"""
Clase Message
propiedades:
    -id
    -sender_id
    -receiver_id
    -text
    -is_read
    -timestamp
"""
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    text = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())