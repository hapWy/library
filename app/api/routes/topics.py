from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import DBSession
from app.crud import topic as topic_crud
from app.schemas import topic as topic_schemas
from app.models.topic import Topic

router = APIRouter(prefix="/api/topics", tags=["topics"])

@router.post("/", response_model=topic_schemas.Topic)
async def create_topic(topic: topic_schemas.TopicCreate, db: DBSession):
    return await topic_crud.create_topic(db=db, topic=topic)

@router.get("/", response_model=List[topic_schemas.Topic])
async def read_topics(
    db: DBSession, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    
):
    query = select(Topic)
    
    if search:
        query = query.where(
            Topic.name.ilike(f"%{search}%") |
            Topic.description.ilike(f"%{search}%")
        )
    
    if sort_by:
        if sort_by == "name":
            query = query.order_by(Topic.name)
        elif sort_by == "topic_id":
            query = query.order_by(Topic.topic_id)
    else:
        query = query.order_by(Topic.topic_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    topics = result.scalars().all()
    return topics

@router.get("/{topic_id}", response_model=topic_schemas.Topic)
async def read_topic(topic_id: int, db: DBSession):
    db_topic = await topic_crud.get_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.put("/{topic_id}", response_model=topic_schemas.Topic)
async def update_topic(
    topic_id: int,
    topic: topic_schemas.TopicCreate,
    db: DBSession
):
    db_topic = await topic_crud.get_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Обновление полей
    for field, value in topic.dict().items():
        setattr(db_topic, field, value)
    
    await db.commit()
    await db.refresh(db_topic)
    return db_topic

@router.delete("/{topic_id}")
async def delete_topic(topic_id: int, db: DBSession):
    db_topic = await topic_crud.get_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    await db.delete(db_topic)
    await db.commit()
    return {"message": "Topic deleted successfully"}