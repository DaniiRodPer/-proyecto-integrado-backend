from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from app.database import Base

class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    swiper_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    swiped_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    is_like = Column(Boolean, nullable=False)

    # Evitamos que un usuario deslice a la misma persona dos veces
    __table_args__ = (UniqueConstraint('swiper_id', 'swiped_id', name='_swiper_swiped_uc'),)