from pydantic import BaseModel, field_validator
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
    
    @field_validator('publish_year')
    def validate_publish_year(cls, v):
        if v is not None and (v < 1500 or v > datetime.now().year):
            raise ValueError('Publish year must be between 1500 and current year')
        return v

class BookCreate(BaseModel):
    title: str
    publisher: Optional[str] = None
    publish_place: Optional[str] = None
    publish_year: Optional[int] = None
    quantity: Optional[int] = 1
    price: Optional[float] = 0.0
    library_id: int
    topic_id: int
    author_id: int

    @field_validator('publish_year')
    def validate_publish_year(cls, v):
        if v is not None and (v < 1500 or v > datetime.now().year):
            raise ValueError('Invalid publish year')
        return v

    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v

    @field_validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v

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