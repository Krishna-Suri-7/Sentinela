from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_settings():
    response = client.get("/api/v1/settings/")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_income" in data
    assert "fixed_expenses" in data
    assert "savings_goal" in data

def test_update_settings():
    payload = {
        "monthly_income": 4000.0,
        "fixed_expenses": 1500.0,
        "savings_goal": 800.0
    }
    response = client.put("/api/v1/settings/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_income"] == 4000.0

def test_get_categories():
    response = client.get("/api/v1/settings/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
