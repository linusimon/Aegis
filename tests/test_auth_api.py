"""Pytest unit tests for Authentication & RBAC API (/api/auth)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_auth_login_admin_success(client):
    payload = {"username": "admin", "password": "admin123"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["role"] == "admin"

def test_auth_login_user_success(client):
    payload = {"username": "user", "password": "user123"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["role"] == "user"

def test_auth_login_invalid_credentials(client):
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401

def test_auth_me_endpoint(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer token_admin_admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"
