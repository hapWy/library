from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import DBSession
from app.crud import author as author_crud
from app.schemas import author as author_schemas
from app.models.author import Author

router = APIRouter(prefix="/api/authors", tags=["authors"])

@router.post("/", response_model=author_schemas.Author)
async def create_author(author: author_schemas.AuthorCreate, db: DBSession):
    return await author_crud.create_author(db=db, author=author)

@router.get("/", response_model=List[author_schemas.Author])
async def read_authors(
    db: DBSession,
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    
):
    query = select(Author)
    
    if search:
        query = query.where(
            Author.full_name.ilike(f"%{search}%") |
            Author.country.ilike(f"%{search}%")
        )
    
    if country:
        query = query.where(Author.country.ilike(f"%{country}%"))
    
    if sort_by:
        if sort_by == "full_name":
            query = query.order_by(Author.full_name)
        elif sort_by == "birth_year":
            query = query.order_by(Author.birth_year.desc())
        elif sort_by == "country":
            query = query.order_by(Author.country)
        elif sort_by == "author_id":
            query = query.order_by(Author.author_id)
    else:
        query = query.order_by(Author.author_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    authors = result.scalars().all()
    return authors

@router.get("/{author_id}", response_model=author_schemas.Author)
async def read_author(author_id: int, db: DBSession):
    db_author = await author_crud.get_author(db, author_id=author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

@router.put("/{author_id}", response_model=author_schemas.Author)
async def update_author(
    author_id: int,
    author: author_schemas.AuthorCreate,
    db: DBSession
):
    db_author = await author_crud.get_author(db, author_id=author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Обновление полей
    for field, value in author.dict().items():
        setattr(db_author, field, value)
    
    await db.commit()
    await db.refresh(db_author)
    return db_author

@router.delete("/{author_id}")
async def delete_author(author_id: int, db: DBSession):
    db_author = await author_crud.get_author(db, author_id=author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    
    await db.delete(db_author)
    await db.commit()
    return {"message": "Author deleted successfully"}