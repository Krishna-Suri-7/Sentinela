from sqlalchemy import Column, Integer, Float, String
from app.core.database import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    monthly_income = Column(Float, default=0.0)
    fixed_expenses = Column(Float, default=0.0)
    savings_goal = Column(Float, default=0.0)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    emoji = Column(String, default="🏷️")
