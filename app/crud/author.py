from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app import models
from app.schemas import author as author_schemas

async def get_authors(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Author]:
    result = await db.execute(select(models.Author).offset(skip).limit(limit))
    return result.scalars().all()

async def get_author(db: AsyncSession, author_id: int) -> Optional[models.Author]:
    result = await db.execute(select(models.Author).where(models.Author.author_id == author_id))
    return result.scalar_one_or_none()

async def create_author(db: AsyncSession, author: author_schemas.AuthorCreate) -> models.Author:
    db_author = models.Author(**author.dict())
    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    return db_author