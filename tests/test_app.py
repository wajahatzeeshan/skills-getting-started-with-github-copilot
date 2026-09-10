from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Programming Class"
    email = "student@merington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_participant_requires_valid_activity_and_email():
    response = client.delete("/activities/DoesNotExist/unregister?email=student@merington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

    response = client.delete("/activities/Programming Class/unregister?email=missing@merington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not found in this activity"
