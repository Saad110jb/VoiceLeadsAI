import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_get_leads():
    response = client.get("/api/v1/leads")
    assert response.status_code == 200
    leads = response.json()
    assert isinstance(leads, list)
    assert len(leads) > 0

def test_get_lead_stats():
    response = client.get("/api/v1/leads/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_leads" in stats
    assert "hot_leads" in stats
    assert "conversion_rate" in stats

def test_create_and_delete_lead():
    new_lead = {
        "name": "Integration Test Lead",
        "email": "test@voiceleads.ai",
        "phone": "+1555000111",
        "company": "Test Enterprise",
        "lead_temperature": "HOT",
        "summary": "Automated unit test lead payload.",
        "budget": "$10,000",
        "timeframe": "Immediate",
        "intent": "Unit Testing",
        "status": "QUALIFIED"
    }
    create_res = client.post("/api/v1/leads", json=new_lead)
    assert create_res.status_code == 200
    created_data = create_res.json()
    assert created_data["name"] == "Integration Test Lead"
    lead_id = created_data["id"]

    # Delete
    del_res = client.delete(f"/api/v1/leads/{lead_id}")
    assert del_res.status_code == 200
