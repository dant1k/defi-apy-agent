#!/usr/bin/env python3
"""Тест агента для проверки работы поиска пулов."""

import sys
sys.path.append('.')

from src.tools import get_opportunities, force_refresh_all_pools
from src.app import run_agent

def test_agent():
    print("🔄 Принудительно обновляем кэш...")
    force_refresh_all_pools()

    print("🔍 Ищем возможности для ETH...")
    opportunities = get_opportunities('ETH', limit=5, force_refresh=True)

    print(f"📊 Найдено возможностей: {len(opportunities)}")
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"{i}. {opp.get('platform', 'Unknown')} ({opp.get('chain', 'Unknown')})")
        print(f"   APY: {opp.get('apy', 0):.2f}% | TVL: ${opp.get('tvl_usd', 0):,.0f}")
        print(f"   Риск: {opp.get('risk_level', 'Unknown')}")
        print()

    print("🤖 Тестируем полного агента...")
    result = run_agent('ETH', {'min_apy': 1}, result_limit=10, force_refresh=True)
    
    print(f"Статус: {result.get('status')}")
    if result.get('best_strategy'):
        bs = result['best_strategy']
        print(f"Лучшая стратегия: {bs.get('platform')} - APY: {bs.get('apy')}% - TVL: ${bs.get('tvl_usd'):,.0f}")
    
    stats = result.get('statistics', {})
    print(f"Рассмотрено: {stats.get('considered', 0)}")
    print(f"Подходящих: {stats.get('matched', 0)}")

if __name__ == "__main__":
    test_agent()

