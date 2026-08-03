"""Pytest unit tests for PDF Executive Report Export (/api/export-report?format=pdf)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_export_report_pdf(client):
    response = client.get("/api/export-report?format=pdf")
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")
    assert len(response.content) > 100
    # Verify PDF magic header %PDF
    assert response.content.startswith(b"%PDF")

def test_api_export_report_html_default(client):
    response = client.get("/api/export-report?format=html")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Aegis AI" in response.text
