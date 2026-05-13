from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.database import get_db
from app.security import get_current_user_id
from app.schemas.userSchema import UserResponse, UserUpdate

router = APIRouter(tags=["Users"])

"""
Función get_unread_status:
    params:
        db
        token_user_id
        
Devuelve una lista con los IDs de los usuarios que han enviado mensajes no leídos al usuario actual
    
    returns:
        List[str]
"""
@router.get("/users/unread-status", response_model=List[str])
def get_unread_status(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    return crud.get_unread_senders(db, token_user_id)


"""
Función get_current_user_profile:
    params:
        db
        token_user_id
        
Obtiene la información completa del perfil del usuario logueado por su token
    
    returns:
        UserResponse
"""
@router.get("/users/me", response_model=UserResponse)
def get_current_user_profile(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    db_user = crud.get_user(db, user_id=token_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


"""
Función get_user_profile:
    params:
        user_id
        db
        current_user_id
        
Busca y devuelve la información pública del perfil de un usuario específico por au ID
    
    returns:
        UserResponse
"""
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: str, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    db_user = crud.get_user(db, user_id=user_id) 
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return db_user


"""
Función check_email:
    params:
        email
        db
        
Comprueba si el correo electrnico ya está registrado en la base de datos
    
    returns:
        diccionario
"""
@router.get("/users/check-email/{email}")
def check_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        return {"exists": True}
    return {"exists": False}


"""
Función update_user_profile:
    params:
        user_id
        user_update
        db
        token_user_id
        
Actualiza la información de un perfil, mirando primero que el que lo edita es su propietario
    
    returns:
        UserResponse
"""
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_profile(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    if user_id != token_user_id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para editar un perfil que no es tuyo"
        )
    
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return db_user