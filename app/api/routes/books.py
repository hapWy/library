from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import DBSession
from app.crud import book as book_crud
from app.schemas import book as book_schemas
from app.models.book import Book

router = APIRouter(prefix="/api/books", tags=["books"])

@router.post("/", response_model=book_schemas.Book)
async def create_book(book: book_schemas.BookCreate, db: DBSession):
    print("🎯 Received book creation request")
    print(f"📖 Book data: {book.dict()}")
    
    # Валидация обязательных полей
    if not book.library_id:
        print("❌ Missing library_id")
    if not book.topic_id:
        print("❌ Missing topic_id") 
    if not book.author_id:
        print("❌ Missing author_id")
    
    try:
        result = await book_crud.create_book(db=db, book=book)
        print("✅ Book created successfully")
        return result
    except Exception as e:
        print(f"❌ Error creating book: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[book_schemas.Book])
async def read_books(
    db: DBSession,
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    library_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    
):
    query = select(Book)
    
    if search:
        query = query.where(
            Book.title.ilike(f"%{search}%") |
            Book.publisher.ilike(f"%{search}%") |
            Book.publish_place.ilike(f"%{search}%")
        )
    
    if library_id:
        query = query.where(Book.library_id == library_id)
    
    if topic_id:
        query = query.where(Book.topic_id == topic_id)
    
    if author_id:
        query = query.where(Book.author_id == author_id)
    
    if min_price is not None:
        query = query.where(Book.price >= min_price)
    
    if max_price is not None:
        query = query.where(Book.price <= max_price)
    
    if sort_by:
        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "price":
            query = query.order_by(Book.price.desc())
        elif sort_by == "publish_year":
            query = query.order_by(Book.publish_year.desc())
        elif sort_by == "quantity":
            query = query.order_by(Book.quantity.desc())
        elif sort_by == "book_id":
            query = query.order_by(Book.book_id)
    else:
        query = query.order_by(Book.book_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    books = result.scalars().all()
    return books

@router.get("/{book_id}", response_model=book_schemas.Book)
async def read_book(book_id: int, db: DBSession):
    db_book = await book_crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=book_schemas.Book)
async def update_book(
    book_id: int,
    book: book_schemas.BookCreate,
    db: DBSession
):
    db_book = await book_crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Обновление полей
    for field, value in book.dict().items():
        setattr(db_book, field, value)
    
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
async def delete_book(book_id: int, db: DBSession):
    db_book = await book_crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(db_book)
    await db.commit()
    return {"message": "Book deleted successfully"}

@router.get("/detailed/", response_model=List[book_schemas.BookDetailed])
async def read_books_detailed(db: DBSession):
    return await book_crud.get_books_detailed(db)

@router.get("/list/", response_model=List[book_schemas.BooksList])
async def read_books_list(db: DBSession):
    return await book_crud.get_books_list(db)