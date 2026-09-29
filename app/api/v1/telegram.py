from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.transaction import Transaction
from app.services.telegram import edit_message_to_confirmed, answer_callback_query
from app.services.summary import get_daily_summary

router = APIRouter()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = await request.json()
    
    if "callback_query" in data:
        callback_query = data["callback_query"]
        callback_data = callback_query.get("data")
        message = callback_query.get("message")
        callback_query_id = callback_query.get("id")
        
        if callback_query_id:
            background_tasks.add_task(answer_callback_query, callback_query_id)
            
        if callback_data and callback_data.startswith("tx_"):
            # Expected format: tx_{id}_{category}
            parts = callback_data.split("_", 2)
            if len(parts) == 3:
                _, tx_id_str, category = parts
                if tx_id_str.isdigit():
                    tx_id = int(tx_id_str)
                    
                    # Update database
                    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
                    if tx:
                        tx.category = category
                        db.commit()
                        
                        # Get daily summary for remaining budget
                        summary = get_daily_summary(db, daily_allowance=50.0)
                        
                        # Edit message to remove inline keyboard and confirm category
                        if message:
                            chat_id = message["chat"]["id"]
                            message_id = message["message_id"]
                            background_tasks.add_task(
                                edit_message_to_confirmed,
                                chat_id=chat_id,
                                message_id=message_id,
                                merchant=tx.merchant,
                                amount=tx.amount,
                                currency=tx.currency,
                                category=category,
                                remaining_budget=summary["remaining"]
                            )
    
    return {"status": "ok"}
