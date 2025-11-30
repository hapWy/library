from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey('libraries.library_id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    author_id = Column(Integer, ForeignKey('authors.author_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False, index=True)
    publisher = Column(String(100))
    publish_place = Column(String(100))
    publish_year = Column(Integer)
    quantity = Column(Integer, default=1)
    price = Column(Numeric(10, 2), default=0)
    
    library = relationship("Library", back_populates="books")
    topic = relationship("Topic", back_populates="books")
    author = relationship("Author", back_populates="books")
    subscriptions = relationship("Subscription", back_populates="book")
    
    __table_args__ = (
        CheckConstraint('publish_year BETWEEN 1500 AND EXTRACT(YEAR FROM CURRENT_DATE)', name='check_publish_year'),
        CheckConstraint('quantity >= 0', name='check_quantity'),
        CheckConstraint('price >= 0', name='check_price'),
    )