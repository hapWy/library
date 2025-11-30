from fastapi import APIRouter, HTTPException
from typing import List

from app.api.deps import DBSession
from app.crud import subscription as subscription_crud
from app.schemas import subscription as subscription_schemas

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/", response_model=subscription_schemas.Subscription)
async def create_subscription(subscription: subscription_schemas.SubscriptionCreate, db: DBSession):
    try:
        return await subscription_crud.create_subscription(db=db, subscription=subscription)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[subscription_schemas.Subscription])
async def read_subscriptions(db: DBSession, skip: int = 0, limit: int = 100):
    subscriptions = await subscription_crud.get_subscriptions(db, skip=skip, limit=limit)
    return subscriptions

@router.get("/detailed/", response_model=List[subscription_schemas.SubscriptionDetailed])
async def read_subscriptions_detailed(db: DBSession):
    return await subscription_crud.get_subscriptions_detailed(db)

@router.delete("/{subscription_id}")
async def return_book(subscription_id: int, db: DBSession):
    success = await subscription_crud.return_book(db, subscription_id=subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Book returned successfully"}