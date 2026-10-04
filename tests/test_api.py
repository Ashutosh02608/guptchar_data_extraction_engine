"""
Unit and integration tests for FastAPI REST API endpoints.
"""

from fastapi.testclient import TestClient
from guptchar.api.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_static_web_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "GUPTCHAR" in response.text
    assert "Extraction Parameters" in response.text


def test_static_assets():
    css_resp = client.get("/app.css")
    assert css_resp.status_code == 200
    assert "--bg-primary" in css_resp.text

    js_resp = client.get("/app.js")
    assert js_resp.status_code == 200
    assert "Guptchar Client Engine" in js_resp.text
