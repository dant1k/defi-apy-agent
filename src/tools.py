"""Инструменты для работы с DeFi доходностью и подбором стратегий."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

from src.pool_index import POOL_INDEX
from src.utils.tokens import classify_pair, contains_wrapper, parse_tokens

API_URL = "https://yields.llama.fi/pools"
PROTOCOL_URL_TMPL = "https://api.llama.fi/protocol/{slug}"
TOKEN_CACHE_DURATION = timedelta(minutes=5)

RISK_LEVELS = {
    "низкий": 1,
    "средний": 2,
    "высокий": 3,
}


class APIError(Exception):
    """Пользовательское исключение для ошибок API."""


_project_url_cache: Dict[str, Optional[str]] = {}


@dataclass
class TokenPoolCache:
    fetched_at: datetime
    data: List[Dict[str, Any]]


_token_cache: Dict[str, TokenPoolCache] = {}


def _fetch_pools_for_token(token: str, limit: int) -> List[Dict[str, Any]]:
    data = POOL_INDEX.get_pools(token)
    if data:
        if limit:
            return data[:limit]
        return data

    def fetch(params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            payload = response.json()
            return (payload or {}).get("data", [])
        except requests.RequestException:
            return []

    # Try exact symbol lookup first (fast, small payload)
    exact = fetch({"symbol": token})
    if exact:
        return exact[:limit] if limit else exact

    search_params: Dict[str, Any] = {"search": token}
    if limit:
        search_params["limit"] = str(limit * 2)
    results = fetch(search_params)

    filtered: List[Dict[str, Any]] = []
    token_upper = token.upper()
    for pool in results:
        symbol = pool.get("symbol") or ""
        tokens = parse_tokens(symbol)
        if token_upper in tokens:
            filtered.append(pool)
            if limit and len(filtered) >= limit:
                break
    return filtered


def _ensure_token_cache(token: str, limit: int, force_refresh: bool = False) -> List[Dict[str, Any]]:
    key = token.upper()
    now = datetime.utcnow()

    if not force_refresh and key in _token_cache:
        entry = _token_cache[key]
        if now - entry.fetched_at < TOKEN_CACHE_DURATION:
            return entry.data

    data = _fetch_pools_for_token(key, limit)
    _token_cache[key] = TokenPoolCache(fetched_at=now, data=data)
    return data


def _normalize_search_tokens(token: str) -> List[str]:
    raw_parts = re.split(r"[,\s/|]+", token.upper())
    return [part for part in raw_parts if part]


def _token_matches(pool: Dict[str, Any], token: str) -> bool:
    """Определяет, относится ли пул к заданному токену."""
    tokens = _normalize_search_tokens(token)
    if not tokens:
        return False

    symbol = (pool.get("symbol") or "").upper()
    pool_ref = (pool.get("pool") or "").upper()
    project = (pool.get("project") or "").upper()
    underlying_tokens = [item.upper() for item in (pool.get("underlyingTokens") or [])]

    def match_single(single: str) -> bool:
        if single == symbol:
            return True

        for candidate in _split_symbol_parts(symbol):
            if candidate == single:
                return True

        if single in symbol:
            return True

        if single in pool_ref:
            return True

        if single in project:
            return True

        if underlying_tokens and any(single in under for under in underlying_tokens):
            return True

        return False

    if len(tokens) == 1:
        return match_single(tokens[0])

    return all(match_single(part) for part in tokens)


def _get_protocol_url(project: Optional[str]) -> Optional[str]:
    """Возвращает ссылку на протокол из API DeFiLlama."""
    if not project:
        return None

    slug = project.lower()
    if slug in _project_url_cache:
        return _project_url_cache[slug]

    try:
        response = requests.get(PROTOCOL_URL_TMPL.format(slug=slug), timeout=15)
        if response.status_code == 200:
            payload = response.json()
            url = payload.get("url")
            _project_url_cache[slug] = url
            return url
    except requests.RequestException:
        pass

    _project_url_cache[slug] = None
    return None


def _split_symbol_parts(value: str) -> Iterable[str]:
    for part in re.split(r"[-_/()\s]+", value):
        cleaned = part.strip()
        if cleaned:
            yield cleaned


def _parse_lockup(meta: Optional[str]) -> Tuple[int, Optional[str]]:
    """Возвращает период блокировки в днях и исходное описание."""
    if not meta:
        return 0, None

    meta_lower = meta.lower()
    if any(key in meta_lower for key in ("no lock", "no-lock", "liquid", "no unstaking", "нет")):
        return 0, meta

    match = re.search(r"(\d+)\s*(day|days|дней|daystaking|дня|недел[яи]|week|weeks|month|months|месяц|месяцев|year|years|год|лет)", meta_lower)
    if not match:
        return 0, meta

    value = int(match.group(1))
    unit = match.group(2)

    if unit.startswith(("day", "дн")):
        days = value
    elif unit.startswith(("week", "нед")):
        days = value * 7
    elif unit.startswith(("month", "месяц")):
        days = value * 30
    else:
        days = value * 365

    return days, meta


def _evaluate_risk(pool: Dict[str, Any]) -> Tuple[str, float, List[str]]:
    """Вычисляет уровень риска пула."""
    score = 0.0
    reasons: List[str] = []

    stablecoin = bool(pool.get("stablecoin"))
    exposure = (pool.get("exposure") or "").lower()
    il_risk = (pool.get("ilRisk") or "").lower()
    tvl = float(pool.get("tvlUsd") or 0)
    apy = float(pool.get("apy") or 0)
    predictions = pool.get("predictions") or {}
    predicted_prob = predictions.get("predictedProbability")
    predicted_class = (predictions.get("predictedClass") or "").lower()

    if not stablecoin:
        score += 0.4
        reasons.append("Токен не является стейблкоином")

    if exposure and exposure != "single":
        score += 0.6
        reasons.append(f"Тип экспозиции: {exposure}")

    if il_risk == "yes":
        score += 1.0
        reasons.append("Есть риск непостоянных потерь")

    if tvl < 5_000_000:
        score += 1.0
        reasons.append("TVL ниже 5M USD")
    elif tvl < 20_000_000:
        score += 0.5
        reasons.append("TVL ниже 20M USD")

    if apy > 20:
        score += 1.2
        reasons.append("Доходность выше 20%")
    elif apy > 10:
        score += 0.6
        reasons.append("Доходность выше 10%")

    if predicted_prob is not None and predicted_prob < 50:
        score += 0.8
        reasons.append("Модель DeFiLlama оценивает пул как рискованный")

    if predicted_class and "down" in predicted_class:
        score += 0.5
        reasons.append(f"Прогноз модели: {predictions.get('predictedClass')}")

    if tvl > 100_000_000:
        score -= 0.3
        reasons.append("Высокий TVL снижает риск")

    score = max(score, 0.0)

    if score <= 0.9:
        level = "низкий"
    elif score <= 2.0:
        level = "средний"
    else:
        level = "высокий"

    return level, round(score, 2), reasons


def _decorate_pool(pool: Dict[str, Any]) -> Dict[str, Any]:
    """Добавляет производные поля для дальнейшего анализа."""
    lockup_days, lockup_note = _parse_lockup(pool.get("poolMeta"))
    risk_level, risk_score, risk_reasons = _evaluate_risk(pool)
    pool_id = pool.get("pool")
    pool_url = f"https://defillama.com/yields/pool/{pool_id}" if pool_id else None
    protocol_url = _get_protocol_url(pool.get("project"))

    tokens = parse_tokens(pool.get("symbol") or "")
    category = classify_pair(tokens)

    return {
        "platform": pool.get("project"),
        "chain": pool.get("chain"),
        "symbol": pool.get("symbol"),
        "tokens": tokens,
        "category": category,
        "contains_wrapper": contains_wrapper(tokens),
        "apy": float(pool.get("apy") or 0),
        "apy_base": pool.get("apyBase"),
        "apy_reward": pool.get("apyReward"),
        "apy_7d": pool.get("apyPct7D"),
        "apy_30d": pool.get("apyPct30D"),
        "stablecoin": bool(pool.get("stablecoin")),
        "tvl_usd": float(pool.get("tvlUsd") or 0),
        "exposure": pool.get("exposure"),
        "il_risk": pool.get("ilRisk"),
        "pool_id": pool_id,
        "pool_url": pool_url,
        "protocol_url": protocol_url,
        "action_url": protocol_url or pool_url,
        "pool_meta": pool.get("poolMeta"),
        "lockup_days": lockup_days,
        "lockup_note": lockup_note,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_reasons": risk_reasons,
        "predicted_class": (pool.get("predictions") or {}).get("predictedClass"),
        "predicted_probability": (pool.get("predictions") or {}).get("predictedProbability"),
        "updated_at": datetime.utcnow().isoformat(),
    }


def get_opportunities(token: str, limit: int = 50, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Возвращает список лучших возможностей по заданному токену."""
    raw_pools = _ensure_token_cache(token, limit=limit, force_refresh=force_refresh)
    filtered = [_decorate_pool(pool) for pool in raw_pools if _token_matches(pool, token)]

    def sort_key(item: Dict[str, Any]) -> tuple:
        risk_value = RISK_LEVELS.get(item["risk_level"], 3)
        return (risk_value, -float(item["tvl_usd"] or 0), -float(item["apy"] or 0))

    filtered.sort(key=sort_key)

    return filtered[:limit]


def analyze_strategies(apy_options: List[Dict[str, Any]], user_prefs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Подбирает стратегию по предпочтениям пользователя."""
    if not apy_options:
        return None

    min_apy = float(user_prefs.get("min_apy", 0))
    max_lockup_days = int(user_prefs.get("max_lockup_days", 365))
    min_tvl = float(user_prefs.get("min_tvl", 0))
    max_risk = (user_prefs.get("risk_level") or "высокий").lower()
    preferred_chains = {chain.lower() for chain in user_prefs.get("preferred_chains", [])}
    excluded_protocols = {name.lower() for name in user_prefs.get("exclude_protocols", [])}
    include_wrappers = bool(user_prefs.get("include_wrappers", True))

    max_risk_value = RISK_LEVELS.get(max_risk, RISK_LEVELS["высокий"])

    def accept(pool: Dict[str, Any]) -> bool:
        if pool["apy"] < min_apy:
            return False
        if pool["lockup_days"] > max_lockup_days:
            return False
        if pool["tvl_usd"] < min_tvl:
            return False
        if RISK_LEVELS.get(pool["risk_level"], 3) > max_risk_value:
            return False
        if preferred_chains and (pool["chain"] or "").lower() not in preferred_chains:
            return False
        if pool["platform"] and pool["platform"].lower() in excluded_protocols:
            return False
        if not include_wrappers and pool.get("contains_wrapper"):
            return False
        return True

    shortlisted = [pool for pool in apy_options if accept(pool)]

    if not shortlisted:
        return None

    def score(pool: Dict[str, Any]) -> float:
        risk_penalty = (RISK_LEVELS.get(pool["risk_level"], 3) - 1) * 0.35
        tvl_bonus = min(pool["tvl_usd"] / 100_000_000, 1.5) * 0.3
        trend_bonus = 0.0
        apy_30d = pool.get("apy_30d")
        if isinstance(apy_30d, (int, float)) and apy_30d is not None:
            trend_bonus = max(min(apy_30d, 5), -5) * 0.02
        return pool["apy"] - risk_penalty + tvl_bonus + trend_bonus

    shortlisted.sort(key=score, reverse=True)

    ranked: List[Dict[str, Any]] = []
    for item in shortlisted:
        enriched = item.copy()
        enriched["score"] = round(score(item), 2)
        ranked.append(enriched)

    best = ranked[0].copy()
    alternatives = [entry.copy() for entry in ranked[1:4]]

    return {
        "best": best,
        "alternatives": alternatives,
        "matched_count": len(ranked),
        "ranked": ranked,
    }


def get_risk_description(risk_level: str) -> str:
    """Возвращает описание уровня риска."""
    descriptions = {
        "низкий": "Надежные протоколы с большим TVL и аудитом",
        "средний": "Проверенные протоколы с умеренным риском или переменной доходностью",
        "высокий": "Агрессивные стратегии, новые протоколы или низкий TVL",
    }
    return descriptions.get(risk_level, "Неизвестный уровень риска")
