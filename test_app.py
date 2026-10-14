
from app import app


def test_normal_readings():
    client = app.test_client()
    response = client.get("/api/readings?scenario=normal")

    assert response.status_code == 200

    data = response.get_json()
    assert data["source"] == "Simulated data"
    assert "temperature" in data
    assert "ph" in data
    assert "oxygen" in data
    assert "turbidity" in data
    assert "ammonia" in data


def test_low_oxygen():
    client = app.test_client()
    response = client.get("/api/readings?scenario=low_oxygen")

    data = response.get_json()
    assert data["oxygen"] == 3.5
    assert any(
        alert["message"] == "Low dissolved oxygen"
        for alert in data["alerts"]
    )


def test_multiple_risks():
    client = app.test_client()
    response = client.get("/api/readings?scenario=multiple_risks")

    data = response.get_json()
    assert data["status"] == "Critical"
    assert len(data["alerts"]) >= 3


def test_health():
    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_history():
    client = app.test_client()
    client.get("/api/readings")
    response = client.get("/api/history")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_invalid_scenario():
    client = app.test_client()
    response = client.get("/api/readings?scenario=invalid")

    assert response.status_code == 400
