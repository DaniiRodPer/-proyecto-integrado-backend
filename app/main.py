import os
import shutil
import uuid
import json
import secrets
import string
import time
import smtplib
import random

from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app import crud
from app.schemas.userSchema import (
    UserCreate, UserResponse, UserUpdate, LoginRequest, TokenResponse, 
    GoogleAuthRequest, RecoverEmailRequest, ResetPasswordRequest
)
from app.database import SessionLocal, engine, Base
from app.security import create_access_token, get_current_user_id
from app.schemas.swipeSchema import SwipeAction, SwipeResponse
from app.schemas.messageSchema import MessageCreate, MessageResponse
from app.models.message import Message
from dotenv import load_dotenv
from email.mime.image import MIMEImage

from typing import Dict

load_dotenv()
BASE_URL_IP = os.getenv("BASE_URL_IP", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

recovery_codes = {}

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def send_email_pin(recipient: str, pin: str):
    """Function to send the recovery email with Dovelia typography and embedded logo"""
    try:
        font_url = f"http://{BASE_URL_IP}:{PORT}/static/fonts/nyghtserif.ttf" 

        msg = MIMEMultipart('related')
        msg['From'] = f"Dovelia App <{EMAIL_SENDER}>"
        msg['To'] = recipient
        msg['Subject'] = "Tu código de recuperación de Dovelia"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="color-scheme" content="light dark">
                <meta name="supported-color-schemes" content="light dark">
                
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
                
                <style>
                    :root {{
                        color-scheme: light dark;
                        supported-color-schemes: light dark;
                    }}
                    
                    @font-face {{
                        font-family: 'NyghtSerif';
                        src: url('{font_url}') format('truetype');
                        font-weight: normal;
                        font-style: normal;
                    }}
                </style>
            </head>
            
            <body style="margin: 0; padding: 0; background-color: #231B18; background-image: linear-gradient(#231B18, #231B18); font-family: 'Montserrat', Arial, sans-serif;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #231B18; background-image: linear-gradient(#231B18, #231B18); padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="100%" max-width="500" border="0" cellspacing="0" cellpadding="0" 
                                   style="background-color: #160906; background-image: linear-gradient(#160906, #160906); border-radius: 28px; overflow: hidden; max-width: 500px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                                <tr>
                                    <td style="padding: 40px 30px; text-align: center;">
                                        
                                        <img src="cid:logo_app" alt="Dovelia Logo" width="120" style="margin-bottom: 10px;">
                                        
                                        <h1 style="color: #FFB5A7; -webkit-text-fill-color: #FFB5A7; font-family: 'NyghtSerif', Georgia, serif; font-size: 48px; margin: 0; font-weight: bold; font-style: italic;">
                                            Dovelia
                                        </h1>
                                        
                                        <div style="height: 2px; background-color: #2D2421; background-image: linear-gradient(#2D2421, #2D2421); margin: 20px auto; width: 50%;"></div>
                                        
                                        <h2 style="color: #FFFFFF; -webkit-text-fill-color: #FFFFFF; font-family: 'Montserrat', Arial, sans-serif; font-size: 20px; margin-top: 0; font-weight: 600; letter-spacing: 1px;">
                                            Restablecer contraseña
                                        </h2>
                                        
                                        <p style="color: #E6E1E0; -webkit-text-fill-color: #E6E1E0; font-family: 'Montserrat', Arial, sans-serif; font-size: 16px; line-height: 1.6; margin: 25px 0;">
                                            Hola,<br>
                                            Has solicitado restablecer tu contraseña. Utiliza el siguiente código PIN de seguridad dentro de la aplicación:
                                        </p>
                                        
                                        <div style="background-color: #120C0A; background-image: linear-gradient(#120C0A, #120C0A); border: 1px solid #FFB5A7; border-radius: 20px; 
                                                    padding: 25px; margin: 20px 0; display: inline-block; min-width: 180px;">
                                            <span style="font-family: 'Montserrat', Arial, sans-serif; font-size: 38px; font-weight: bold; letter-spacing: 10px; color: #FFB5A7; -webkit-text-fill-color: #FFB5A7; text-shadow: 0 0 10px rgba(255,181,167,0.3);">
                                                {pin}
                                            </span>
                                        </div>
                                        
                                        <p style="color: #ABA4A2; -webkit-text-fill-color: #ABA4A2; font-family: 'Montserrat', Arial, sans-serif; font-size: 13px; margin-top: 30px; font-style: italic;">
                                            Este código es de un solo uso. Si no has solicitado este cambio, puedes ignorar este correo.
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="background-color: #2D2421; background-image: linear-gradient(#2D2421, #2D2421); padding: 20px; text-align: center;">
                                        <p style="color: #FFB5A7; -webkit-text-fill-color: #FFB5A7; font-family: 'Montserrat', Arial, sans-serif; font-size: 11px; margin: 0; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">
                                            Dovelia &copy; 2026
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with open("static/images/dovelia_logo.png", "rb") as img_file:
                logo_img = MIMEImage(img_file.read())
                logo_img.add_header('Content-ID', '<logo_app>')
                logo_img.add_header('Content-Disposition', 'inline')
                msg.attach(logo_img)
        except Exception as img_e:
            print(f"Aviso: No se pudo cargar el logo local. Comprueba la ruta. Error: {img_e}")

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado con éxito a {recipient}")
    except Exception as e:
        print(f"Error enviando correo: {e}")

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, receiver_id: str):
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.get("/messages/{other_user_id}", response_model=List[MessageResponse])
def get_chat_history(other_user_id: str, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    return crud.get_chat_messages(db, token_user_id, other_user_id)

@app.post("/messages", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    db_msg = crud.create_message(db, token_user_id, message)
    
    msg_dict = {
        "type": "message",
        "id": db_msg.id,
        "sender_id": db_msg.sender_id,
        "receiver_id": db_msg.receiver_id,
        "text": db_msg.text,
        "timestamp": db_msg.timestamp.isoformat()
    }
    
    await manager.send_personal_message(json.dumps(msg_dict), message.receiver_id)
    
    return db_msg

@app.get("/users/unread-status", response_model=List[str])
def get_unread_status(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    """Endpoint para que la app sepa dónde poner el puntito rojo al arrancar"""
    return crud.get_unread_senders(db, token_user_id)


@app.get("/users/me", response_model=UserResponse)
def get_current_user_profile(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    """
    Obtiene el perfil del usuario autenticado basado en el token.
    """
    db_user = crud.get_user(db, user_id=token_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: str, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    """
    Endpoint para obtener los datos de un usuario específico.
    """
    db_user = crud.get_user(db, user_id=user_id) 
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return db_user


@app.get("/users/check-email/{email}")
def check_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        return {"exists": True}
    return {"exists": False}


@app.get("/discover/users", response_model=List[UserResponse])
def get_users_to_discover(
    db: Session = Depends(get_db),
    token_user_id: str = Depends(get_current_user_id),
    city: Optional[str] = None,
    rooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    tags: Optional[List[str]] = Query(None)
    ):
    users = crud.get_discover_users(
        db=db, 
        current_user_id=token_user_id,
        city=city,
        rooms=rooms,
        bathrooms=bathrooms,
        tags=tags
    )
    return users


@app.get("/matches", response_model=List[UserResponse])
def get_user_matches(db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    matches = crud.get_user_matches(db, current_user_id=token_user_id)
    return matches


@app.post("/users/", response_model=TokenResponse)
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


@app.post("/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint para iniciar sesión. Devuelve un Token JWT si tiene éxito.
    """
    # 1. Comprobamos las credenciales
    user = crud.authenticate_user(db, email=login_data.email, password=login_data.password)
    
    if not user:
        # Si falla, devolvemos el mítico error 401 Unauthorized
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )
    
    # 2. Creamos el token. Dentro del token guardamos el ID del usuario
    access_token = create_access_token(data={"sub": user.id})
    
    # 3. Devolvemos el Token a Android
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id
    }
    
@app.post("/auth/google", response_model=TokenResponse)
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
            random_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
            
            new_user_data = UserCreate(
                id=str(uuid.uuid4()),
                name=name,
                surname=surname,
                email=email,
                password=random_pass,
                birth_date=date.today(),
                profile_pic_url=picture,
                user_description="¡Hola! Uso Dovelia.",
                user_tags=[],
                creation_date=int(time.time())
            )
            user = crud.create_user(db=db, user=new_user_data)
        
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer", "user_id": str(user.id)}
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Token de Google inválido")


@app.post("/users/recover-request")
def request_recovery_pin(request: RecoverEmailRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    
    if user:
        pin = str(random.randint(1000, 9999))
        recovery_codes[request.email] = pin
        send_email_pin(user.email, pin)
        
    return {"status": "ok", "message": "Si el correo existe, se ha enviado un PIN."}


@app.post("/users/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    valid_pin = recovery_codes.get(request.email)
    if not valid_pin or valid_pin != request.pin:
        raise HTTPException(status_code=400, detail="El PIN es incorrecto o ha caducado.")
    
    user = crud.update_user_password(db, email=request.email, new_password=request.new_password)
    
    if user:
        del recovery_codes[request.email]
        
    return {"status": "success", "message": "Contraseña actualizada correctamente."}
   
    
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    # 1. Generar un nombre único para que no se sobreescriban
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    file_path = f"static/images/{filename}"
    
    # 2. Guardar el archivo físicamente en la carpeta
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Devolver la URL (ajusta localhost al puerto que uses)
    # Si usas el emulador será http://10.0.2.2:8000/...
    return {"url": file_path}

@app.post("/discover/swipe", response_model=SwipeResponse)
async def swipe_user(action: SwipeAction, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    """Registra un like/dislike y avisa si hay match"""
    if token_user_id == action.swiped_id:
        raise HTTPException(status_code=400, detail="No puedes deslizarte a ti mismo")
        
    is_match = crud.record_swipe_and_check_match(
        db=db, 
        swiper_id=token_user_id, 
        swiped_id=action.swiped_id, 
        is_like=action.is_like
    )
    
    if is_match:
        match_notification = {
            "type": "match",
            "sender_id": token_user_id,
            "receiver_id": action.swiped_id
        }
        await manager.send_personal_message(json.dumps(match_notification), action.swiped_id)    
    return {"mutual_match": is_match}



@app.put("/users/{user_id}", response_model=UserResponse)
def update_user_profile(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    """
    Endpoint para editar el perfil: Actualiza los datos de un usuario.
    """
    if user_id != token_user_id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para editar un perfil que no es tuyo"
        )
    
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return db_user

@app.put("/messages/mark-read/{sender_id}")
def mark_read(sender_id: str, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    """Endpoint para limpiar el puntito cuando el usuario entra al chat"""
    crud.mark_messages_as_read(db, token_user_id, sender_id)
    return {"status": "success"}

@app.delete("/upload/image/{filename}")
async def delete_image(filename: str, token_user_id: str = Depends(get_current_user_id)):
    file_path = f"static/images/{filename}"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"detail": "Imagen eliminada con éxito"}
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")