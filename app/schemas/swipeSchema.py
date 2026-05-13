from pydantic import BaseModel

"""
Clase SwipeAction
propiedades:
    -swiped_id
    -is_like
    
Define los datos necesarios para guardar una interaccion de Like o Dislike sobre otro perfil
"""
class SwipeAction(BaseModel):
    swiped_id: str
    is_like: bool

class SwipeResponse(BaseModel):
    mutual_match: bool