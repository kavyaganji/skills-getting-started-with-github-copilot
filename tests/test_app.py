"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "testuser@mergington.edu"})
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    activities_response = client.get("/activities")
    assert "testuser@mergington.edu" in activities_response.json()["Chess Club"]["participants"]


def test_signup_duplicate(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_remove_participant_success(client):
    client.post("/activities/Gym Class/signup", params={"email": "remove-test@mergington.edu"})
    response = client.delete("/activities/Gym Class/participants", params={"email": "remove-test@mergington.edu"})
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    activities_response = client.get("/activities")
    assert "remove-test@mergington.edu" not in activities_response.json()["Gym Class"]["participants"]


def test_remove_participant_not_found(client):
    response = client.delete("/activities/Chess Club/participants", params={"email": "notfound@mergington.edu"})
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
