from pydantic import BaseModel
from typing import Optional

class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    topic_id: int
    
    class Config:
        from_attributes = True