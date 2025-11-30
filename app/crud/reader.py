from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app import models
from app.schemas import reader as reader_schemas

async def get_readers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Reader]:
    result = await db.execute(select(models.Reader).offset(skip).limit(limit))
    return result.scalars().all()

async def get_reader(db: AsyncSession, reader_id: int) -> Optional[models.Reader]:
    result = await db.execute(select(models.Reader).where(models.Reader.reader_id == reader_id))
    return result.scalar_one_or_none()

async def create_reader(db: AsyncSession, reader: reader_schemas.ReaderCreate) -> models.Reader:
    db_reader = models.Reader(**reader.dict())
    db.add(db_reader)
    await db.commit()
    await db.refresh(db_reader)
    return db_reader