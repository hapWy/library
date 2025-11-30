from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Reader(Base):
    __tablename__ = "readers"
    
    reader_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, index=True)
    address = Column(String(200))
    phone = Column(String(20), unique=True, index=True)
    reg_date = Column(Date, server_default=func.current_date())
    
    subscriptions = relationship("Subscription", back_populates="reader")