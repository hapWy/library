from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional
from app.schemas.stats import LibraryStats, AuthorStats, SubscriptionStats

async def get_library_stats(
    db: AsyncSession, 
    min_books: Optional[int] = 0,
    sort_by: Optional[str] = "total_books"
) -> List[LibraryStats]:
    valid_sort_fields = ["library_name", "total_books", "total_copies", "total_value"]
    if sort_by not in valid_sort_fields:
        sort_by = "total_books"
    
    order_clause = {
        "library_name": "library_name",
        "total_books": "total_books DESC",
        "total_copies": "total_copies DESC", 
        "total_value": "total_value DESC"
    }[sort_by]
    
    query = f"""
    SELECT 
        library_name,
        total_books,
        total_copies,
        total_value
    FROM vw_library_stats
    WHERE total_books >= :min_books
    ORDER BY {order_clause}
    """
    
    result = await db.execute(
        text(query), 
        {"min_books": min_books}
    )
    stats_data = result.all()
    
    return [LibraryStats(
        library_name=stat.library_name,
        total_books=stat.total_books,
        total_copies=stat.total_copies,
        total_value=stat.total_value
    ) for stat in stats_data]

async def get_author_stats(
    db: AsyncSession,
    min_books: Optional[int] = 1,
    country: Optional[str] = None,
    sort_by: Optional[str] = "total_books"
) -> List[AuthorStats]:
    valid_sort_fields = ["author_name", "total_books", "total_copies", "avg_price"]
    if sort_by not in valid_sort_fields:
        sort_by = "total_books"
    
    order_clause = {
        "author_name": "author_name",
        "total_books": "total_books DESC",
        "total_copies": "total_copies DESC",
        "avg_price": "avg_price DESC"
    }[sort_by]
    
    query = f"""
    SELECT 
        a.author_name,
        a.total_books,
        a.total_copies,
        a.avg_price
    FROM vw_author_stats a
    JOIN authors auth ON a.author_name = auth.full_name
    WHERE a.total_books >= :min_books
    """
    
    params = {"min_books": min_books}
    
    if country:
        query += " AND auth.country = :country"
        params["country"] = country
    
    query += f" ORDER BY {order_clause}"
    
    result = await db.execute(text(query), params)
    stats_data = result.all()
    
    return [AuthorStats(
        author_name=stat.author_name,
        total_books=stat.total_books,
        total_copies=stat.total_copies,
        avg_price=stat.avg_price
    ) for stat in stats_data]

async def get_active_subscriptions(
    db: AsyncSession,
    library_id: Optional[int] = None,
    sort_by: Optional[str] = "issue_date"
) -> List[SubscriptionStats]:
    valid_sort_fields = ["reader_name", "book_title", "library_name", "issue_date", "deposit"]
    if sort_by not in valid_sort_fields:
        sort_by = "issue_date"
    
    order_clause = {
        "reader_name": "reader_name",
        "book_title": "book_title", 
        "library_name": "library_name",
        "issue_date": "issue_date DESC",
        "deposit": "deposit DESC"
    }[sort_by]
    
    query = f"""
    SELECT 
        subscription_id,
        reader_name,
        book_title,
        library_name,
        issue_date,
        return_date,
        deposit
    FROM vw_active_subscriptions
    WHERE 1=1
    """
    
    params = {}
    
    if library_id:
        query += " AND library_id = :library_id"
        params["library_id"] = library_id
    
    query += f" ORDER BY {order_clause}"
    
    result = await db.execute(text(query), params)
    stats_data = result.all()
    
    return [SubscriptionStats(
        subscription_id=stat.subscription_id,
        reader_name=stat.reader_name,
        book_title=stat.book_title,
        library_name=stat.library_name,
        issue_date=stat.issue_date.isoformat() if stat.issue_date else None,
        return_date=stat.return_date.isoformat() if stat.return_date else None,
        deposit=stat.deposit
    ) for stat in stats_data]