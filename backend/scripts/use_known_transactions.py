#!/usr/bin/env python3
"""
Use known transaction versions for discovery
These can be found manually from Aptos Explorer
"""
import asyncio
import sys
from scripts.discover_dex_fees import discover_fees

# Known transaction examples (to be updated with real ones from Explorer)
KNOWN_TRANSACTIONS = {
    "pancakeswap-amm": [
        # Add real transaction versions here from Explorer
        # Example: 1234567890
    ],
    "aux-exchange": [
        # Add real transaction versions here
    ],
}

async def discover_known_transactions(dex_slug: str):
    """Discover fees for known transactions"""
    if dex_slug not in KNOWN_TRANSACTIONS:
        print(f"❌ Unknown DEX: {dex_slug}")
        return
    
    tx_versions = KNOWN_TRANSACTIONS[dex_slug]
    
    if not tx_versions:
        print(f"⚠️  No known transactions for {dex_slug}")
        print(f"   Please add transaction versions to KNOWN_TRANSACTIONS in this script")
        print(f"   Find them at: https://explorer.aptoslabs.com/")
        return
    
    print(f"🔍 Discovering {len(tx_versions)} known transactions for {dex_slug}")
    
    for i, tx_version in enumerate(tx_versions, 1):
        print(f"\n[{i}/{len(tx_versions)}] Transaction {tx_version}")
        print("-" * 80)
        try:
            await discover_fees(tx_version, dex_slug)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python use_known_transactions.py <dex_slug>")
        sys.exit(1)
    
    dex_slug = sys.argv[1]
    asyncio.run(discover_known_transactions(dex_slug))

