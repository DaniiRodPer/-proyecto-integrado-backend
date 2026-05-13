from typing import Dict
from fastapi import WebSocket

"""
Clase ConnectionManager
propiedades:
    -active_connections
    
funciones:
    -connect
    -disconnect
    -send_personal_message
"""
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    """
    Función connect:
        params:
            websocket
            user_id
            
    Acepta la conexión de un nuevo WebSocket y lo almacena en un diccionario de conexiones activas
    """
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket


    """
    Función disconnect:
        params:
            user_id
            
    Borra la conexión del diccionario cuando el usuario cierra la aplicación o pierde conexión
    """
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]


    """
    Función send_personal_message:
        params:
            message
            receiver_id
            
    Busca al destinatario en las conexiones activas y le envía un mensaje por el socket
    """
    async def send_personal_message(self, message: str, receiver_id: str):
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            await websocket.send_text(message)

manager = ConnectionManager()