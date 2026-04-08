def test_get_default_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbols"] == ["BTC", "ETH", "HBAR", "IOTA"]
    assert data["email"] == ""
    assert "alert_preferences" in data


def test_update_symbols(client):
    # First create default settings
    client.get("/api/settings")

    resp = client.put(
        "/api/settings",
        json={"symbols": ["SOL", "AVAX"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbols"] == ["SOL", "AVAX"]


def test_update_requires_two_symbols(client):
    client.get("/api/settings")
    resp = client.put("/api/settings", json={"symbols": ["BTC"]})
    assert resp.status_code == 400


def test_update_rejects_unsupported_symbol(client):
    client.get("/api/settings")
    resp = client.put("/api/settings", json={"symbols": ["BTC", "FAKE"]})
    assert resp.status_code == 400


def test_update_email(client):
    client.get("/api/settings")
    resp = client.put("/api/settings", json={"email": "test@example.com"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_update_alert_preferences(client):
    client.get("/api/settings")
    prefs = {"signal_change": False, "rsi_extreme": True}
    resp = client.put("/api/settings", json={"alert_preferences": prefs})
    assert resp.status_code == 200
    assert resp.json()["alert_preferences"] == prefs
