from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Library(Base):
    __tablename__ = "libraries"
    
    library_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    address = Column(String(200), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    books = relationship("Book", back_populates="library", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="library", cascade="all, delete-orphan")