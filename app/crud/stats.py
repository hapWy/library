from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app import models
from app.schemas import stats as stats_schemas

async def get_library_stats(db: AsyncSession) -> List[stats_schemas.LibraryStats]:
    result = await db.execute(
        select(
            models.Library.name,
            func.count(models.Book.book_id).label('total_books'),
            func.sum(models.Book.quantity).label('total_copies')
        )
        .select_from(models.Library)
        .join(models.Book)
        .group_by(models.Library.name)
        .having(func.count(models.Book.book_id) > 0)
    )
    stats_data = result.all()
    
    return [stats_schemas.LibraryStats(
        library_name=stat.name,
        total_books=stat.total_books,
        total_copies=stat.total_copies
    ) for stat in stats_data]