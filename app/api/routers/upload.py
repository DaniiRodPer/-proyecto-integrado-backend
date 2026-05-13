import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.security import get_current_user_id

router = APIRouter(tags=["Upload"])

"""
Función upload_image:
    params:
        file
        
Genera un UUID único para la imagen, la almacena en el servidor y devuleve la URL relativa
    
    returns:
        diccionario
"""
@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    file_path = f"static/images/{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"url": file_path}



"""
Función delete_image:
    params:
        filename
        token_user_id
        
Busca una imagen por su nombre de archivo en el servidor y la elimina del almacenamiento del servidor
    
    returns:
        diccionario
"""
@router.delete("/upload/image/{filename}")
async def delete_image(filename: str, token_user_id: str = Depends(get_current_user_id)):
    file_path = f"static/images/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"detail": "Imagen eliminada con éxito"}
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")