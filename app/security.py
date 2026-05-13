from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#CONFGURACIÓN DEL TOKEN
SECRET_KEY = "mi_clave_super_secreta_y_larga_para_el_proyecto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


def verify_password(plain_password, hashed_password):
    """Comprueba si la contraseña plana coincide con el hash de la DB"""
    return pwd_context.verify(plain_password, hashed_password)


"""
Función verify_password:
    params:
        plain_password
        hashed_password
        
Compara una contraseña en texto plano con un hash almacenado para verificar si coincide

    returns:
        bool
"""
def get_password_hash(password):
    return pwd_context.hash(password)


"""
Función create_access_token:
    params:
        data
        
Genera un token JWT firmado y una fecha de expiración.

    returns:
        str
"""
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


"""
Función get_current_user_id:
    params:
        token
        
Decodifica y valida un token JWT recibido en la cabecera y extraye el UUID del usuario
si el token es inválido, lanza un error 401, de lo contrario devuelve el ID del usuario.

    returns:
        str
"""
def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """
    Valida el token. 
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except jwt.PyJWTError:
        raise credentials_exception