from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LibraryBase(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None

class LibraryCreate(LibraryBase):
    pass

class Library(LibraryBase):
    library_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True