from fastapi import APIRouter, HTTPException
from typing import List

from app.api.deps import DBSession
from app.crud import library as library_crud
from app.schemas import library as library_schemas

router = APIRouter(prefix="/libraries", tags=["libraries"])

@router.post("/", response_model=library_schemas.Library)
async def create_library(library: library_schemas.LibraryCreate, db: DBSession):
    return await library_crud.create_library(db=db, library=library)

@router.get("/", response_model=List[library_schemas.Library])
async def read_libraries(db: DBSession, skip: int = 0, limit: int = 100):
    libraries = await library_crud.get_libraries(db, skip=skip, limit=limit)
    return libraries

@router.get("/{library_id}", response_model=library_schemas.Library)
async def read_library(library_id: int, db: DBSession):
    db_library = await library_crud.get_library(db, library_id=library_id)
    if db_library is None:
        raise HTTPException(status_code=404, detail="Library not found")
    return db_library