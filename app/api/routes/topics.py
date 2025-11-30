from fastapi import APIRouter, HTTPException
from typing import List

from app.api.deps import DBSession
from app.crud import topic as topic_crud
from app.schemas import topic as topic_schemas

router = APIRouter(prefix="/topics", tags=["topics"])

@router.post("/", response_model=topic_schemas.Topic)
async def create_topic(topic: topic_schemas.TopicCreate, db: DBSession):
    return await topic_crud.create_topic(db=db, topic=topic)

@router.get("/", response_model=List[topic_schemas.Topic])
async def read_topics(db: DBSession, skip: int = 0, limit: int = 100):
    topics = await topic_crud.get_topics(db, skip=skip, limit=limit)
    return topics

@router.get("/{topic_id}", response_model=topic_schemas.Topic)
async def read_topic(topic_id: int, db: DBSession):
    db_topic = await topic_crud.get_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic