from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import DBSession
from app.crud import reader as reader_crud
from app.schemas import reader as reader_schemas
from app.models.reader import Reader

router = APIRouter(prefix="/api/readers", tags=["readers"])

@router.post("/", response_model=reader_schemas.Reader)
async def create_reader(reader: reader_schemas.ReaderCreate, db: DBSession):
    return await reader_crud.create_reader(db=db, reader=reader)

@router.get("/", response_model=List[reader_schemas.Reader])
async def read_readers(
    db: DBSession,
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    
):
    query = select(Reader)
    
    if search:
        query = query.where(
            Reader.full_name.ilike(f"%{search}%") |
            Reader.address.ilike(f"%{search}%") |
            Reader.phone.ilike(f"%{search}%")
        )
    
    if sort_by:
        if sort_by == "full_name":
            query = query.order_by(Reader.full_name)
        elif sort_by == "reg_date":
            query = query.order_by(Reader.reg_date.desc())
        elif sort_by == "reader_id":
            query = query.order_by(Reader.reader_id)
    else:
        query = query.order_by(Reader.reader_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    readers = result.scalars().all()
    return readers

@router.get("/{reader_id}", response_model=reader_schemas.Reader)
async def read_reader(reader_id: int, db: DBSession):
    db_reader = await reader_crud.get_reader(db, reader_id=reader_id)
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return db_reader

@router.put("/{reader_id}", response_model=reader_schemas.Reader)
async def update_reader(
    reader_id: int,
    reader: reader_schemas.ReaderCreate,
    db: DBSession
):
    db_reader = await reader_crud.get_reader(db, reader_id=reader_id)
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    # Обновление полей
    for field, value in reader.dict().items():
        setattr(db_reader, field, value)
    
    await db.commit()
    await db.refresh(db_reader)
    return db_reader

@router.delete("/{reader_id}")
async def delete_reader(reader_id: int, db: DBSession):
    db_reader = await reader_crud.get_reader(db, reader_id=reader_id)
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    await db.delete(db_reader)
    await db.commit()
    return {"message": "Reader deleted successfully"}