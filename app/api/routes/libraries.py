from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import DBSession
from app.crud import library as library_crud
from app.schemas import library as library_schemas
from app.models.library import Library

router = APIRouter(prefix="/api/libraries", tags=["libraries"])

@router.post("/", response_model=library_schemas.Library)
async def create_library(library: library_schemas.LibraryCreate, db: DBSession):
    return await library_crud.create_library(db=db, library=library)

@router.get("/", response_model=List[library_schemas.Library])
async def read_libraries(
    db: DBSession,
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    
):
    query = select(Library)
    
    if search:
        query = query.where(
            Library.name.ilike(f"%{search}%") |
            Library.address.ilike(f"%{search}%") |
            Library.phone.ilike(f"%{search}%")
        )
    
    if sort_by:
        if sort_by == "name":
            query = query.order_by(Library.name)
        elif sort_by == "created_at":
            query = query.order_by(Library.created_at.desc())
        elif sort_by == "address":
            query = query.order_by(Library.address)
    else:
        query = query.order_by(Library.library_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    libraries = result.scalars().all()
    return libraries

@router.get("/{library_id}", response_model=library_schemas.Library)
async def read_library(library_id: int, db: DBSession):
    db_library = await library_crud.get_library(db, library_id=library_id)
    if db_library is None:
        raise HTTPException(status_code=404, detail="Library not found")
    return db_library

@router.put("/{library_id}", response_model=library_schemas.Library)
async def update_library(
    library_id: int,
    library: library_schemas.LibraryCreate,
    db: DBSession
):
    db_library = await library_crud.get_library(db, library_id=library_id)
    if db_library is None:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Обновление полей
    for field, value in library.dict().items():
        setattr(db_library, field, value)
    
    await db.commit()
    await db.refresh(db_library)
    return db_library

@router.delete("/{library_id}")
async def delete_library(library_id: int, db: DBSession):
    db_library = await library_crud.get_library(db, library_id=library_id)
    if db_library is None:
        raise HTTPException(status_code=404, detail="Library not found")
    
    await db.delete(db_library)
    await db.commit()
    return {"message": "Library deleted successfully"}