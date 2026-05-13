from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional
from .accommodationSchema import AccommodationResponse, AccommodationCreate, AccommodationUpdate

"""
Clase UserResponse
propiedades:
    -id
    -name
    -surname
    -email
    -birth_date
    -profile_pic_url
    -user_tags
    -user_description
    -creation_date
    -accommodation
    
Clase de Pydantic para validar los datos que envia la api.
"""
class UserBase(BaseModel):
    id: str
    name: str
    surname: str
    email: EmailStr
    birth_date: date
    profile_pic_url: str
    user_tags: List[str] = []
    user_description: str
    creation_date: int

class UserCreate(UserBase):
    password: str
    accommodation: Optional[AccommodationCreate] = None 

class UserResponse(UserBase):
    accommodation: Optional[AccommodationResponse] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    profile_pic_url: Optional[str] = None
    user_description: Optional[str] = None
    user_tags: Optional[List[str]] = None
    
    accommodation: Optional[AccommodationUpdate] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    
class GoogleAuthRequest(BaseModel):
    token: str
    
class RecoverEmailRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    pin: str
    new_password: str