from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.subscription import Subscription
from app.models.book import Book
from app.schemas.subscription import SubscriptionCreate, SubscriptionDetailed

async def get_subscriptions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Subscription]:
    result = await db.execute(
        select(Subscription)
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(Subscription.book),
            selectinload(Subscription.reader),
            selectinload(Subscription.library)
        )
    )
    return result.scalars().all()

async def get_subscription(db: AsyncSession, subscription_id: int) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.subscription_id == subscription_id)
        .options(
            selectinload(Subscription.book),
            selectinload(Subscription.reader),
            selectinload(Subscription.library)
        )
    )
    return result.scalar_one_or_none()

async def create_subscription(db: AsyncSession, subscription: SubscriptionCreate) -> Subscription:
    # Check book availability
    book_result = await db.execute(
        select(Book).where(Book.book_id == subscription.book_id)
    )
    book = book_result.scalar_one_or_none()
    
    if not book or book.quantity <= 0:
        raise ValueError("Book not available")
    
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)
    return db_subscription

async def return_book(db: AsyncSession, subscription_id: int) -> bool:
    result = await db.execute(
        select(Subscription).where(Subscription.subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        # Если книга еще не возвращена, увеличиваем количество
        if not subscription.return_date:
            # Получаем книгу и увеличиваем количество
            book_result = await db.execute(
                select(Book).where(Book.book_id == subscription.book_id)
            )
            book = book_result.scalar_one_or_none()
            
            if book:
                book.quantity += 1
                print(f"✅ Book quantity increased: {book.title} now has {book.quantity} copies")
        
        # Устанавливаем дату возврата
        from datetime import date
        subscription.return_date = date.today()
        
        await db.commit()
        return True
    return False

async def get_subscriptions_detailed(db: AsyncSession) -> List[SubscriptionDetailed]:
    result = await db.execute(
        select(Subscription)
        .options(
            selectinload(Subscription.book),
            selectinload(Subscription.reader),
            selectinload(Subscription.library)
        )
    )
    subscriptions = result.scalars().all()
    
    subscriptions_detailed = []
    for subscription in subscriptions:
        subscriptions_detailed.append(SubscriptionDetailed(
            subscription_id=subscription.subscription_id,
            issue_date=subscription.issue_date,
            return_date=subscription.return_date,
            deposit=subscription.deposit,
            book_title=subscription.book.title,
            reader_name=subscription.reader.full_name,
            library_name=subscription.library.name
        ))
    return subscriptions_detailed