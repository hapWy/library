from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class SubscriptionBase(BaseModel):
    library_id: int
    book_id: int
    reader_id: int
    issue_date: Optional[date] = None
    return_date: Optional[date] = None
    deposit: Decimal = 0

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    subscription_id: int
    
    class Config:
        from_attributes = True

class SubscriptionDetailed(BaseModel):
    subscription_id: int
    issue_date: date
    return_date: Optional[date]
    deposit: Decimal
    book_title: str
    reader_name: str
    library_name: str
    
    class Config:
        from_attributes = True