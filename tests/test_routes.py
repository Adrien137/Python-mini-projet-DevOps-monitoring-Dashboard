"""Tests des routes de api.main via FastAPI TestClient."""

import os

os.environ["API_KEY"] = "test-key-123"

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_returns_expected_fields():
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "cpu_percent" in body
    assert "memory_percent" in body
    assert "disk_percent" in body


def test_create_server_without_api_key_returns_403():
    response = client.post(
        "/servers", json={"name": "srv1", "host": "localhost", "port": 8000}
    )
    assert response.status_code == 403


def test_create_server_with_valid_api_key_returns_201():
    response = client.post(
        "/servers",
        json={"name": "srv1", "host": "localhost", "port": 8000},
        headers={"X-API-Key": "test-key-123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "srv1"
    assert body["status"] == "DOWN"


def test_delete_unknown_server_returns_404():
    response = client.delete(
        "/servers/does-not-exist",
        headers={"X-API-Key": "test-key-123"},
    )
    assert response.status_code == 404


def test_list_servers_includes_created_server():
    client.post(
        "/servers",
        json={"name": "srv2", "host": "localhost", "port": 9000},
        headers={"X-API-Key": "test-key-123"},
    )
    response = client.get("/servers")
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert "srv2" in names


def test_delete_server_with_valid_id_returns_204():
    create_resp = client.post(
        "/servers",
        json={"name": "srv-to-delete", "host": "localhost", "port": 7000},
        headers={"X-API-Key": "test-key-123"},
    )
    server_id = create_resp.json()["id"]

    delete_resp = client.delete(
        f"/servers/{server_id}", headers={"X-API-Key": "test-key-123"}
    )
    assert delete_resp.status_code == 204

    response = client.get("/servers")
    ids = [s["id"] for s in response.json()]
    assert server_id not in ids


def test_check_unknown_server_returns_404():
    response = client.post("/servers/does-not-exist/check")
    assert response.status_code == 404


def test_check_server_returns_status():
    create_resp = client.post(
        "/servers",
        json={"name": "srv-check", "host": "127.0.0.1", "port": 9999},
        headers={"X-API-Key": "test-key-123"},
    )
    server_id = create_resp.json()["id"]

    response = client.post(f"/servers/{server_id}/check")
    assert response.status_code == 200
    assert response.json()["status"] in ("UP", "DEGRADED", "DOWN")


def test_ws_metrics_streams_json_frame():
    with client.websocket_connect("/ws/metrics") as websocket:
        data = websocket.receive_json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data
