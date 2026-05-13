from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from app.database import Base

"""
Clase Swipe
propiedades:
    -id
    -swiper_id
    -swiped_id
    -is_read
    -is_like
"""
class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    swiper_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    swiped_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    is_like = Column(Boolean, nullable=False)

    # Esto es para evitar que un usuario deslice a la misma persona dos veces
    __table_args__ = (UniqueConstraint('swiper_id', 'swiped_id', name='_swiper_swiped_uc'),)