from datetime import datetime, timedelta

import pytest

from src import coins


def test_get_top_market_tokens_uses_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    sample = [{"symbol": "BTC", "name": "Bitcoin", "slug": "bitcoin"}]

    calls = {"count": 0}

    def fake_fetch(limit: int = 100) -> list[dict[str, str]]:
        calls["count"] += 1
        return sample

    monkeypatch.setattr(coins, "_fetch_top_tokens", fake_fetch)
    coins._tokens_cache = None

    first = coins.get_top_market_tokens()
    second = coins.get_top_market_tokens()

    assert first == sample
    assert second == sample
    assert calls["count"] == 1

    # force refresh should bypass cache
    third = coins.get_top_market_tokens(force_refresh=True)
    assert third == sample
    assert calls["count"] == 2
