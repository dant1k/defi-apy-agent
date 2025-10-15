from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from agent.graph import graph  # noqa: F401  # ensure graph is importable
from api.cache import StrategyCacheEntry, strategy_cache_key
from api.dependencies import get_strategy_cache as strategy_cache_dependency
from src import api


@pytest.fixture(autouse=True)
def mock_pool_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "start_preload_index", lambda: None)
    monkeypatch.setattr("src.pool_index.POOL_INDEX.ensure_loaded", lambda force=False: None)
    monkeypatch.setattr("src.pool_index.POOL_INDEX.get_pools", lambda token: [])


@pytest.fixture
def cache_stub():
    class StubCache:
        def __init__(self) -> None:
            self.tokens_payload = None
            self.entries = {}
            self.enqueued = []
            self.latest_snapshot = None
            self.protocol_values: list[str] = []
            self.chain_values: list[str] = []

        async def get_tokens(self):
            return self.tokens_payload

        async def set_tokens(self, tokens):
            self.tokens_payload = {"tokens": tokens}

        async def get_strategy(self, key):
            entry = self.entries.get(key)
            if entry is not None:
                return entry
            if self.latest_snapshot:
                for item in self.latest_snapshot.get("items", []):
                    if item.get("id") == key:
                        return item
            return None

        async def enqueue_refresh(self, payload):
            self.enqueued.append(payload)

        async def pop_refresh_request(self, timeout: int = 0):
            return None

        async def get_latest_strategies(self):
            return self.latest_snapshot

        async def get_protocols(self):
            return self.protocol_values

        async def get_chains(self):
            return self.chain_values

        async def get_tvl_history(self, strategy_id: str, limit: int = 96):
            return []

    stub = StubCache()

    async def dependency():
        yield stub

    api.app.dependency_overrides[strategy_cache_dependency] = dependency

    try:
        yield stub
    finally:
        api.app.dependency_overrides.pop(strategy_cache_dependency, None)


def test_health_endpoint(cache_stub) -> None:
    client = TestClient(api.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tokens_endpoint(monkeypatch, cache_stub) -> None:
    client = TestClient(api.app)

    sample_tokens = [
        {"symbol": "BTC", "name": "Bitcoin", "slug": "bitcoin"},
        {"symbol": "ETH", "name": "Ethereum", "slug": "ethereum"},
    ]

    monkeypatch.setattr(api, "get_top_market_tokens", lambda limit=100, force_refresh=False: sample_tokens)

    response = client.get("/tokens")
    assert response.status_code == 200
    assert response.json() == {"tokens": sample_tokens}


def test_strategy_endpoint_success(cache_stub) -> None:
    client = TestClient(api.app)

    sample_response = {
        "status": "ok",
        "token": "ETH",
        "best_strategy": {"platform": "ProtocolA", "action_url": "https://example.com"},
        "alternatives": [],
        "statistics": {"matched": 1, "considered": 2},
        "warnings": [],
    }

    now = datetime.now(timezone.utc)
    key = strategy_cache_key("ETH", "any", True)
    cache_stub.entries[key] = StrategyCacheEntry(
        key=key,
        data=sample_response,
        updated_at=now,
        expires_at=now + timedelta(minutes=10),
    )

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


def test_new_pools_endpoint(monkeypatch, cache_stub) -> None:
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

    response = client.get("/analytics/new-pools?symbols=APT")
    assert response.status_code == 200
    assert response.json() == payload


def test_strategy_endpoint_validation_error(cache_stub) -> None:
    client = TestClient(api.app)

    response = client.post("/strategies", json={"token": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Поле token не может быть пустым"


def test_list_strategies_endpoint(cache_stub) -> None:
    client = TestClient(api.app)
    cache_stub.latest_snapshot = {
        "updated_at": "2024-01-01T00:00:00Z",
        "items": [
            {
                "id": "source:1",
                "chain": "Ethereum",
                "protocol": "ProtocolA",
                "apy": 12.5,
                "tvl_usd": 2_000_000,
                "ai_score": 80,
                "tvl_growth_24h": 5.0,
            },
            {
                "id": "source:2",
                "chain": "Arbitrum",
                "protocol": "ProtocolB",
                "apy": 6.0,
                "tvl_usd": 500_000,
                "ai_score": 40,
                "tvl_growth_24h": -2.0,
            },
        ],
    }

    response = client.get("/strategies?chain=Ethereum&min_tvl=1000000")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "source:1"


def test_top_strategies_endpoint(cache_stub) -> None:
    client = TestClient(api.app)
    cache_stub.latest_snapshot = {
        "updated_at": "2024-01-01T00:00:00Z",
        "items": [
            {"id": "a", "ai_score": 10, "tvl_usd": 1000, "apy": 5},
            {"id": "b", "ai_score": 90, "tvl_usd": 2000, "apy": 20},
        ],
    }

    response = client.get("/strategies/top?limit=1")
    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == "b"


def test_protocols_and_chains(cache_stub) -> None:
    client = TestClient(api.app)
    cache_stub.protocol_values = ["ProtocolA", "ProtocolB"]
    cache_stub.chain_values = ["Ethereum", "Arbitrum"]

    response = client.get("/protocols")
    assert response.status_code == 200
    assert set(response.json()["items"]) == {"ProtocolA", "ProtocolB"}

    response = client.get("/chains")
    assert response.status_code == 200
    assert set(response.json()["items"]) == {"Ethereum", "Arbitrum"}


def test_refresh_endpoint(monkeypatch, cache_stub) -> None:
    client = TestClient(api.app)

    def fake_collect():
        return {"strategies": 1}

    monkeypatch.setattr("api.routers.aggregator.collect_and_store", fake_collect)

    response = client.get("/refresh")
    assert response.status_code == 200
    assert response.json()["details"] == {"strategies": 1}


def test_strategy_details_endpoint(cache_stub) -> None:
    client = TestClient(api.app)
    cache_stub.latest_snapshot = {
        "updated_at": "2024-01-01T00:00:00Z",
        "items": [
            {"id": "strategy-1", "protocol": "A", "chain": "Ethereum", "apy": 10, "tvl_usd": 1_000_000},
        ],
    }
    cache_stub.entries = {}
    cache_stub.latest_snapshot["items"][0]["ai_score"] = 50
    cache_stub.latest_snapshot["items"][0]["ai_comment"] = "Test comment"
    cache_stub.latest_snapshot["items"][0]["token_pair"] = "ETH/DAI"
    cache_stub.latest_snapshot["items"][0]["risk_index"] = 1.2
    cache_stub.latest_snapshot["items"][0]["url"] = "https://example.com"
    cache_stub.protocol_values = ["A"]
    cache_stub.chain_values = ["Ethereum"]
    cache_stub.latest_snapshot["items"][0]["id"] = "strategy-1"
    cache_stub.latest_snapshot["items"][0]["chain"] = "Ethereum"
    cache_stub.latest_snapshot["items"][0]["protocol"] = "ProtocolA"
    cache_stub.latest_snapshot["items"][0]["icon_url"] = "https://icons.llama.fi/protocola"
    cache_stub.latest_snapshot["items"][0]["source"] = "defillama"
    cache_stub.latest_snapshot["items"][0]["updated_at"] = "2024-01-01T00:00:00Z"

    # mimic item hash and tvl history
    cache_stub.enqueued = []

    async def get_history(strategy_id: str, limit: int = 96):
        return [
            {"t": "2024-01-01T00:00:00Z", "v": 1_000_000},
            {"t": "2024-01-01T00:15:00Z", "v": 1_050_000},
        ]

    cache_stub.get_tvl_history = get_history  # type: ignore[attr-defined]

    response = client.get("/strategies/strategy-1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["strategy"]["id"] == "strategy-1"
    assert len(payload["history"]) == 2
