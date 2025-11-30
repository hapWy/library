from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Author(Base):
    __tablename__ = "authors"
    
    author_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, unique=True, index=True)
    birth_year = Column(Integer)
    country = Column(String(100))
    
    books = relationship("Book", back_populates="author")