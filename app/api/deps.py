from typing import Annotated, AsyncGenerator
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Session

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session



# Для аннотаций в роутерах
DBSession = Annotated[AsyncSession, Depends(get_db)]