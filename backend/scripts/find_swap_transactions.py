#!/usr/bin/env python3
"""
Helper script to find swap transactions for a DEX
Uses Aptos Indexer to search for recent swap transactions
"""
import asyncio
import sys
from datetime import datetime, timedelta
from app.providers.aptos_indexer import AptosIndexerProvider


async def find_swap_transactions(
    dex_slug: str,
    entry_functions: list[str] = None,
    pool_address: str = None,
    hours: int = 24,
    limit: int = 10
):
    """
    Find recent swap transactions for a DEX
    
    Args:
        dex_slug: DEX identifier
        entry_functions: List of entry function identifiers (optional)
        pool_address: Pool address to filter by (optional)
        hours: Look back hours (default 24)
        limit: Maximum transactions to return
    """
    print(f"🔍 Searching for swap transactions...")
    print(f"   DEX: {dex_slug}")
    if entry_functions:
        print(f"   Entry functions: {entry_functions}")
    if pool_address:
        print(f"   Pool address: {pool_address}")
    
    provider = AptosIndexerProvider()
    
    try:
        # If entry functions not provided, try common patterns
        if not entry_functions:
            print("   ⚠️  No entry functions provided. Using common patterns...")
            entry_functions = [
                f"*::router::swap*",
                f"*::swap*",
            ]
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        # Query user_transactions
        # Note: This is a simplified query - actual implementation may need
        # to query by specific entry functions or use different approach
        query = """
        query FindSwapTransactions($startTime: timestamp!, $endTime: timestamp!, $limit: Int!) {
            user_transactions(
                where: {
                    transaction_timestamp: {_gte: $startTime, _lte: $endTime}
                }
                order_by: {transaction_timestamp: desc}
                limit: $limit
            ) {
                version
                transaction_timestamp
                entry_function_id_str
                sender
            }
        }
        """
        
        variables = {
            "startTime": start_timestamp,
            "endTime": end_timestamp,
            "limit": limit * 10  # Get more to filter
        }
        
        data = await provider._graphql_query(query, variables)
        
        if not data:
            print("❌ No transactions found")
            return []
        
        transactions = data.get("user_transactions", [])
        
        # Filter by entry function if provided
        if entry_functions:
            filtered = []
            for tx in transactions:
                entry_func = tx.get("entry_function_id_str", "")
                # Simple pattern matching
                for pattern in entry_functions:
                    if pattern.replace("*", "") in entry_func.lower():
                        filtered.append(tx)
                        break
            transactions = filtered[:limit]
        else:
            transactions = transactions[:limit]
        
        print(f"\n📊 Found {len(transactions)} transactions:")
        print("=" * 80)
        
        for i, tx in enumerate(transactions, 1):
            print(f"\n{i}. Transaction {tx['version']}")
            print(f"   Timestamp: {datetime.fromtimestamp(tx['transaction_timestamp'])}")
            print(f"   Entry Function: {tx.get('entry_function_id_str', 'N/A')}")
            print(f"   Sender: {tx.get('sender', 'N/A')}")
            print(f"   🔗 https://explorer.aptoslabs.com/txn/{tx['version']}")
        
        print(f"\n💡 To analyze a transaction:")
        print(f"   python scripts/discover_dex_fees.py <tx_version> {dex_slug}")
        
        return transactions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await provider.close()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python find_swap_transactions.py <dex_slug> [entry_function] [pool_address] [hours]")
        print("\nExample:")
        print("  python find_swap_transactions.py pancakeswap-amm")
        print("  python find_swap_transactions.py aux-exchange 0x1::router::swap")
        sys.exit(1)
    
    dex_slug = sys.argv[1]
    entry_functions = [sys.argv[2]] if len(sys.argv) > 2 else None
    pool_address = sys.argv[3] if len(sys.argv) > 3 else None
    hours = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    
    await find_swap_transactions(dex_slug, entry_functions, pool_address, hours)


if __name__ == "__main__":
    asyncio.run(main())

