from fastapi import FastAPI
from app.api.v1.webhook import router as webhook_router
from app.api.v1.telegram import router as telegram_router
from app.api.v1.summary import router as summary_router
from app.core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinela")

app.include_router(webhook_router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(telegram_router, prefix="/api/v1", tags=["Telegram"])
app.include_router(summary_router, prefix="/api/v1", tags=["Summary"])

@app.get("/")
def root():
    return {"message": "Sentinela API is running."}

@app.get("/health")
def health_check():
    return {"status": "ok", "engine": "operational"}