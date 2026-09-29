from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    merchant: str
    amount: float
    currency: str = Field(default="EUR")

class TransactionResponse(TransactionCreate):
    id: int
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
