from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

# Use the default fallback key since the module is already loaded
TEST_API_KEY = "change_this_default_key"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "engine": "operational"}

def test_webhook_missing_key():
    # Test completely missing API key (FastAPI validates headers and returns 422)
    payload = {
        "merchant": "Test Store",
        "amount": 15.50,
        "currency": "EUR"
    }
    response = client.post("/api/v1/transactions/webhook", json=payload)
    assert response.status_code == 422

def test_webhook_unauthorized():
    # Test WRONG API key
    headers = {"X-API-Key": "wrong_password"}
    payload = {
        "merchant": "Test Store",
        "amount": 15.50,
        "currency": "EUR"
    }
    response = client.post("/api/v1/transactions/webhook", headers=headers, json=payload)
    assert response.status_code == 401

def test_webhook_invalid_payload():
    # Test missing amount field
    headers = {"X-API-Key": TEST_API_KEY}
    payload = {
        "merchant": "Test Store",
        "currency": "EUR"
    }
    response = client.post("/api/v1/transactions/webhook", headers=headers, json=payload)
    assert response.status_code == 422 # Unprocessable Entity
