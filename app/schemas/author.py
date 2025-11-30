from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class AuthorBase(BaseModel):
    full_name: str
    birth_year: Optional[int] = None
    country: Optional[str] = None
    
    @validator('birth_year')
    def validate_birth_year(cls, v):
        if v is not None and (v < 1500 or v > datetime.now().year):
            raise ValueError('Birth year must be between 1500 and current year')
        return v

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    author_id: int
    
    class Config:
        from_attributes = True