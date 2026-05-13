import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.api.routers import auth, users, discover, chat, upload

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dovelia API")

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(discover.router)
app.include_router(chat.router)
app.include_router(upload.router)