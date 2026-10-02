import os
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.transaction import TransactionCreate
from app.models.transaction import Transaction
from app.core.database import get_db
from app.services.telegram import send_transaction_notification

router = APIRouter()

EXPECTED_API_KEY = os.getenv("API_KEY", "change_this_default_key")


@router.post("/webhook", status_code=status.HTTP_201_CREATED)
async def receive_transaction(
    payload: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )

    # Save to database
    new_tx = Transaction(
        merchant=payload.merchant,
        amount=payload.amount,
        currency=payload.currency,
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    from app.models.settings import Category
    categories_db = db.query(Category).all()
    categories_list = [{"name": c.name, "emoji": c.emoji} for c in categories_db]

    background_tasks.add_task(
        send_transaction_notification,
        merchant=new_tx.merchant,
        amount=new_tx.amount,
        currency=new_tx.currency,
        tx_id=new_tx.id,
        categories=categories_list,
    )

    return {
        "status": "received",
        "tx_id": new_tx.id,
        "merchant": new_tx.merchant,
        "amount": new_tx.amount,
        "currency": new_tx.currency,
    }
