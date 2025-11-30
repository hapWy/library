from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.book import Book
from app.models.author import Author
from app.models.topic import Topic
from app.models.library import Library
from app.schemas.book import BookCreate, BookDetailed, BooksList

async def get_books(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Book]:
    result = await db.execute(
        select(Book)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Book.author), selectinload(Book.topic), selectinload(Book.library))
    )
    return result.scalars().all()

async def get_book(db: AsyncSession, book_id: int) -> Optional[Book]:
    result = await db.execute(
        select(Book)
        .where(Book.book_id == book_id)
        .options(selectinload(Book.author), selectinload(Book.topic), selectinload(Book.library))
    )
    return result.scalar_one_or_none()

async def create_book(db: AsyncSession, book: BookCreate) -> Book:
    db_book = Book(**book.dict())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def get_books_detailed(db: AsyncSession) -> List[BookDetailed]:
    result = await db.execute(
        select(
            Book.book_id,
            Book.title,
            Book.quantity,
            Book.price,
            Author.full_name.label("author_name"),
            Topic.name.label("topic_name"),
            Library.name.label("library_name")
        )
        .select_from(Book)
        .join(Author)
        .join(Topic)
        .join(Library)
    )
    books_data = result.all()
    
    books_detailed = []
    for book in books_data:
        books_detailed.append(BookDetailed(
            book_id=book.book_id,
            title=book.title,
            quantity=book.quantity,
            price=book.price,
            author_name=book.author_name,
            topic_name=book.topic_name,
            library_name=book.library_name
        ))
    return books_detailed

async def get_books_list(db: AsyncSession) -> List[BooksList]:
    result = await db.execute(select(Book.book_id, Book.title, Book.quantity, Book.price))
    books_data = result.all()
    
    return [BooksList(
        book_id=book.book_id,
        title=book.title,
        quantity=book.quantity,
        price=book.price
    ) for book in books_data]