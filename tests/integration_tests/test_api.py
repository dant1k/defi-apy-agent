from fastapi.testclient import TestClient

from agent.graph import graph  # noqa: F401  # ensure graph is importable
from src import api


def test_health_endpoint() -> None:
    client = TestClient(api.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tokens_endpoint(monkeypatch) -> None:
    client = TestClient(api.app)

    sample_tokens = [
        {"symbol": "BTC", "name": "Bitcoin", "slug": "bitcoin"},
        {"symbol": "ETH", "name": "Ethereum", "slug": "ethereum"},
    ]

    monkeypatch.setattr(api, "get_top_market_tokens", lambda limit=100, force_refresh=False: sample_tokens)

    response = client.get("/tokens")
    assert response.status_code == 200
    assert response.json() == {"tokens": sample_tokens}


def test_strategy_endpoint_success(monkeypatch) -> None:
    client = TestClient(api.app)

    sample_response = {
        "status": "ok",
        "token": "ETH",
        "best_strategy": {"platform": "ProtocolA", "action_url": "https://example.com"},
        "alternatives": [],
        "statistics": {"matched": 1, "considered": 2},
        "warnings": [],
    }

    def fake_run_agent(*args, **kwargs):
        return sample_response

    monkeypatch.setattr(api, "run_agent", fake_run_agent)

    response = client.post(
        "/strategies",
        json={
            "token": "ETH",
            "preferences": {"min_apy": 5},
            "result_limit": 10,
        },
    )

    assert response.status_code == 200
    assert response.json() == sample_response


def test_new_pools_endpoint(monkeypatch) -> None:
    client = TestClient(api.app)

    payload = {
        "period": "7d",
        "days": 7,
        "min_tvl": 5_000_000,
        "filters": {"symbols": [], "chains": []},
        "count": 1,
        "pools": [
            {
                "pool_id": "pool-1",
                "pair": "APT-USDC",
                "protocol": "protocol-a",
                "chain": "Aptos",
                "tvl_usd": 6500000.0,
                "apy": 12.0,
                "tvl_change_pct": 20.0,
                "apy_change_pct": 5.0,
                "momentum": 14.0,
                "category": "token-stable",
                "first_seen": None,
                "action_url": "https://protocol-a.example",
            }
        ],
    }

    monkeypatch.setattr(api, "get_new_pools", lambda *args, **kwargs: payload)

    response = client.get("/analytics/new-pools")
    assert response.status_code == 200
    assert response.json() == payload


def test_strategy_endpoint_validation_error() -> None:
    client = TestClient(api.app)

    response = client.post("/strategies", json={"token": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Поле token не может быть пустым"
