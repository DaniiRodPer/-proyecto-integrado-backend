from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

"""
Clase Accommodation
propiedades:
    -id
    -city
    -description
    -square_meters
    -bathrooms
    -bedrooms
    -pics_urls
    -tags
    -owner_id
    
relaciones:
    -owner
"""
class Accommodation(Base):
    __tablename__ = "accommodations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    square_meters = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    pics_urls = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)

    owner_id = Column(String(50), ForeignKey("users.id"))
    owner = relationship("User", back_populates="accommodation")