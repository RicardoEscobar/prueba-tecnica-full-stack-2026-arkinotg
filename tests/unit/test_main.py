"""
Unit tests for main.py
"""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_get_overdue_policies():
    response = client.get("/advisors/1/expired-policies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    for policy in data:
        assert "id" in policy
        assert "client_id" in policy
        assert "insurer" in policy
        assert "expiration_date" in policy
        assert "status" in policy
        assert "days_overdue" in policy
        assert "contact_attempts" in policy
        assert "priority" in policy
        assert "recommended_action" in policy
