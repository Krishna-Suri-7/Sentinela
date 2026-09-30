from pydantic import BaseModel, ConfigDict
from typing import Optional

class SettingsBase(BaseModel):
    monthly_income: float
    fixed_expenses: float
    savings_goal: float

class SettingsResponse(SettingsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str
    emoji: str

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
