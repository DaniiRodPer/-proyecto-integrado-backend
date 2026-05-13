from sqlalchemy import Column, String, Integer, Text, Date, JSON
from sqlalchemy.orm import relationship
from app.database import Base

"""
Clase User
propiedades:
    -id
    -name
    -surname
    -email
    -hashed_password
    -birth_date
    -profile_pic_url
    -user_description
    -user_tags
    -creation_date
    
relaciones:
    -accommodation
"""
class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    profile_pic_url = Column(String(255), nullable=True)
    user_description = Column(Text, nullable=True)
    user_tags = Column(JSON, nullable=True)
    creation_date = Column(Integer, nullable=False)

    accommodation = relationship("Accommodation", back_populates="owner", uselist=False)