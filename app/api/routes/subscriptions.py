from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date

from app.api.deps import DBSession
from app.crud import subscription as subscription_crud
from app.models.book import Book
from app.schemas import subscription as subscription_schemas
from app.models.subscription import Subscription

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

@router.post("/", response_model=subscription_schemas.Subscription)
async def create_subscription(subscription: subscription_schemas.SubscriptionCreate, db: DBSession):
    try:
        return await subscription_crud.create_subscription(db=db, subscription=subscription)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[subscription_schemas.Subscription])
async def read_subscriptions(
    db: DBSession,
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    reader_id: Optional[int] = Query(None),
    book_id: Optional[int] = Query(None),
    library_id: Optional[int] = Query(None),
    active_only: Optional[bool] = Query(False),
    
):
    query = select(Subscription)
    
    if reader_id:
        query = query.where(Subscription.reader_id == reader_id)
    
    if book_id:
        query = query.where(Subscription.book_id == book_id)
    
    if library_id:
        query = query.where(Subscription.library_id == library_id)
    
    if active_only:
        # Активная подписка: return_date is NULL ИЛИ return_date > текущей даты
        from datetime import date
        today = date.today()
        query = query.where(
            (Subscription.return_date.is_(None)) | 
            (Subscription.return_date > today)
        )
    
    if sort_by:
        if sort_by == "issue_date":
            query = query.order_by(Subscription.issue_date.desc())
        elif sort_by == "return_date":
            query = query.order_by(Subscription.return_date.desc())
        elif sort_by == "deposit":
            query = query.order_by(Subscription.deposit.desc())
        elif sort_by == "subscription_id":
            query = query.order_by(Subscription.subscription_id)
    else:
        query = query.order_by(Subscription.subscription_id.desc())
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    return subscriptions

@router.get("/{subscription_id}", response_model=subscription_schemas.Subscription)
async def read_subscription(subscription_id: int, db: DBSession):
    db_subscription = await subscription_crud.get_subscription(db, subscription_id=subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription

@router.put("/{subscription_id}", response_model=subscription_schemas.Subscription)
async def update_subscription(
    subscription_id: int,
    subscription: subscription_schemas.SubscriptionCreate,
    db: DBSession
):
    db_subscription = await subscription_crud.get_subscription(db, subscription_id=subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Обновление полей
    for field, value in subscription.dict().items():
        setattr(db_subscription, field, value)
    
    await db.commit()
    await db.refresh(db_subscription)
    return db_subscription

@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: int, db: DBSession):
    """Удалить подписку и вернуть книгу если она активна"""
    db_subscription = await subscription_crud.get_subscription(db, subscription_id=subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Если подписка активна, увеличиваем количество книг
    if not db_subscription.return_date:
        book_result = await db.execute(
            select(Book).where(Book.book_id == db_subscription.book_id)
        )
        book = book_result.scalar_one_or_none()
        
        if book:
            book.quantity += 1
            print(f"✅ Book quantity increased on delete: {book.title} now has {book.quantity} copies")
    
    await db.delete(db_subscription)
    await db.commit()
    return {"message": "Subscription deleted successfully"}

@router.post("/{subscription_id}/return")
async def return_subscription(subscription_id: int, db: DBSession):
    db_subscription = await subscription_crud.get_subscription(db, subscription_id=subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Помечаем как возвращенную
    db_subscription.return_date = date.today()
    await db.commit()
    
    return {"message": "Book marked as returned"}

@router.get("/detailed/", response_model=List[subscription_schemas.SubscriptionDetailed])
async def read_subscriptions_detailed(db: DBSession):
    return await subscription_crud.get_subscriptions_detailed(db)

@router.get("/reader/{reader_id}/active")
async def get_reader_active_subscriptions(reader_id: int, db: DBSession):
    """Получить активные подписки читателя"""
    result = await db.execute(
        select(Subscription)
        .where(
            Subscription.reader_id == reader_id,
            Subscription.return_date.is_(None)
        )
    )
    subscriptions = result.scalars().all()
    return subscriptions

@router.post("/{subscription_id}/return")
async def return_subscription(subscription_id: int, db: DBSession):
    """Вернуть книгу (пометить подписку как возвращенную и увеличить количество книг)"""
    db_subscription = await subscription_crud.get_subscription(db, subscription_id=subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if db_subscription.return_date is not None:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    # Увеличиваем количество книг
    book_result = await db.execute(
        select(Book).where(Book.book_id == db_subscription.book_id)
    )
    book = book_result.scalar_one_or_none()
    
    if book:
        book.quantity += 1
        print(f"✅ Book returned: {book.title} quantity increased to {book.quantity}")
    else:
        print("⚠️ Book not found when returning")
    
    # Помечаем как возвращенную
    db_subscription.return_date = date.today()
    await db.commit()
    
    return {"message": "Book returned successfully", "book_quantity": book.quantity if book else 0}


@router.get("/active/", response_model=List[subscription_schemas.SubscriptionDetailed])
async def get_active_subscriptions(
    db: DBSession,
    library_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    """Получить активные подписки (без даты возврата)"""
    query = select(Subscription).where(Subscription.return_date.is_(None))
    
    if library_id:
        query = query.where(Subscription.library_id == library_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(
        query.options(
            selectinload(Subscription.book),
            selectinload(Subscription.reader),
            selectinload(Subscription.library)
        )
    )
    subscriptions = result.scalars().all()
    
    # Преобразуем в детальный формат
    subscriptions_detailed = []
    for subscription in subscriptions:
        subscriptions_detailed.append(subscription_schemas.SubscriptionDetailed(
            subscription_id=subscription.subscription_id,
            issue_date=subscription.issue_date,
            return_date=subscription.return_date,
            deposit=subscription.deposit,
            book_title=subscription.book.title,
            reader_name=subscription.reader.full_name,
            library_name=subscription.library.name
        ))
    
    return subscriptions_detailed

@router.get("/{subscription_id}/status")
async def get_subscription_status(subscription_id: int, db: DBSession):
    """Получить статус подписки"""
    db_subscription = await subscription_crud.get_subscription(db, subscription_id=subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    from datetime import date
    today = date.today()
    
    is_active = (
        db_subscription.return_date is None or 
        db_subscription.return_date > today
    )
    
    is_overdue = (
        db_subscription.return_date is not None and 
        db_subscription.return_date < today
    )
    
    return {
        "subscription_id": db_subscription.subscription_id,
        "is_active": is_active,
        "is_overdue": is_overdue,
        "issue_date": db_subscription.issue_date,
        "return_date": db_subscription.return_date,
        "days_remaining": (
            (db_subscription.return_date - today).days 
            if db_subscription.return_date and db_subscription.return_date > today 
            else 0
        ),
        "days_overdue": (
            (today - db_subscription.return_date).days 
            if db_subscription.return_date and db_subscription.return_date < today 
            else 0
        )
    }