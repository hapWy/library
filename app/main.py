import asyncio
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from app.db.session import Session, engine, create_views_and_triggers
from app.db.base_class import Base
from app.api.deps import DBSession
from app.api.routes.libraries import router as libraries_router
from app.api.routes.topics import router as topics_router
from app.api.routes.authors import router as authors_router
from app.api.routes.books import router as books_router
from app.api.routes.readers import router as readers_router
from app.api.routes.subscriptions import router as subscriptions_router
from app.crud.stats import get_library_stats, get_author_stats, get_active_subscriptions
from app.schemas.stats import LibraryStats, AuthorStats, SubscriptionStats

app = FastAPI(
    title="Library Management System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(libraries_router)
app.include_router(topics_router)
app.include_router(authors_router)
app.include_router(books_router)
app.include_router(readers_router)
app.include_router(subscriptions_router)

async def init_db():
    """Initialize database tables, views and triggers"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Database initialization attempt {attempt + 1}/{max_retries}")
            
            # Создаем таблицы
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully!")
            
            # Ждем немного перед созданием представлений
            await asyncio.sleep(1)
            
            # Создаем представления и триггеры
            await create_views_and_triggers()
            
            print("✅ Database initialization completed successfully!")
            return
            
        except Exception as e:
            print(f"❌ Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("🔄 Retrying in 3 seconds...")
                await asyncio.sleep(3)
            else:
                print("❌ All database initialization attempts failed")
                raise

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Library Management System...")
    
    # Wait a bit for database to be ready
    await asyncio.sleep(5)
    
    try:
        # Initialize database
        await init_db()
        print("🎉 Application started successfully!")
    except Exception as e:
        print(f"💥 Application startup failed: {e}")
        # Приложение все равно запускается, но без представлений
        print("⚠️  Application running without views and triggers")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface"""
    try:
        with open("app/static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>Library System</title></head>
            <body>
                <h1>Library Management System</h1>
                <p>Static files not found. Please check the deployment.</p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Simple health check"""
    try:
        async with Session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

# Report endpoints
@app.get("/reports/library-stats/", response_model=List[LibraryStats])
async def get_library_stats_report(
    db: DBSession,
    min_books: Optional[int] = Query(0, description="Минимальное количество книг"),
    sort_by: Optional[str] = Query("total_books", description="Поле для сортировки")
):
    """Отчет по статистике библиотек"""
    return await get_library_stats(db, min_books, sort_by)

@app.get("/reports/author-stats/", response_model=List[AuthorStats])
async def get_author_stats_report(
    db: DBSession,
    min_books: Optional[int] = Query(1, description="Минимальное количество книг"),
    country: Optional[str] = Query(None, description="Фильтр по стране"),
    sort_by: Optional[str] = Query("total_books", description="Поле для сортировки")
):
    """Отчет по статистике авторов"""
    return await get_author_stats(db, min_books, country, sort_by)

@app.get("/reports/active-subscriptions/", response_model=List[SubscriptionStats])
async def get_active_subscriptions_report(
    db: DBSession,
    library_id: Optional[int] = Query(None, description="Фильтр по библиотеке"),
    sort_by: Optional[str] = Query("issue_date", description="Поле для сортировки")
):
    """Отчет по активным подпискам"""
    return await get_active_subscriptions(db, library_id, sort_by)

@app.get("/reports/book-prices/")
async def get_book_prices_report(
    db: DBSession,
    min_price: Optional[float] = Query(0, description="Минимальная цена"),
    max_price: Optional[float] = Query(1000, description="Максимальная цена"),
    topic_id: Optional[int] = Query(None, description="Фильтр по теме")
):
    """Отчет по ценам книг с группировкой по библиотекам"""
    try:
        query = """
        SELECT 
            l.name as library_name,
            COUNT(*) as book_count,
            AVG(b.price) as avg_price,
            MAX(b.price) as max_price,
            MIN(b.price) as min_price,
            SUM(b.quantity * b.price) as total_value
        FROM books b
        JOIN libraries l ON b.library_id = l.library_id
        WHERE b.price BETWEEN :min_price AND :max_price
        """
        
        params = {"min_price": min_price, "max_price": max_price}
        
        if topic_id:
            query += " AND b.topic_id = :topic_id"
            params["topic_id"] = topic_id
        
        query += " GROUP BY l.library_id, l.name HAVING COUNT(*) > 0 ORDER BY total_value DESC"
        
        result = await db.execute(text(query), params)
        rows = result.all()
        
        return [{
            "library_name": row.library_name,
            "book_count": row.book_count,
            "avg_price": float(row.avg_price) if row.avg_price else 0,
            "max_price": float(row.max_price) if row.max_price else 0,
            "min_price": float(row.min_price) if row.min_price else 0,
            "total_value": float(row.total_value) if row.total_value else 0
        } for row in rows]
        
    except Exception as e:
        print(f"❌ Error generating book prices report: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)