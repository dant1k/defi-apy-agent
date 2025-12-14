#!/usr/bin/env python3
"""
Helper script to discover fees from Aptos Explorer transaction URLs
Usage: python discover_from_explorer.py <explorer_url> <dex_slug>
Example: python discover_from_explorer.py https://explorer.aptoslabs.com/txn/123456789 pancakeswap-amm
"""
import asyncio
import sys
import re
from scripts.discover_dex_fees import discover_fees


def extract_tx_version_from_url(url: str) -> int:
    """Extract transaction version from Aptos Explorer URL"""
    # Pattern: https://explorer.aptoslabs.com/txn/123456789
    match = re.search(r'/txn/(\d+)', url)
    if match:
        return int(match.group(1))
    
    # Pattern: just a number
    if url.isdigit():
        return int(url)
    
    raise ValueError(f"Could not extract transaction version from: {url}")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python discover_from_explorer.py <tx_url_or_version> <dex_slug>")
        print("\nExamples:")
        print("  python discover_from_explorer.py https://explorer.aptoslabs.com/txn/123456789 pancakeswap-amm")
        print("  python discover_from_explorer.py 123456789 aux-exchange")
        sys.exit(1)
    
    tx_input = sys.argv[1]
    dex_slug = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        tx_version = extract_tx_version_from_url(tx_input)
        print(f"📋 Transaction version: {tx_version}")
        if dex_slug:
            print(f"   DEX: {dex_slug}")
        
        await discover_fees(tx_version, dex_slug)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

