import os
import shutil
import uuid
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import crud
from app.database import SessionLocal, engine, Base
from app.security import create_access_token, get_current_user_id
from app.schemas.userSchema import UserCreate, UserResponse, UserUpdate, LoginRequest, TokenResponse
from app.schemas.swipeSchema import SwipeAction, SwipeResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return {"url": f"http://10.0.2.2:8000/{file_path}"}



@app.post("/discover/swipe", response_model=SwipeResponse)
def swipe_user(action: SwipeAction, db: Session = Depends(get_db), token_user_id: str = Depends(get_current_user_id)):
    """Registra un like/dislike y avisa si hay match"""
    if token_user_id == action.swiped_id:
        raise HTTPException(status_code=400, detail="No puedes deslizarte a ti mismo")
        
    is_match = crud.record_swipe_and_check_match(
        db=db, 
        swiper_id=token_user_id, 
        swiped_id=action.swiped_id, 
        is_like=action.is_like
    )
    
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


@app.delete("/upload/image/{filename}")
async def delete_image(filename: str, token_user_id: str = Depends(get_current_user_id)):
    file_path = f"static/images/{filename}"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"detail": "Imagen eliminada con éxito"}
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")