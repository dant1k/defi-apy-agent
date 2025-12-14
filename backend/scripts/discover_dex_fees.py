#!/usr/bin/env python3
"""
Discovery script for DEX fees analysis
Usage: python discover_dex_fees.py <transaction_version> [dex_slug]
"""
import asyncio
import sys
import json
from datetime import datetime
from app.providers.aptos_indexer import AptosIndexerProvider


async def discover_fees(transaction_version: int, dex_slug: str = None):
    """
    Discover fee structure for a swap transaction
    
    Args:
        transaction_version: Transaction version to analyze
        dex_slug: Optional DEX slug for context
    """
    print(f"🔍 Analyzing transaction {transaction_version}...")
    if dex_slug:
        print(f"   DEX: {dex_slug}")
    
    provider = AptosIndexerProvider()
    
    try:
        # Fetch fungible asset activities (recommended method)
        activities = await provider.fetch_fungible_asset_activities_for_transaction(transaction_version)
        
        print(f"\n📊 Fungible Asset Activities ({len(activities)} found):")
        print("=" * 80)
        
        # Group by owner and asset type for analysis
        owner_assets = {}
        for activity in activities:
            owner = activity.get('owner_address', '')
            asset_type = activity.get('asset_type', '')
            amount = activity.get('amount', 0)
            activity_type = activity.get('type', '')
            
            key = f"{owner}:{asset_type}"
            if key not in owner_assets:
                owner_assets[key] = {
                    "owner": owner,
                    "asset_type": asset_type,
                    "total_amount": 0,
                    "activities": []
                }
            owner_assets[key]["total_amount"] += int(amount) if amount else 0
            owner_assets[key]["activities"].append({
                "event_index": activity.get('event_index'),
                "type": activity_type,
                "amount": amount
            })
        
        # Print detailed activities
        for i, activity in enumerate(activities):
            print(f"\nActivity {i + 1}:")
            print(f"  Event Index: {activity.get('event_index')}")
            print(f"  Owner Address: {activity.get('owner_address')}")
            print(f"  Asset Type: {activity.get('asset_type')}")
            print(f"  Type: {activity.get('type')}")
            print(f"  Amount: {activity.get('amount')}")
        
        # Analysis summary
        print(f"\n📈 Summary by Owner/Asset:")
        print("=" * 80)
        for key, data in sorted(owner_assets.items(), key=lambda x: abs(x[1]["total_amount"]), reverse=True):
            print(f"\n{data['owner']} | {data['asset_type']}")
            print(f"  Total Amount: {data['total_amount']}")
            print(f"  Activities: {len(data['activities'])}")
        
        # Try to identify fee patterns
        print(f"\n🔎 Fee Analysis:")
        print("=" * 80)
        print("Looking for potential fee movements...")
        
        fee_candidates = []
        for key, data in owner_assets.items():
            owner = data['owner']
            total = data['total_amount']
            # Small positive amounts to fee recipients might be fees
            if total > 0 and total < 1000000000:  # Less than 1 token (assuming 8 decimals)
                fee_candidates.append({
                    "owner": owner,
                    "asset_type": data['asset_type'],
                    "amount": total,
                    "reason": "Small positive amount to non-pool address"
                })
        
        if fee_candidates:
            print("\nPotential fee movements:")
            for candidate in fee_candidates:
                print(f"  - {candidate['owner']} received {candidate['amount']} of {candidate['asset_type']}")
        else:
            print("  No obvious fee movements found. Check if fees are:")
            print("    - Stored in pool contract")
            print("    - Included in swap amounts")
            print("    - In raw events (not in activities)")
        
        # Save to fixture file
        fixture_data = {
            "transaction_version": transaction_version,
            "dex_slug": dex_slug,
            "timestamp": datetime.utcnow().isoformat(),
            "activities": activities,
            "analysis": {
                "total_activities": len(activities),
                "owner_assets_summary": {
                    k: {
                        "owner": v["owner"],
                        "asset_type": v["asset_type"],
                        "total_amount": v["total_amount"],
                        "activity_count": len(v["activities"])
                    }
                    for k, v in owner_assets.items()
                },
                "fee_candidates": fee_candidates
            }
        }
        
        fixture_file = f"backend/tests/fixtures/tx_{transaction_version}.json"
        import os
        os.makedirs(os.path.dirname(fixture_file), exist_ok=True)
        
        with open(fixture_file, 'w') as f:
            json.dump(fixture_data, f, indent=2)
        
        print(f"\n✅ Saved to: {fixture_file}")
        print("\n💡 Next Steps:")
        print("   1. Review fee candidates above")
        print("   2. Check entry function in transaction details")
        print("   3. Update DexAdapter:")
        print("      - get_swap_entry_functions()")
        print("      - get_fee_recipient_address()")
        print("      - parse_fees_from_activities()")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await provider.close()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python discover_dex_fees.py <transaction_version> [dex_slug]")
        print("\nExample:")
        print("  python discover_dex_fees.py 123456789 pancakeswap-amm")
        sys.exit(1)
    
    tx_version = int(sys.argv[1])
    dex_slug = sys.argv[2] if len(sys.argv) > 2 else None
    
    await discover_fees(tx_version, dex_slug)


if __name__ == "__main__":
    asyncio.run(main())

