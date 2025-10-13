import importlib

import pytest

import agent.graph as agent_graph


def test_agent_recommends_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    mocked_pools = [
        {
            "platform": "ProtocolA",
            "chain": "Ethereum",
            "symbol": "ETH",
            "apy": 5.5,
            "apy_base": 5.0,
            "apy_reward": 0.5,
            "apy_7d": 0.1,
            "apy_30d": 0.2,
            "stablecoin": False,
            "tvl_usd": 120_000_000,
            "exposure": "single",
            "il_risk": "no",
            "pool_id": "pool-a",
            "pool_url": "https://defillama.com/yields/pool/pool-a",
            "protocol_url": "https://protocol-a.example",
            "action_url": "https://protocol-a.example",
            "pool_meta": "liquid staking",
            "lockup_days": 0,
            "lockup_note": "liquid staking",
            "risk_level": "низкий",
            "risk_score": 0.8,
            "risk_reasons": [],
            "predicted_class": "Stable/Up",
            "predicted_probability": 85,
            "updated_at": "2024-01-01T00:00:00",
        },
        {
            "platform": "ProtocolB",
            "chain": "Ethereum",
            "symbol": "ETH",
            "apy": 4.2,
            "apy_base": 8.0,
            "apy_reward": 1.5,
            "apy_7d": 0.3,
            "apy_30d": 0.4,
            "stablecoin": False,
            "tvl_usd": 40_000_000,
            "exposure": "lp",
            "il_risk": "yes",
            "pool_id": "pool-b",
            "pool_url": "https://defillama.com/yields/pool/pool-b",
            "protocol_url": "https://protocol-b.example",
            "action_url": "https://protocol-b.example",
            "pool_meta": "7 days lockup",
            "lockup_days": 7,
            "lockup_note": "7 days lockup",
            "risk_level": "высокий",
            "risk_score": 3.2,
            "risk_reasons": ["High yield"],
            "predicted_class": "DownOnly",
            "predicted_probability": 45,
            "updated_at": "2024-01-01T00:00:00",
        },
    ]

    def fake_get_opportunities(token: str, limit: int = 200, force_refresh: bool = False):
        assert token == "ETH"
        return mocked_pools

    agent_graph_module = importlib.import_module("agent.graph")
    monkeypatch.setattr(agent_graph_module, "get_opportunities", fake_get_opportunities)

    result = agent_graph_module.graph.invoke({"input": "ETH"})
    output = result["output"]

    assert output["status"] == "ok"
    assert output["best_strategy"]["platform"] == "ProtocolA"
    assert output["statistics"]["matched"] == 1
    assert output["best_strategy"]["action_url"] == "https://protocol-a.example"
    assert len(output["alternatives"]) == 0
    assert not output["warnings"]
