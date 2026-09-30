from pydantic import BaseModel, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
