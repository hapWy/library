from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReaderBase(BaseModel):
    full_name: str
    address: Optional[str] = None
    phone: Optional[str] = None

class ReaderCreate(ReaderBase):
    pass

class Reader(ReaderBase):
    reader_id: int
    reg_date: date
    
    class Config:
        from_attributes = True