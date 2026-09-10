from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange
    original_activities = deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_activities))

    yield

    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_activities))


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Programming Class"
    email = "student@merington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_participant_requires_valid_activity_and_email():
    # Arrange
    activity_name = "Programming Class"
    email = "missing@merington.edu"

    # Act
    response_for_missing_activity = client.delete(
        "/activities/DoesNotExist/unregister?email=student@merington.edu"
    )
    response_for_missing_participant = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response_for_missing_activity.status_code == 404
    assert response_for_missing_activity.json()["detail"] == "Activity not found"
    assert response_for_missing_participant.status_code == 400
    assert response_for_missing_participant.json()["detail"] == "Student not found in this activity"


def test_signup_rejects_non_merington_email_domain():
    # Arrange
    activity_name = "Chess Club"
    email = "student@gmail.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Email must be from the @merington.edu domain"
