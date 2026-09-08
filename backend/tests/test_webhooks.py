import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_vapi_tool_call_check_availability():
    payload = {
        "message": {
            "type": "function-call",
            "functionCall": {
                "name": "check_availability",
                "parameters": {"date": "2026-08-20"}
            }
        }
    }
    response = client.post("/api/v1/vapi/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["results"][0]["result"]["available"] is True

def test_vapi_end_of_call_report():
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {"duration": 180},
            "analysis": {"summary": "Customer interested in enterprise voice CRM plan."},
            "artifact": {
                "transcript": "Agent: Welcome. Prospect: I need an automated lead qualification system with gsheets sync.",
                "recordingUrl": "https://sample.com/rec.mp3"
            }
        }
    }
    response = client.post("/api/v1/vapi/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "lead_id" in data
