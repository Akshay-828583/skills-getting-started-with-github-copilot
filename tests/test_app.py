import uuid

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture
def test_email():
    email = f"test-{uuid.uuid4()}@example.com"
    yield email

    for activity in activities.values():
        if email in activity["participants"]:
            activity["participants"].remove(email)


def test_get_activities_returns_activity_details():
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "Chess Club" in response_data
    assert "description" in response_data["Chess Club"]
    assert "participants" in response_data["Chess Club"]


def test_signup_adds_participant_to_activity(test_email):
    # Arrange
    activity_name = "Basketball Club"
    endpoint = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(endpoint, params={"email": test_email})

    # Assert
    assert response.status_code == 200
    assert test_email in activities[activity_name]["participants"]
    assert response.json() == {
        "message": f"Signed up {test_email} for {activity_name}"
    }


def test_signup_rejects_duplicate_participant(test_email):
    # Arrange
    activity_name = "Track and Field"
    endpoint = f"/activities/{activity_name}/signup"
    client.post(endpoint, params={"email": test_email})

    # Act
    response = client.post(endpoint, params={"email": test_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(test_email):
    # Arrange
    endpoint = "/activities/Unknown Club/signup"

    # Act
    response = client.post(endpoint, params={"email": test_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_email(test_email):
    # Arrange
    activity_name = "Chess Club"
    signup_endpoint = f"/activities/{activity_name}/signup"
    delete_endpoint = f"/activities/{activity_name}/participants/{test_email}"
    client.post(signup_endpoint, params={"email": test_email})

    # Act
    response = client.delete(delete_endpoint)

    # Assert
    assert response.status_code == 200
    assert test_email not in activities[activity_name]["participants"]
    assert response.json() == {
        "message": f"Removed {test_email} from {activity_name}"
    }


def test_delete_participant_missing_email_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = f"missing-{uuid.uuid4()}@example.com"
    endpoint = f"/activities/{activity_name}/participants/{email}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_delete_participant_from_unknown_activity_returns_404(test_email):
    # Arrange
    endpoint = f"/activities/Unknown Club/participants/{test_email}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
