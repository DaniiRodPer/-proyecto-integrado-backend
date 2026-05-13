from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://dev_user:00000@localhost/pi_backend_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

"""
Función get_db:

Crea una nueva sesión de base de datos para cada petición y asegura su cierre una vez finalizada la operación.
Establece la comunicación entre FastAPI y sqlalchemy.
"""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()