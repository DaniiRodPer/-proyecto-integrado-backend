from pydantic import BaseModel

class SwipeAction(BaseModel):
    swiped_id: str
    is_like: bool

class SwipeResponse(BaseModel):
    mutual_match: bool