#!/usr/bin/env python3
"""
Automated script to find and discover swap transactions for DEXes
"""
import asyncio
import sys
from datetime import datetime, timedelta
from app.providers.aptos_indexer import AptosIndexerProvider
from scripts.discover_dex_fees import discover_fees


# Known DEX configurations
DEX_CONFIGS = {
    "pancakeswap-amm": {
        "entry_functions": [
            "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9::router::swap_exact_input",
            "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9::router::swap_exact_output",
        ],
        "router_address": "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9",
    },
    "aux-exchange": {
        "entry_functions": [
            "0xbd35135844473187163ca197ca93b2ab014370587bb0e3b26a3bc4d5190f77c8::router::swap",
        ],
        "router_address": "0xbd35135844473187163ca197ca93b2ab014370587bb0e3b26a3bc4d5190f77c8",
    },
    "hyperion": {
        "entry_functions": [
            "0xc1ccc37cfe6e2daf58194d0deeaa097b65642cc810cb66ba937460a9b8f283ba::hyperion_restricted_router::exact_input_swap_entry",
            "0xc1ccc37cfe6e2daf58194d0deeaa097b65642cc810cb66ba937460a9b8f283ba::hyperion_restricted_router::exact_output_swap_entry",
        ],
        "router_address": "0xc1ccc37cfe6e2daf58194d0deeaa097b65642cc810cb66ba937460a9b8f283ba",
    },
}


async def find_recent_swaps_for_dex(dex_slug: str, limit: int = 5):
    """Find recent swap transactions for a DEX"""
    if dex_slug not in DEX_CONFIGS:
        print(f"❌ Unknown DEX: {dex_slug}")
        print(f"   Available: {list(DEX_CONFIGS.keys())}")
        return []
    
    config = DEX_CONFIGS[dex_slug]
    entry_functions = config["entry_functions"]
    router_address = config["router_address"]
    
    print(f"🔍 Searching for {dex_slug} swap transactions...")
    print(f"   Router: {router_address}")
    print(f"   Entry functions: {len(entry_functions)}")
    
    provider = AptosIndexerProvider()
    
    try:
        # Calculate time range (last 24 hours)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        # Query for transactions with these entry functions
        # Note: GraphQL may need exact match, so we'll try each function
        all_transactions = []
        
        for entry_func in entry_functions:
            # Try without timestamp filter first (schema may differ)
            query = """
            query FindSwaps($entryFunc: String!, $limit: Int!) {
                user_transactions(
                    where: {
                        entry_function_id_str: {_eq: $entryFunc}
                    }
                    order_by: {version: desc}
                    limit: $limit
                ) {
                    version
                    entry_function_id_str
                    sender
                }
            }
            """
            
            variables = {
                "entryFunc": entry_func,
                "limit": limit * 2  # Get more to filter by recency
            }
            
            data = await provider._graphql_query(query, variables)
            if data:
                txs = data.get("user_transactions", [])
                all_transactions.extend(txs)
        
        # Remove duplicates and sort
        seen = set()
        unique_txs = []
        for tx in all_transactions:
            version = tx["version"]
            if version not in seen:
                seen.add(version)
                unique_txs.append(tx)
        
        # Sort by version desc (newer transactions have higher version)
        unique_txs.sort(key=lambda x: x.get("version", 0), reverse=True)
        unique_txs = unique_txs[:limit]
        
        print(f"\n✅ Found {len(unique_txs)} transactions:")
        for i, tx in enumerate(unique_txs, 1):
            print(f"   {i}. Version {tx['version']}")
            print(f"      Function: {tx.get('entry_function_id_str', 'N/A')}")
            print(f"      Sender: {tx.get('sender', 'N/A')}")
            print(f"      Explorer: https://explorer.aptoslabs.com/txn/{tx['version']}")
        
        return unique_txs
        
    except Exception as e:
        print(f"❌ Error finding transactions: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await provider.close()


async def find_and_discover(dex_slug: str, count: int = 3):
    """Find and discover swap transactions for a DEX"""
    print(f"🚀 Finding and discovering transactions for {dex_slug}")
    print("=" * 80)
    
    # Find transactions
    transactions = await find_recent_swaps_for_dex(dex_slug, limit=count * 2)
    
    if not transactions:
        print(f"\n❌ No transactions found for {dex_slug}")
        print("   Try:")
        print("   1. Check if DEX is active")
        print("   2. Manually find transactions in Aptos Explorer")
        print("   3. Use: python scripts/discover_dex_fees.py <tx_version> <dex_slug>")
        return
    
    # Take first N transactions
    transactions = transactions[:count]
    
    print(f"\n📊 Running discovery for {len(transactions)} transactions...")
    print("=" * 80)
    
    # Run discovery for each
    for i, tx in enumerate(transactions, 1):
        tx_version = tx["version"]
        print(f"\n[{i}/{len(transactions)}] Discovering transaction {tx_version}...")
        print("-" * 80)
        
        try:
            await discover_fees(tx_version, dex_slug)
        except Exception as e:
            print(f"❌ Error discovering {tx_version}: {e}")
            continue
    
    print(f"\n✅ Discovery complete!")
    print(f"   Check fixtures in: backend/tests/fixtures/tx_*.json")
    print(f"\n💡 Next steps:")
    print(f"   1. Review fixtures: python scripts/validate_fixture.py tests/fixtures/tx_<version>.json")
    print(f"   2. Generate adapter: python scripts/update_adapter_from_fixture.py tests/fixtures/tx_<version>.json {dex_slug}")
    print(f"   3. Update adapter code based on analysis")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python find_and_discover.py <dex_slug> [count]")
        print("\nAvailable DEXes:")
        for slug in DEX_CONFIGS.keys():
            print(f"   - {slug}")
        print("\nExample:")
        print("  python find_and_discover.py pancakeswap-amm 3")
        sys.exit(1)
    
    dex_slug = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    await find_and_discover(dex_slug, count)


if __name__ == "__main__":
    asyncio.run(main())

