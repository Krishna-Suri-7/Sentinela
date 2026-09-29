import os
import calendar
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction

def get_daily_summary(db: Session, daily_allowance: float = None):
    now = datetime.now()
    today = now.date()
    
    # 1. Load config from Environment Variables (for cloud deployment)
    income = float(os.getenv("MONTHLY_INCOME", "3000.0"))
    fixed = float(os.getenv("FIXED_EXPENSES", "1200.0"))
    savings = float(os.getenv("SAVINGS_GOAL", "500.0"))
    
    disposable_income = income - fixed - savings
    
    # 2. Get total spent THIS month
    first_day_of_month = today.replace(day=1)
    
    monthly_spent = db.query(func.sum(Transaction.amount)).filter(
        func.date(Transaction.created_at) >= first_day_of_month
    ).scalar() or 0.0
    
    # 3. Calculate remaining monthly budget
    remaining_monthly = disposable_income - monthly_spent
    
    # 4. Calculate days remaining in the month (including today)
    _, last_day = calendar.monthrange(today.year, today.month)
    days_remaining = (last_day - today.day) + 1
    
    # 5. Dynamic daily allowance
    dynamic_daily_allowance = remaining_monthly / days_remaining if days_remaining > 0 else remaining_monthly
    
    # 6. Calculate how much was spent SPECIFICALLY today
    total_spent_today = db.query(func.sum(Transaction.amount)).filter(
        func.date(Transaction.created_at) == today
    ).scalar() or 0.0
    
    # The actual remaining for today is the dynamic allowance minus what we already spent today
    remaining_today = dynamic_daily_allowance - total_spent_today
    
    return {
        "date": str(today),
        "monthly_disposable": disposable_income,
        "monthly_spent": monthly_spent,
        "remaining_monthly": remaining_monthly,
        "days_remaining_in_month": days_remaining,
        "calculated_daily_allowance": round(dynamic_daily_allowance, 2),
        "total_spent_today": round(total_spent_today, 2),
        "remaining": round(remaining_today, 2),
        "status": "under_budget" if remaining_today >= 0 else "over_budget"
    }
