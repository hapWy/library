from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    subscription_id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey('libraries.library_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    reader_id = Column(Integer, ForeignKey('readers.reader_id'), nullable=False)
    issue_date = Column(Date, server_default=func.current_date())
    return_date = Column(Date)
    deposit = Column(Numeric(10, 2), default=0)
    
    library = relationship("Library", back_populates="subscriptions")
    book = relationship("Book", back_populates="subscriptions")
    reader = relationship("Reader", back_populates="subscriptions")
    
    __table_args__ = (
        CheckConstraint('deposit >= 0', name='check_deposit'),
    )