from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app import models
from app.schemas import topic as topic_schemas

async def get_topics(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Topic]:
    result = await db.execute(select(models.Topic).offset(skip).limit(limit))
    return result.scalars().all()

async def get_topic(db: AsyncSession, topic_id: int) -> Optional[models.Topic]:
    result = await db.execute(select(models.Topic).where(models.Topic.topic_id == topic_id))
    return result.scalar_one_or_none()

async def create_topic(db: AsyncSession, topic: topic_schemas.TopicCreate) -> models.Topic:
    db_topic = models.Topic(**topic.dict())
    db.add(db_topic)
    await db.commit()
    await db.refresh(db_topic)
    return db_topic