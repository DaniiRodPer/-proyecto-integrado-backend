from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from app.models import User, Accommodation
from app.schemas.userSchema import UserCreate, UserUpdate
from app.schemas.accommodationSchema import AccommodationCreate
from app.security import get_password_hash, verify_password
from app.models.swipe import Swipe
from app.models.user import User
from app.models.message import Message
from app.schemas.messageSchema import MessageCreate


"""
Función get_user_by_email:
    params:
        db
        email
        
Busca en la base de datos un usuario que coincida con el email proporcionado.

    returns:
        User
"""
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


"""
Función create_user:
    params:
        db
        user
        
Registra un nuevo usuario hasheando su contraseña y creando su alojsmiento asociado.

    returns:
        User
"""
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


"""
Función get_users:
    params:
        db
        skip
        limit
        
Recupera una lista de usuarios de la base de datos con soporte para paginación con saltos y límites.

    returns:
        List[User]
"""
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


"""
Función get_user:
    params:
        db
        user_id
        
Devuelve un usuario específico por su UUID.

    returns:
        User
"""
def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


"""
Función update_user:
    params:
        db
        user_id
        user_update
        
Actualiza los campos de perfil de n usuario y los datos de su alojamiento, si el alojamiento no existía lo crea.

    returns:
        User
"""
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


"""
Función authenticate_user:
    params:
        db
        email
        password
        
Valida la identidad de un usuario comprobando si el email existe y los hash de la contraseña coinciden

    returns:
        User o False
"""
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
        
    return user


"""
Función get_discover_users:
    params:
        db
        current_user_id
        limit
        city
        rooms
        bathrooms
        tags
        
Devuelve una lista aleatoria de perfiles para la sección de discover quitando al usuario actual y perfiles ya deslizados y con filtros de búsqueda opcionalmente.

    returns:
        List[User]
"""
def get_discover_users(db: Session, current_user_id: str, limit: int = 10, city: str = None, rooms: int = None, bathrooms: int = None, tags: list = None):
    swiped_subquery = select(Swipe.swiped_id).where(Swipe.swiper_id == current_user_id).scalar_subquery()
    
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
        if tags:
            for tag in tags:
                query = query.filter(Accommodation.tags.like(f'%{tag}%'))
            
    return query.order_by(func.rand()).limit(limit).all()


"""
Función record_swipe_and_check_match:
    params:
        db
        swiper_id
        swiped_id
        is_like
        
Almacena un swipe y verifica si hay match

    returns:
        bool
"""
def record_swipe_and_check_match(db: Session, swiper_id: str, swiped_id: str, is_like: bool) -> bool:

    existing_swipe = db.query(Swipe).filter(Swipe.swiper_id == swiper_id, Swipe.swiped_id == swiped_id).first()
    
    if not existing_swipe:
        new_swipe = Swipe(swiper_id=swiper_id, swiped_id=swiped_id, is_like=is_like)
        db.add(new_swipe)
        db.commit()

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


"""
Función get_user_matches:
    params:
        db
        current_user_id
        
Busca en la tabla de swipes registros de swipes opuestos entre dos usuariosy y devuleve los matches del usuarios actual del parametro

    returns:
        List[User]
"""
def get_user_matches(db: Session, current_user_id: str):
    my_likes_subquery = select(Swipe.swiped_id).where(
        Swipe.swiper_id == current_user_id,
        Swipe.is_like == True
    ).scalar_subquery()
    
    mutual_match_ids = select(Swipe.swiper_id).where(
        Swipe.swiped_id == current_user_id,
        Swipe.is_like == True,
        Swipe.swiper_id.in_(my_likes_subquery)
    ).scalar_subquery()
    
    return db.query(User).filter(User.id.in_(mutual_match_ids)).all()


"""
Función create_message:
    params:
        db
        sender_id
        msg (MessageCreate)
        
Registra un nuevo mensaje en la base de datos vinculando al emisor y receptor.

    returns:
        Message
"""
def create_message(db: Session, sender_id: str, msg: MessageCreate):
    db_msg = Message(
        sender_id=sender_id,
        receiver_id=msg.receiver_id,
        text=msg.text
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


"""
Función get_chat_messages:
    params:
        db
        user1_id
        user2_id
        
Recupera el historial completo de conversación entre dos usuarios, ordenado cronológicamente.

    returns:
        List[Message]
"""
def get_chat_messages(db: Session, user1_id: str, user2_id: str):
    return db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.timestamp.asc()).all()
    

def update_user_password(db: Session, email: str, new_password: str):
    user = get_user_by_email(db, email)
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
    return user

def get_unread_senders(db: Session, user_id: str):
    senders = db.query(Message.sender_id).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).distinct().all()
    return [s[0] for s in senders]


"""
Función record_swipe_and_check_match:
    params:
        db
        swiper_id
        swiped_id
        is_like
        
Almacena un swipe y verifica si hay match

    returns:
        bool
"""
def mark_messages_as_read(db: Session, token_user_id: str, sender_id: str):
    db.query(Message).filter(
        Message.receiver_id == token_user_id,
        Message.sender_id == sender_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()