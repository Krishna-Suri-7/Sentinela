from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.settings import Settings, Category
from app.schemas.settings import SettingsBase, SettingsResponse, CategoryBase, CategoryResponse
import os

router = APIRouter()

@router.get("/", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        # Create default from env vars
        settings = Settings(
            monthly_income=float(os.getenv("MONTHLY_INCOME", "3000.0")),
            fixed_expenses=float(os.getenv("FIXED_EXPENSES", "1200.0")),
            savings_goal=float(os.getenv("SAVINGS_GOAL", "500.0"))
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/", response_model=SettingsResponse)
def update_settings(settings_in: SettingsBase, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
    
    settings.monthly_income = settings_in.monthly_income
    settings.fixed_expenses = settings_in.fixed_expenses
    settings.savings_goal = settings_in.savings_goal
    db.commit()
    db.refresh(settings)
    return settings

@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    if not categories:
        default_cats = [
            Category(name="Food", emoji="🍔"),
            Category(name="Transport", emoji="🚗"),
            Category(name="Shopping", emoji="🛍️"),
            Category(name="Entertainment", emoji="🍿")
        ]
        db.add_all(default_cats)
        db.commit()
        categories = db.query(Category).all()
    return categories

@router.post("/categories", response_model=CategoryResponse)
def add_category(cat_in: CategoryBase, db: Session = Depends(get_db)):
    cat = Category(name=cat_in.name, emoji=cat_in.emoji)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"status": "ok"}
