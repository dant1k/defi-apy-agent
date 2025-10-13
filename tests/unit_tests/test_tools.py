from src.tools import analyze_strategies


def make_option(
    *,
    platform: str,
    apy: float,
    risk_level: str,
    lockup_days: int,
    tvl_usd: float,
    chain: str = "ethereum",
    contains_wrapper: bool = False,
    category: str = "single",
) -> dict:
    return {
        "platform": platform,
        "apy": apy,
        "risk_level": risk_level,
        "lockup_days": lockup_days,
        "tvl_usd": tvl_usd,
        "chain": chain,
        "category": category,
        "contains_wrapper": contains_wrapper,
        "risk_score": 1.0,
        "risk_reasons": [],
        "stablecoin": False,
        "exposure": "single",
        "il_risk": "no",
    }


def test_analyze_strategies_selects_best() -> None:
    options = [
        make_option(platform="ProtocolA", apy=4.0, risk_level="низкий", lockup_days=0, tvl_usd=50_000_000),
        make_option(platform="ProtocolB", apy=7.5, risk_level="средний", lockup_days=7, tvl_usd=80_000_000),
        make_option(platform="ProtocolC", apy=11.0, risk_level="высокий", lockup_days=0, tvl_usd=5_000_000),
    ]

    prefs = {
        "min_apy": 5.0,
        "risk_level": "средний",
        "max_lockup_days": 30,
        "min_tvl": 10_000_000,
        "preferred_chains": [],
        "exclude_protocols": [],
    }

    result = analyze_strategies(options, prefs)
    assert result is not None
    assert result["best"]["platform"] == "ProtocolB"
    assert result["alternatives"] == []
    assert result["matched_count"] == 1


def test_analyze_strategies_respects_filters() -> None:
    options = [
        make_option(platform="ProtocolA", apy=8.0, risk_level="высокий", lockup_days=0, tvl_usd=200_000_000),
        make_option(platform="ProtocolB", apy=6.0, risk_level="средний", lockup_days=45, tvl_usd=200_000_000),
        make_option(platform="ProtocolC", apy=6.5, risk_level="средний", lockup_days=10, tvl_usd=4_000_000),
    ]

    prefs = {
        "min_apy": 5.0,
        "risk_level": "средний",
        "max_lockup_days": 20,
        "min_tvl": 5_000_000,
        "preferred_chains": [],
        "exclude_protocols": [],
    }

    result = analyze_strategies(options, prefs)
    assert result is None


def test_analyze_strategies_excludes_wrappers_when_disabled() -> None:
    options = [
        make_option(
            platform="ProtocolA",
            apy=8.0,
            risk_level="средний",
            lockup_days=0,
            tvl_usd=10_000_000,
            contains_wrapper=True,
            category="token-wrapper",
        ),
        make_option(
            platform="ProtocolB",
            apy=6.0,
            risk_level="средний",
            lockup_days=0,
            tvl_usd=12_000_000,
        ),
    ]

    prefs = {
        "min_apy": 0.0,
        "risk_level": "высокий",
        "max_lockup_days": 365,
        "min_tvl": 1_000_000,
        "preferred_chains": [],
        "include_wrappers": False,
    }

    result = analyze_strategies(options, prefs)
    assert result is not None
    assert result["best"]["platform"] == "ProtocolB"
    assert result["matched_count"] == 1
