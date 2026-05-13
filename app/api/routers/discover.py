import json
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud
from app.database import get_db
from app.security import get_current_user_id
from app.schemas.userSchema import UserResponse
from app.schemas.swipeSchema import SwipeAction, SwipeResponse
from app.services.websocket_manager import manager

router = APIRouter(tags=["Discover"])

"""
Función get_users_to_discover:
    params:
        db
        token_user_id
        city
        rooms
        bathrooms
        tags
        
Devuelve una lista de usuarios aleatorios excluyendo al propio usuario y con los que ya ha interactuado
    
    returns:
        List[UserResponse]
"""
@router.get("/discover/users", response_model=List[UserResponse])
def get_users_to_discover(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id), 
                           city: Optional[str] = None, rooms: Optional[int] = None, bathrooms: Optional[int] = None, 
                           tags: Optional[List[str]] = Query(None)):
    return crud.get_discover_users(db=db, current_user_id=token_user_id, city=city, rooms=rooms, bathrooms=bathrooms, tags=tags)


"""
Función get_user_matches:
    params:
        db
        token_user_id
        
Devuelve la lista de usuarios con los que el usuario ha hecho match
    
    returns:
        List[UserResponse]
"""
@router.get("/matches", response_model=List[UserResponse])
def get_user_matches(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    return crud.get_user_matches(db, current_user_id=token_user_id)


"""
Función swipe_user:
    params:
        action
        db
        token_user_id
        
Registra un Like o Dislike en la base de datos, si hay match, envía una notificación por el socket al otro usuario
    
    returns:
        SwipeResponse
"""
@router.post("/discover/swipe", response_model=SwipeResponse)
async def swipe_user(action: SwipeAction, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    if token_user_id == action.swiped_id:
        raise HTTPException(status_code=400, detail="No puedes deslizarte a ti mismo")
    is_match = crud.record_swipe_and_check_match(db=db, swiper_id=token_user_id, swiped_id=action.swiped_id, is_like=action.is_like)
    if is_match:
        match_notification = {"type": "match", "sender_id": token_user_id, "receiver_id": action.swiped_id}
        await manager.send_personal_message(json.dumps(match_notification), action.swiped_id)    
    return {"mutual_match": is_match}