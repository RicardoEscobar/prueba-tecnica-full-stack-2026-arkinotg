"""
Unit tests for main.py
"""
import sqlite3
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

import main as main_module


@pytest.fixture
def client(monkeypatch):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()

    now = datetime.now()
    normal_expiration = (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    urgent_expiration = (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.executescript(
        """
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL
        );

        CREATE TABLE policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            advisor_id TEXT NOT NULL,
            client_id INTEGER NOT NULL,
            insurer TEXT NOT NULL,
            expiration_date TEXT NOT NULL,
            status INTEGER NOT NULL
        );

        CREATE TABLE contact_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            attempt_date TEXT
        );
        """
    )

    cursor.execute(
        "INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
        ("John Doe", "john.doe@example.com", "123-456-7890"),
    )
    cursor.execute(
        "INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
        ("Jane Smith", "jane.smith@example.com", "987-654-3210"),
    )

    cursor.execute(
        """
        INSERT INTO policies (advisor_id, client_id, insurer, expiration_date, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("1", 1, "Insurer A", normal_expiration, 1),
    )
    normal_policy_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO policies (advisor_id, client_id, insurer, expiration_date, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("1", 2, "Insurer B", urgent_expiration, 1),
    )
    urgent_policy_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO contact_attempts (policy_id, attempt_date) VALUES (?, ?)",
        (normal_policy_id, now.strftime("%Y-%m-%d %H:%M:%S")),
    )
    cursor.execute(
        "INSERT INTO contact_attempts (policy_id, attempt_date) VALUES (?, ?)",
        (urgent_policy_id, now.strftime("%Y-%m-%d %H:%M:%S")),
    )
    cursor.execute(
        "INSERT INTO contact_attempts (policy_id, attempt_date) VALUES (?, ?)",
        (urgent_policy_id, now.strftime("%Y-%m-%d %H:%M:%S")),
    )

    conn.commit()

    def fake_get_db_connection(db_path=None):
        return conn

    monkeypatch.setattr(main_module, "get_db_connection", fake_get_db_connection)

    with TestClient(main_module.app) as test_client:
        yield test_client

    conn.close()


def test_get_overdue_policies(client):
    response = client.get("/advisors/1/expired-policies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    priorities = {policy["priority"] for policy in data}
    assert priorities == {"normal", "urgent"}

    for policy in data:
        assert "policy_id" in policy
        assert "client_name" in policy
        assert "client_phone" in policy
        assert "insurer" in policy
        assert "expiration_date" in policy
        assert "days_overdue" in policy
        assert "contact_attempts" in policy
        assert "priority" in policy
        assert "recommended_action" in policy
