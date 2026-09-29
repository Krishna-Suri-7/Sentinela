from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.summary import get_daily_summary

router = APIRouter()

@router.get("/summary/daily")
def daily_summary(allowance: float = 50.0, db: Session = Depends(get_db)):
    return get_daily_summary(db, daily_allowance=allowance)
