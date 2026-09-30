from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.api.v1.webhook import router as webhook_router
from app.api.v1.telegram import router as telegram_router
from app.api.v1.summary import router as summary_router
from app.api.v1.settings import router as settings_router
from app.core.database import engine, Base

# Import models so SQLAlchemy creates them
from app.models import transaction, settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinela")

app.include_router(webhook_router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(telegram_router, prefix="/api/v1", tags=["Telegram"])
app.include_router(summary_router, prefix="/api/v1", tags=["Summary"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])

# Mount web dashboard
os.makedirs("static", exist_ok=True)
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")

@app.get("/health")
def health_check():
    return {"status": "ok", "engine": "operational"}