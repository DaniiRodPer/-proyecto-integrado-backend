import uuid
import secrets
import string
import time
import random
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app import crud
from app.database import get_db
from app.security import create_access_token
from app.schemas.userSchema import (
    UserCreate, LoginRequest, TokenResponse, 
    GoogleAuthRequest, RecoverEmailRequest, ResetPasswordRequest, GoogleAuthResponse
)
from app.services.email_service import send_email_pin

router = APIRouter(tags=["Auth"])

recovery_codes = {}

"""
Función register_user:
    params:
        user
        db
        
Comprueba que el email no exista, guarda el nuevo usuario en la base de datos y devuelve el token de acceso
    
    returns:
        TokenResponse
"""
@router.post("/users/", response_model=TokenResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = crud.create_user(db=db, user=user)
    
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": new_user.id
    }


"""
Función login_user:
    params:
        login_data
        db
        
Verifica las credenciales del usuario y si son correctas genera un Token JWT de sesión
    
    returns:
        TokenResponse
"""
@router.post("/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint para iniciar sesión. Devuelve un Token JWT si tiene éxito.
    """
    #Comprueba las credenciales
    user = crud.authenticate_user(db, email=login_data.email, password=login_data.password)
    
    if not user:
        #Devuleve un error 401
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )
    
    #Crea el token. Dentro del token guardamos el ID del usuario
    access_token = create_access_token(data={"sub": user.id})
    
    #Devuelev el Token
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id
    }
    
    
"""
Función login_with_google:
    params:
        data
        db
        
Valida el token proporcionado por Google y si el usuario existe inicia sesión, si no genera una contraseña y lo registra
    
    returns:
        TokenResponse
"""
@router.post("/auth/google", response_model=GoogleAuthResponse) # <--- Usamos tu esquema completo
def login_with_google(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        GOOGLE_CLIENT_ID = "554855269813-sfhobfm3i9tbcrpav3af2pmfaq0ab92d.apps.googleusercontent.com"
        
        idinfo = id_token.verify_oauth2_token(data.token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email = idinfo['email']
        name = idinfo.get('given_name', idinfo.get('name', 'Usuario'))
        surname = idinfo.get('family_name', '')
        picture = idinfo.get('picture', '')
        
        user = crud.get_user_by_email(db, email=email)
        
        if not user:
            return {
                "access_token": "",
                "token_type": "bearer", 
                "user_id": str(uuid.uuid4()), 
                "is_new_user": True,
                "name": name,
                "surname": surname,
                "email": email,
                "profile_pic_url": picture
            }
        
        access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user_id": str(user.id),
            "is_new_user": False,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "profile_pic_url": user.profile_pic_url if user.profile_pic_url else ""
        }        
    except ValueError:
        raise HTTPException(status_code=401, detail="Token de Google inválido")


"""
Función request_recovery_pin:
    params:
        request
        db
        
Genera un numero de 4 dígitos aleatorio y envía el correo de recuperación si el email está registrado
    
    returns:
        diccionario
"""
@router.post("/users/recover-request")
def request_recovery_pin(request: RecoverEmailRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    
    if user:
        pin = str(random.randint(1000, 9999))
        recovery_codes[request.email] = pin
        send_email_pin(user.email, pin)
        
    return {"status": "ok", "message": "Si el correo existe, se ha enviado un PIN."}



"""
Función reset_password:
    params:
        request
        db
        
Comprueba que el PIN introducido coincida con el almacenado y actualiza la contraseña del usuario en BD
    
    returns:
        diccionario
"""
@router.post("/users/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    valid_pin = recovery_codes.get(request.email)
    if not valid_pin or valid_pin != request.pin:
        raise HTTPException(status_code=400, detail="El PIN es incorrecto o ha caducado.")
    
    user = crud.update_user_password(db, email=request.email, new_password=request.new_password)
    
    if user:
        del recovery_codes[request.email]
        
    return {"status": "success", "message": "Contraseña actualizada correctamente."}