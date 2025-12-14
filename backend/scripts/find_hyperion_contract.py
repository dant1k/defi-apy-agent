#!/usr/bin/env python3
"""
Script to find Hyperion contract address and entry functions from Aptos Explorer/Indexer
"""
import asyncio
import sys
from app.providers.aptos_indexer import AptosIndexerProvider


async def find_hyperion_contract():
    """Find Hyperion contract address and entry functions"""
    print("🔍 Searching for Hyperion contract...")
    print("   Documentation: https://docs.hyperion.xyz/")
    
    provider = AptosIndexerProvider()
    
    try:
        # Try to find transactions with "hyperion" in entry function
        query = """
        query FindHyperion {
            user_transactions(
                where: {
                    entry_function_id_str: {_ilike: "%hyperion%"}
                }
                order_by: {version: desc}
                limit: 10
            ) {
                version
                entry_function_id_str
                sender
            }
        }
        """
        
        data = await provider._graphql_query(query)
        
        if data:
            txs = data.get("user_transactions", [])
            if txs:
                print(f"\n✅ Found {len(txs)} Hyperion transactions:")
                print("=" * 80)
                
                # Extract unique entry functions
                entry_functions = set()
                for tx in txs:
                    entry_func = tx.get("entry_function_id_str", "")
                    if entry_func:
                        entry_functions.add(entry_func)
                    print(f"  Version {tx['version']}: {entry_func}")
                    print(f"    Explorer: https://explorer.aptoslabs.com/txn/{tx['version']}")
                
                print(f"\n📋 Unique Entry Functions:")
                for func in sorted(entry_functions):
                    print(f"  - {func}")
                
                # Extract contract address (first part before ::)
                if entry_functions:
                    first_func = list(entry_functions)[0]
                    contract_parts = first_func.split("::")
                    if len(contract_parts) >= 1:
                        contract_address = contract_parts[0]
                        print(f"\n📍 Contract Address: {contract_address}")
                        print(f"   Explorer: https://explorer.aptoslabs.com/account/{contract_address}")
            else:
                print("❌ No Hyperion transactions found")
                print("\n💡 Try:")
                print("   1. Check Aptos Explorer manually")
                print("   2. Look for Hyperion router address in docs")
                print("   3. Use known transaction versions if available")
        else:
            print("❌ No data returned from Indexer")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(find_hyperion_contract())

