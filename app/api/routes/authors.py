from fastapi import APIRouter, HTTPException
from typing import List

from app.api.deps import DBSession
from app.crud import author as author_crud
from app.schemas import author as author_schemas

router = APIRouter(prefix="/authors", tags=["authors"])

@router.post("/", response_model=author_schemas.Author)
async def create_author(author: author_schemas.AuthorCreate, db: DBSession):
    return await author_crud.create_author(db=db, author=author)

@router.get("/", response_model=List[author_schemas.Author])
async def read_authors(db: DBSession, skip: int = 0, limit: int = 100):
    authors = await author_crud.get_authors(db, skip=skip, limit=limit)
    return authors

@router.get("/{author_id}", response_model=author_schemas.Author)
async def read_author(author_id: int, db: DBSession):
    db_author = await author_crud.get_author(db, author_id=author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author