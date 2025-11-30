from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import DBSession
from app.api.routes import libraries, topics, authors, books, readers, subscriptions
from app.crud import stats as stats_crud
from app.schemas import stats as stats_schemas

app = FastAPI(title="Library Management System", version="1.0.0")

# Include routers
app.include_router(libraries.router)
app.include_router(topics.router)
app.include_router(authors.router)
app.include_router(books.router)
app.include_router(readers.router)
app.include_router(subscriptions.router)



@app.get("/")
async def read_root():
    return {"message": "Library Management System API"}

@app.get("/stats/library/", response_model=List[stats_schemas.LibraryStats])
async def get_library_stats(db: DBSession):
    return await stats_crud.get_library_stats(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)