def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "uptime_seconds" in data


def test_health_returns_uptime(client):
    resp = client.get("/health")
    data = resp.json()
    assert data["uptime_seconds"] >= 0
