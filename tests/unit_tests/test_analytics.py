from datetime import datetime, timedelta, timezone

import pytest

from src import analytics


@pytest.fixture(autouse=True)
def reset_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    analytics._all_pools_cache = None  # type: ignore[attr-defined]
    analytics._chart_cache.clear()  # type: ignore[attr-defined]
    analytics._project_url_cache.clear()  # type: ignore[attr-defined]


def build_chart(days: int, now: datetime) -> list[dict[str, float | str | None]]:
    entries = []
    for offset in range(days, -1, -1):
        entries.append(
            {
                "timestamp": (now - timedelta(days=offset)).isoformat(),
                "tvlUsd": 5_000_000 + (days - offset) * 500_000,
                "apy": 10 + (days - offset) * 0.5,
                "apyBase": None,
                "apyReward": None,
                "il7d": None,
                "apyBase7d": None,
            }
        )
    return entries


def test_get_new_pools_returns_sorted(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.now(timezone.utc)

    pools = [
        {
            "pool": "pool-1",
            "symbol": "APT-USDC",
            "project": "protocol-a",
            "chain": "Aptos",
            "tvlUsd": 6_500_000,
            "apy": 12,
            "count": 2,
        },
        {
            "pool": "pool-2",
            "symbol": "BTC-wBTC",
            "project": "protocol-b",
            "chain": "Ethereum",
            "tvlUsd": 8_000_000,
            "apy": 4,
            "count": 10,
        },
    ]

    monkeypatch.setattr(analytics, "get_all_pools", lambda force_refresh=False: pools)
    monkeypatch.setattr(analytics, "get_chart", lambda pool_id, force_refresh=False: build_chart(2, now))
    monkeypatch.setattr(analytics, "get_project_url", lambda project: f"https://{project}.example")

    result = analytics.get_new_pools(
        period="7d",
        min_tvl=5_000_000,
        symbols=("APT",),
        chains=(),
        sort="momentum",
        limit=10,
    )

    assert result["period"] == "7d"
    assert result["count"] == 1
    pool = result["pools"][0]
    assert pool["pair"] == "APT-USDC"
    assert pool["momentum"] > 0
    assert pool["tvl_change_pct"] > 0


def test_get_new_pools_filters_by_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.now(timezone.utc)
    pools = [
        {
            "pool": "pool-3",
            "symbol": "APT-USDC",
            "project": "protocol-a",
            "chain": "Aptos",
            "tvlUsd": 5_500_000,
            "apy": 9,
            "count": 1,
        },
        {
            "pool": "pool-4",
            "symbol": "ETH-USDT",
            "project": "protocol-b",
            "chain": "Ethereum",
            "tvlUsd": 9_000_000,
            "apy": 5,
            "count": 1,
        },
    ]

    monkeypatch.setattr(analytics, "get_all_pools", lambda force_refresh=False: pools)
    monkeypatch.setattr(analytics, "get_chart", lambda pool_id, force_refresh=False: build_chart(1, now))
    monkeypatch.setattr(analytics, "get_project_url", lambda project: None)

    result = analytics.get_new_pools(
        period="24h",
        min_tvl=5_000_000,
        chains=("aptos",),
        limit=5,
    )

    assert result["count"] == 1
    assert result["pools"][0]["chain"] == "Aptos"
