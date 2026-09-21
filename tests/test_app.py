from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_delete_participant_removes_email():
    email = "student@test.com"

    signup_response = client.post("/activities/Chess Club/signup?email=" + email)
    assert signup_response.status_code == 200

    response = client.delete(f"/activities/Chess Club/participants/{email}")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_delete_participant_missing_email_returns_404():
    response = client.delete("/activities/Chess Club/participants/notregistered@example.com")
    assert response.status_code == 404
