from sqlalchemy.orm import Session
from app.models import User, Accommodation
from app.schemas.userSchema import UserCreate, UserUpdate
from app.schemas.accommodationSchema import AccommodationCreate
from app.security import get_password_hash, verify_password
from app.models.swipe import Swipe
from app.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    user_data = user.model_dump(exclude={"accommodation", "password"})
    
    hashed_pwd = get_password_hash(user.password)
    db_user = User(**user_data, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if user.accommodation:
        acc_data = user.accommodation.model_dump()
        db_accommodation = Accommodation(**acc_data, owner_id=db_user.id)
        db.add(db_accommodation)
        db.commit()
        db.refresh(db_user)

    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Recupera una lista de usuarios. 
    skip y limit sirven para la paginación (ej: cargar de 10 en 10).
    """
    return db.query(User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: str):
    """
    Busca un único usuario por su ID.
    También traerá su casa automáticamente si la tiene.
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: str, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    accommodation_data = update_data.pop("accommodation", None)
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    if accommodation_data is not None:
        if db_user.accommodation:
            for key, value in accommodation_data.items():
                setattr(db_user.accommodation, key, value)
        else:
            new_acc = Accommodation(**accommodation_data, owner_id=user_id)
            db.add(new_acc)
            
    db.commit()
    db.refresh(db_user)
    
    return db_user



def authenticate_user(db: Session, email: str, password: str):
    """Comprueba si el usuario existe y la contraseña es correcta"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
        
    return user



def get_discover_users(
    db: Session,
    current_user_id: str,
    limit: int = 10,
    city: str = None,
    rooms: int = None,
    bathrooms: int = None,
    tags: list = None
    ):
    swiped_subquery = db.query(Swipe.swiped_id).filter(Swipe.swiper_id == current_user_id).subquery()
    
    query = db.query(User).filter(
        User.id != current_user_id,
        User.id.notin_(swiped_subquery)
    )

    if city or rooms or bathrooms or tags:
        query = query.join(Accommodation)
        
        if city:
            query = query.filter(Accommodation.city == city)
        if rooms:
            query = query.filter(Accommodation.bedrooms >= rooms)
        if bathrooms:
            query = query.filter(Accommodation.bathrooms >= bathrooms)
    return query.limit(limit).all()


def record_swipe_and_check_match(db: Session, swiper_id: str, swiped_id: str, is_like: bool) -> bool:
    """
    Guarda el swipe y devuelve True si hay Match mutuo.
    """
    # 1. Comprobamos si ya existía (por si acaso la app manda dos veces la petición)
    existing_swipe = db.query(Swipe).filter(Swipe.swiper_id == swiper_id, Swipe.swiped_id == swiped_id).first()
    
    if not existing_swipe:
        new_swipe = Swipe(swiper_id=swiper_id, swiped_id=swiped_id, is_like=is_like)
        db.add(new_swipe)
        db.commit()

    # 2. Si es un Like, comprobamos si la otra persona también nos dio Like
    mutual_match = False
    if is_like:
        reverse_swipe = db.query(Swipe).filter(
            Swipe.swiper_id == swiped_id,
            Swipe.swiped_id == swiper_id,
            Swipe.is_like == True
        ).first()
        
        if reverse_swipe:
            mutual_match = True

    return mutual_match


def get_user_matches(db: Session, current_user_id: str):
    """
    Recupera los usuarios con los que hay un match mutuo (ambos dieron is_like=True).
    """
    # 1. Subconsulta: IDs de las personas a las que yo les he dado Like
    my_likes_subquery = db.query(Swipe.swiped_id).filter(
        Swipe.swiper_id == current_user_id,
        Swipe.is_like == True
    ).subquery()
    
    # 2. Subconsulta: IDs de las personas que me han dado Like, 
    # y que además están en mi lista de Likes
    mutual_match_ids = db.query(Swipe.swiper_id).filter(
        Swipe.swiped_id == current_user_id,
        Swipe.is_like == True,
        Swipe.swiper_id.in_(my_likes_subquery)
    ).subquery()
    
    return db.query(User).filter(User.id.in_(mutual_match_ids)).all()