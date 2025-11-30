from fastapi import APIRouter, HTTPException
from typing import List

from app.api.deps import DBSession
from app.crud import book as book_crud
from app.schemas import book as book_schemas

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=book_schemas.Book)
async def create_book(book: book_schemas.BookCreate, db: DBSession):
    return await book_crud.create_book(db=db, book=book)

@router.get("/", response_model=List[book_schemas.Book])
async def read_books(db: DBSession, skip: int = 0, limit: int = 100):
    books = await book_crud.get_books(db, skip=skip, limit=limit)
    return books

@router.get("/{book_id}", response_model=book_schemas.Book)
async def read_book(book_id: int, db: DBSession):
    db_book = await book_crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/detailed/", response_model=List[book_schemas.BookDetailed])
async def read_books_detailed(db: DBSession):
    return await book_crud.get_books_detailed(db)

@router.get("/list/", response_model=List[book_schemas.BooksList])
async def read_books_list(db: DBSession):
    return await book_crud.get_books_list(db)