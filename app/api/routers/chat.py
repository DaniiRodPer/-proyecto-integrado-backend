import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from app import crud
from app.database import get_db
from app.security import get_current_user_id
from app.schemas.messageSchema import MessageCreate, MessageResponse
from app.services.websocket_manager import manager

router = APIRouter(tags=["Chat"])

"""
Función websocket_endpoint:
    params:
        websocket
        user_id
        
Establece el canal de comunicación persistente con un usuario y lo destrye cuando el cliente se desconects
"""
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)


"""
Función get_chat_history:
    params:
        other_user_id
        db
        token_user_id
        
Consulta y devuelve el listado completo de mensajes enviados y recibidos entre dos usuarios ordenados por fecha
    
    returns:
        List[MessageResponse]
"""
@router.get("/messages/{other_user_id}", response_model=List[MessageResponse])
def get_chat_history(other_user_id: str, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    return crud.get_chat_messages(db, token_user_id, other_user_id)


"""
Función send_message:
    params:
        message
        db
        token_user_id
        
Inserta un nuevo mensaje en la BD y notifica al usuario receptor en tiempo real mediante su socket
    
    returns:
        MessageResponse
"""
@router.post("/messages", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    db_msg = crud.create_message(db, token_user_id, message)
    msg_dict = {"type": "message", "id": db_msg.id, "sender_id": db_msg.sender_id, "receiver_id": db_msg.receiver_id, "text": db_msg.text, "timestamp": db_msg.timestamp.isoformat()}
    await manager.send_personal_message(json.dumps(msg_dict), message.receiver_id)
    return db_msg


"""
Función mark_read:
    params:
        sender_id
        db
        token_user_id
        
Cambia el estado de los mensajes de un chat a como leídos en DB
    
    returns:
        diccionario
"""
@router.put("/messages/mark-read/{sender_id}")
def mark_read(sender_id: str, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    crud.mark_messages_as_read(db, token_user_id, sender_id)
    return {"status": "success"}