"""CLI для запуска DeFi APY агента."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from agent.graph import graph


def _build_preferences(args: argparse.Namespace) -> Dict[str, Any]:
    prefs: Dict[str, Any] = {}

    if args.min_apy is not None:
        prefs["min_apy"] = args.min_apy
    if args.risk_level:
        prefs["risk_level"] = args.risk_level.lower()
    if args.max_lockup is not None:
        prefs["max_lockup_days"] = args.max_lockup
    if args.min_tvl is not None:
        prefs["min_tvl"] = args.min_tvl
    if args.chain:
        prefs["preferred_chains"] = _split_list(args.chain)

    return prefs


def _split_list(values: List[str]) -> List[str]:
    result: List[str] = []
    for value in values:
        chunks = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
        result.extend(chunks)
    return result


def run_agent(
    token: str,
    user_preferences: Dict[str, Any] | None = None,
    *,
    result_limit: int = 200,
    force_refresh: bool = False,
    debug: bool = False,
) -> Dict[str, Any]:
    """Запускает граф и возвращает ответ."""
    state = {
        "input": token,
        "user_prefs": user_preferences or {},
    }

    context = {
        "result_limit": result_limit,
        "force_refresh": force_refresh,
        "keep_debug_data": debug,
    }

    result = graph.invoke(state, config={"configurable": context})
    return result.get("output", result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Поиск лучших DeFi APY стратегий")
    parser.add_argument("token", type=str, help="Тикер токена (например, ETH, USDC)")
    parser.add_argument("--min-apy", type=float, dest="min_apy", help="Минимальный APY (%)")
    parser.add_argument(
        "--risk",
        dest="risk_level",
        help="Допустимый уровень риска: низкий, средний, высокий",
    )
    parser.add_argument(
        "--max-lockup",
        type=int,
        help="Максимальный период блокировки в днях",
    )
    parser.add_argument(
        "--min-tvl",
        type=float,
        help="Минимальный TVL в USD (если число меньше 100000, трактуется как миллионы)",
    )
    parser.add_argument(
        "--chain",
        nargs="*",
        help="Предпочитаемые сети (через пробел или запятую)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=60,
        help="Максимальное количество стратегий для анализа (по умолчанию 60)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Игнорировать кэш и получать свежие данные",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Вернуть отладочные данные",
    )

    args = parser.parse_args()
    prefs = _build_preferences(args)

    output = run_agent(
        args.token,
        user_preferences=prefs,
        result_limit=args.limit,
        force_refresh=args.refresh,
        debug=args.debug,
    )

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
