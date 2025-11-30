from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class BookBase(BaseModel):
    title: str
    publisher: Optional[str] = None
    publish_place: Optional[str] = None
    publish_year: Optional[int] = None
    quantity: int = 1
    price: Decimal = 0
    
    @validator('publish_year')
    def validate_publish_year(cls, v):
        if v is not None and (v < 1500 or v > datetime.now().year):
            raise ValueError('Publish year must be between 1500 and current year')
        return v

class BookCreate(BookBase):
    library_id: int
    topic_id: int
    author_id: int

class Book(BookBase):
    book_id: int
    library_id: int
    topic_id: int
    author_id: int
    
    class Config:
        from_attributes = True

class BookDetailed(BaseModel):
    book_id: int
    title: str
    author_name: str
    topic_name: str
    library_name: str
    quantity: int
    price: Decimal
    
    class Config:
        from_attributes = True

class BooksList(BaseModel):
    book_id: int
    title: str
    quantity: int
    price: Decimal
    
    class Config:
        from_attributes = True