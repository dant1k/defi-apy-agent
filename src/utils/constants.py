"""Константы и настройки по умолчанию для агента."""

from __future__ import annotations

DEFAULT_USER_PREFERENCES = {
    "min_apy": 4.0,
    "risk_level": "средний",
    "max_lockup_days": 365,
    "min_tvl": 5_000_000,  # в USD
    "preferred_chains": [],
    "include_wrappers": True,
}

RISK_DESCRIPTIONS = {
    "низкий": "Протоколы с высокой проверенностью, большим TVL и аудитами.",
    "средний": "Стратегии с умеренным риском, переменной доходностью или сложной архитектурой.",
    "высокий": "Агрессивные стратегии, свежие протоколы или высокая зависимость от токенов вознаграждения.",
}

SUPPORTED_RISK_LEVELS = list(RISK_DESCRIPTIONS.keys())

__all__ = [
    "DEFAULT_USER_PREFERENCES",
    "RISK_DESCRIPTIONS",
    "SUPPORTED_RISK_LEVELS",
]
