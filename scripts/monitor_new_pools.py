#!/usr/bin/env python3
"""
Скрипт для мониторинга новых пулов и уведомлений о лучших возможностях.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set

from src.tools import discover_new_pools, force_refresh_all_pools

# Настройки мониторинга
POPULAR_TOKENS = ["ETH", "USDC", "USDT", "BTC", "WETH", "DAI", "WBTC", "LINK", "UNI", "AAVE"]
MIN_APY_THRESHOLD = 10.0  # Минимальный APY для уведомления
MIN_TVL_THRESHOLD = 5_000_000  # Минимальный TVL для уведомления
CHECK_INTERVAL = 300  # Проверяем каждые 5 минут

# Кэш для отслеживания уже найденных пулов
discovered_pools: Set[str] = set()

def log_new_opportunity(token: str, pool: Dict) -> None:
    """Логирует новую найденную возможность."""
    apy = pool.get("apy", 0)
    tvl = pool.get("tvl_usd", 0)
    protocol = pool.get("platform", "Unknown")
    chain = pool.get("chain", "Unknown")
    
    logging.info(
        f"🚀 НОВАЯ ВОЗМОЖНОСТЬ: {token} | {protocol} ({chain}) | "
        f"APY: {apy:.2f}% | TVL: ${tvl:,.0f} | "
        f"Риск: {pool.get('risk_level', 'Unknown')}"
    )

async def monitor_token(token: str) -> List[Dict]:
    """Мониторит новые пулы для конкретного токена."""
    try:
        # Ищем новые пулы с принудительным обновлением
        new_pools = discover_new_pools(token, limit=50, force_refresh=True)
        
        opportunities = []
        for pool in new_pools:
            pool_id = pool.get("pool_id")
            if not pool_id or pool_id in discovered_pools:
                continue
                
            apy = float(pool.get("apy", 0))
            tvl = float(pool.get("tvl_usd", 0))
            
            # Проверяем критерии для уведомления
            if apy >= MIN_APY_THRESHOLD and tvl >= MIN_TVL_THRESHOLD:
                discovered_pools.add(pool_id)
                log_new_opportunity(token, pool)
                opportunities.append(pool)
        
        return opportunities
    except Exception as e:
        logging.error(f"Ошибка при мониторинге {token}: {e}")
        return []

async def main():
    """Основной цикл мониторинга."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("new_pools_monitor.log"),
            logging.StreamHandler()
        ]
    )
    
    logging.info("🔍 Запуск мониторинга новых пулов...")
    logging.info(f"Мониторим токены: {', '.join(POPULAR_TOKENS)}")
    logging.info(f"Критерии: APY >= {MIN_APY_THRESHOLD}%, TVL >= ${MIN_TVL_THRESHOLD:,}")
    
    while True:
        try:
            start_time = time.time()
            total_opportunities = 0
            
            # Принудительно обновляем все кэши
            force_refresh_all_pools()
            
            # Мониторим каждый токен
            for token in POPULAR_TOKENS:
                opportunities = await monitor_token(token)
                total_opportunities += len(opportunities)
            
            elapsed = time.time() - start_time
            logging.info(f"✅ Цикл завершен за {elapsed:.1f}с. Найдено возможностей: {total_opportunities}")
            
            # Ждем до следующей проверки
            await asyncio.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logging.info("🛑 Мониторинг остановлен пользователем")
            break
        except Exception as e:
            logging.error(f"❌ Ошибка в основном цикле: {e}")
            await asyncio.sleep(60)  # Ждем минуту перед повтором

if __name__ == "__main__":
    asyncio.run(main())

