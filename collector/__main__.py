"""CLI entrypoint for data collector."""

from __future__ import annotations

import argparse
import logging
import sys

from .pipeline import collect_and_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect DeFi strategy data and store in Redis cache.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    stats = collect_and_store()
    logging.info("Collection finished: %s", stats)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
