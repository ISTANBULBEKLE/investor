def test_invalid_symbol_returns_400(client):
    resp = client.get("/api/market/INVALID/price")
    assert resp.status_code == 400
    assert "Unsupported symbol" in resp.json()["detail"]


def test_valid_symbol_accepted(client):
    # This calls real Binance API — only check status, not values
    resp = client.get("/api/market/BTC/price")
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC"
    assert data["price"] > 0


def test_ohlcv_endpoint(client):
    resp = client.get("/api/market/ETH/ohlcv?timeframe=1h&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "ETH"
    assert data["timeframe"] == "1h"
    assert len(data["data"]) == 5


def test_ohlcv_invalid_timeframe(client):
    resp = client.get("/api/market/BTC/ohlcv?timeframe=2h")
    assert resp.status_code == 422  # Validation error
