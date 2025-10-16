"""Граф для DeFi APY агента на LangGraph.

Работает с данными DeFiLlama, фильтрует стратегии по предпочтениям
пользователя и выбирает оптимальную рекомендацию.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from src.tools import APIError, analyze_strategies, get_opportunities, get_risk_description, discover_new_pools
from src.utils.constants import DEFAULT_USER_PREFERENCES, SUPPORTED_RISK_LEVELS


class Context(TypedDict, total=False):
    """Параметры выполнения, передаваемые через runtime context."""

    result_limit: int
    force_refresh: bool
    default_min_apy: float
    default_risk_level: str
    keep_debug_data: bool


class AgentState(TypedDict, total=False):
    """Состояние между узлами графа."""

    input: str
    token: str
    user_prefs: Dict[str, Any]
    opportunities: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    warnings: List[str]
    error: str
    output: Dict[str, Any]


def _normalize_preferences(
    raw_prefs: Optional[Dict[str, Any]], runtime: Optional[Runtime[Context]]
) -> Dict[str, Any]:
    """Объединяет настройки пользователя, значения по умолчанию и контекст."""
    prefs: Dict[str, Any] = dict(DEFAULT_USER_PREFERENCES)

    runtime_context = runtime.context if runtime else None
    if runtime_context:
        if "default_min_apy" in runtime_context:
            prefs["min_apy"] = float(runtime_context["default_min_apy"])
        if "default_risk_level" in runtime_context:
            candidate = str(runtime_context["default_risk_level"]).lower()
            if candidate in SUPPORTED_RISK_LEVELS:
                prefs["risk_level"] = candidate

    if not raw_prefs:
        return prefs

    for key, value in raw_prefs.items():
        if value is None:
            continue

        if key == "min_apy":
            prefs["min_apy"] = float(value)
        elif key == "risk_level":
            candidate = str(value).lower()
            if candidate in SUPPORTED_RISK_LEVELS:
                prefs["risk_level"] = candidate
        elif key == "max_lockup_days":
            prefs["max_lockup_days"] = int(value)
        elif key == "min_tvl":
            numeric = float(value)
            prefs["min_tvl"] = numeric * 1_000_000 if numeric < 100_000 else numeric
        elif key == "preferred_chains":
            prefs["preferred_chains"] = list(value)
        elif key == "include_wrappers":
            prefs["include_wrappers"] = bool(value)

    return prefs


def prepare_state(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Нормализует входные данные."""
    warnings: List[str] = []

    token = state.get("token") or state.get("input")
    if not token:
        return {"error": "Не указан тикер токена для поиска стратегий"}

    normalized_token = str(token).strip().upper()
    if len(normalized_token) > 12:
        warnings.append("Тикер выглядит необычно, проверьте корректность ввода")

    prefs = _normalize_preferences(state.get("user_prefs"), runtime)

    return {
        "token": normalized_token,
        "user_prefs": prefs,
        "warnings": warnings,
    }


def fetch_opportunities(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Получает список доступных стратегий через DeFiLlama."""
    if state.get("error"):
        return {}

    context = (runtime.context or {}) if runtime else {}
    limit = int(context.get("result_limit", 200))
    force_refresh = bool(context.get("force_refresh", False))

    try:
        # Сначала пробуем обычный поиск
        opportunities = get_opportunities(state["token"], limit=limit, force_refresh=force_refresh)
        
        # Если найдено мало результатов, используем агрессивный поиск новых пулов
        if len(opportunities) < limit // 2:
            new_pools = discover_new_pools(state["token"], limit=limit, force_refresh=True)
            # Объединяем результаты, убирая дубликаты
            existing_ids = {pool.get("pool_id") for pool in opportunities}
            for pool in new_pools:
                if pool.get("pool_id") not in existing_ids:
                    opportunities.append(pool)
                    if len(opportunities) >= limit:
                        break
    except APIError as exc:
        return {"error": str(exc)}

    warnings = list(state.get("warnings", []))
    if not opportunities:
        warnings.append("Для указанного токена не найдено активных стратегий")

    return {
        "opportunities": opportunities,
        "warnings": warnings,
    }


def analyze_opportunities(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Фильтрует стратегии по предпочтениям пользователя и оценивает их."""
    if state.get("error"):
        return {}

    opportunities = state.get("opportunities", [])
    analysis = analyze_strategies(opportunities, state["user_prefs"])

    warnings = list(state.get("warnings", []))
    if not analysis or not analysis.get("best"):
        warnings.append("Не удалось подобрать стратегию по заданным ограничениям")
        return {"analysis": None, "warnings": warnings}

    matched_count = int(analysis.get("matched_count") or 0)
    if matched_count <= 0:
        warnings.append("Не удалось подобрать стратегию по заданным ограничениям")
        return {"analysis": None, "warnings": warnings}

    analysis["total_opportunities"] = len(opportunities)
    analysis["matched_opportunities"] = matched_count
    return {"analysis": analysis, "warnings": warnings}


def format_response(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Формирует итоговый ответ агента."""
    if state.get("error"):
        return {
            "output": {
                "status": "error",
                "token": state.get("token"),
                "message": state["error"],
                "warnings": state.get("warnings", []),
            }
        }

    analysis = state.get("analysis")
    if not analysis or not analysis.get("best"):
        return {
            "output": {
                "status": "empty",
                "token": state.get("token"),
                "warnings": state.get("warnings", []),
            }
        }

    def enrich(item: Dict[str, Any]) -> Dict[str, Any]:
        enriched = item.copy()
        enriched["risk_description"] = get_risk_description(enriched["risk_level"])
        return enriched

    best = enrich(analysis["best"])
    alternatives = [enrich(item) for item in analysis.get("alternatives", [])]
    all_strategies = [enrich(item) for item in analysis.get("ranked", [])]
    response: Dict[str, Any] = {
        "status": "ok",
        "token": state.get("token"),
        "best_strategy": best,
        "alternatives": alternatives,
        "statistics": {
            "matched": analysis.get("matched_opportunities", analysis.get("matched_count", 0)),
            "considered": analysis.get("total_opportunities", 0),
        },
        "warnings": state.get("warnings", []),
    }

    if all_strategies:
        response["all_strategies"] = all_strategies

    context = (runtime.context or {}) if runtime else {}
    if context.get("keep_debug_data"):
        response["debug"] = {
            "preferences": state.get("user_prefs"),
            "raw_candidates": state.get("opportunities"),
        }

    return {"output": response}


# Сборка графа
graph_builder = StateGraph(AgentState, context_schema=Context)

graph_builder.add_node("prepare", prepare_state)
graph_builder.add_node("fetch", fetch_opportunities)
graph_builder.add_node("analyze", analyze_opportunities)
graph_builder.add_node("format", format_response)

graph_builder.add_edge("__start__", "prepare")
graph_builder.add_edge("prepare", "fetch")
graph_builder.add_edge("fetch", "analyze")
graph_builder.add_edge("analyze", "format")
graph_builder.add_edge("format", "__end__")

graph = graph_builder.compile(name="DeFi APY Agent")
