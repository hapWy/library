from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL



engine = create_async_engine(DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)