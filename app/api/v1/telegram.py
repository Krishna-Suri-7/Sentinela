from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.settings import Category
from app.services.telegram import edit_message_to_confirmed, answer_callback_query
from app.services.summary import get_daily_summary
import os
import httpx

router = APIRouter()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = await request.json()
    
    # Handle normal messages (like /summary)
    if "message" in data and "text" in data["message"]:
        msg_text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        
        if msg_text.startswith("/summary"):
            summary = get_daily_summary(db)
            rem = summary["remaining"]
            
            # Calculate weekly spending by category
            one_week_ago = datetime.now() - timedelta(days=7)
            weekly_stats = db.query(
                Transaction.category, 
                func.sum(Transaction.amount)
            ).filter(
                Transaction.created_at >= one_week_ago
            ).group_by(Transaction.category).all()
            
            cat_text = "\n".join([f"• {cat}: €{amt:.2f}" for cat, amt in weekly_stats])
            if not cat_text:
                cat_text = "No spending in the last 7 days."
                
            text = (
                f"📊 *Current Status*\n\n"
                f"💸 *Spent Today:* €{summary['total_spent_today']:.2f}\n"
                f"💰 *Remaining Today:* €{rem:.2f}\n"
                f"📅 *Remaining Monthly:* €{summary['remaining_monthly']:.2f}\n\n"
                f"📈 *Last 7 Days by Category:*\n"
                f"{cat_text}"
            )
            
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if token:
                async with httpx.AsyncClient() as client:
                    await client.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload)
    
    # Handle interactive button taps
    if "callback_query" in data:
        callback_query = data["callback_query"]
        callback_data = callback_query.get("data")
        message = callback_query.get("message")
        callback_query_id = callback_query.get("id")
        
        if callback_query_id:
            background_tasks.add_task(answer_callback_query, callback_query_id)
            
        if callback_data and callback_data.startswith("tx_"):
            parts = callback_data.split("_", 2)
            if len(parts) == 3:
                _, tx_id_str, category = parts
                if tx_id_str.isdigit():
                    tx_id = int(tx_id_str)
                    
                    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
                    if tx:
                        tx.category = category
                        db.commit()
                        
                        summary = get_daily_summary(db)
                        categories_db = db.query(Category).all()
                        categories_list = [{"name": c.name, "emoji": c.emoji} for c in categories_db]
                        
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
                                remaining_budget=summary["remaining"],
                                categories=categories_list,
                                tx_id=tx.id
                            )
    
    return {"status": "ok"}
