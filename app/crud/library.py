from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app import models
from app.schemas import library as library_schemas

async def get_libraries(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Library]:
    result = await db.execute(select(models.Library).offset(skip).limit(limit))
    return result.scalars().all()

async def get_library(db: AsyncSession, library_id: int) -> Optional[models.Library]:
    result = await db.execute(select(models.Library).where(models.Library.library_id == library_id))
    return result.scalar_one_or_none()

async def create_library(db: AsyncSession, library: library_schemas.LibraryCreate) -> models.Library:
    db_library = models.Library(**library.dict())
    db.add(db_library)
    await db.commit()
    await db.refresh(db_library)
    return db_library