"""Background worker that periodically refreshes aggregated strategies."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Dict

from collector.aptos_dex_pipeline import collect_and_store_aptos_dex_data
from collector.pipeline import collect_and_store

REFRESH_INTERVAL_SECONDS = int(os.getenv("AGGREGATOR_UPDATE_INTERVAL", str(2 * 60)))  # Обновляем каждые 2 минуты
INITIAL_DELAY_SECONDS = int(os.getenv("AGGREGATOR_INITIAL_DELAY", "0"))


async def _run_cycle() -> Dict[str, int]:
    return await asyncio.to_thread(collect_and_store)


async def _run_aptos_dex_cycle() -> None:
    """Запустить обновление данных Aptos DEX."""
    await asyncio.to_thread(collect_and_store_aptos_dex_data)


async def main() -> None:
    logging.basicConfig(
        level=os.getenv("AGGREGATOR_WORKER_LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if INITIAL_DELAY_SECONDS > 0:
        logging.info("Initial delay %s seconds before first collection", INITIAL_DELAY_SECONDS)
        await asyncio.sleep(INITIAL_DELAY_SECONDS)

    # Запускаем обновление Aptos DEX параллельно
    async def aptos_dex_updater():
        while True:
            try:
                await _run_aptos_dex_cycle()
                logging.info("Aptos DEX data refresh completed")
            except Exception as exc:  # noqa: BLE001 - log and continue loop
                logging.exception("Aptos DEX refresh failed: %s", exc)
            await asyncio.sleep(max(300, REFRESH_INTERVAL_SECONDS * 2))  # Обновляем реже, чем основные стратегии

    # Запускаем обновление Aptos DEX в фоне
    asyncio.create_task(aptos_dex_updater())

    while True:
        try:
            stats = await _run_cycle()
            logging.info("Aggregator refresh completed", extra={"stats": stats})
        except Exception as exc:  # noqa: BLE001 - log and continue loop
            logging.exception("Aggregator refresh failed: %s", exc)
        await asyncio.sleep(max(30, REFRESH_INTERVAL_SECONDS))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
