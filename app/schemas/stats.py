from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class LibraryStats(BaseModel):
    library_name: str
    total_books: int
    total_copies: int
    total_value: Decimal
    
    class Config:
        from_attributes = True

class AuthorStats(BaseModel):
    author_name: str
    total_books: int
    total_copies: int
    avg_price: Decimal
    
    class Config:
        from_attributes = True

class SubscriptionStats(BaseModel):
    subscription_id: int
    reader_name: str
    book_title: str
    library_name: str
    issue_date: str
    return_date: Optional[str]
    deposit: Decimal
    
    class Config:
        from_attributes = True