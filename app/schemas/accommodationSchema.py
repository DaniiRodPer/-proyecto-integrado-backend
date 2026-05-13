from pydantic import BaseModel
from typing import List, Optional

"""
Clase AccommodationBase
propiedades:
    -city
    -description
    -square_meters
    -bathrooms
    -bedrooms
    -pics_urls
    -tags
    
Define los campos básicos de un alojamiento para la validación en las peticiones
"""
class AccommodationBase(BaseModel):
    city: str
    description: str
    square_meters: int
    bathrooms: int
    bedrooms: int
    pics_urls: List[str] = []
    tags: List[str] = []

class AccommodationCreate(AccommodationBase):
    pass

class AccommodationResponse(AccommodationBase):
    id: int
    owner_id: str

    class Config:
        from_attributes = True
        
class AccommodationUpdate(BaseModel):
    city: Optional[str] = None
    description: Optional[str] = None
    square_meters: Optional[int] = None
    bathrooms: Optional[int] = None
    bedrooms: Optional[int] = None
    pics_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None