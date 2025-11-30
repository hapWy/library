from fastapi import APIRouter, HTTPException
from typing import List

from app.api.deps import DBSession
from app.crud import reader as reader_crud
from app.schemas import reader as reader_schemas

router = APIRouter(prefix="/readers", tags=["readers"])

@router.post("/", response_model=reader_schemas.Reader)
async def create_reader(reader: reader_schemas.ReaderCreate, db: DBSession):
    return await reader_crud.create_reader(db=db, reader=reader)

@router.get("/", response_model=List[reader_schemas.Reader])
async def read_readers(db: DBSession, skip: int = 0, limit: int = 100):
    readers = await reader_crud.get_readers(db, skip=skip, limit=limit)
    return readers

@router.get("/{reader_id}", response_model=reader_schemas.Reader)
async def read_reader(reader_id: int, db: DBSession):
    db_reader = await reader_crud.get_reader(db, reader_id=reader_id)
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return db_reader