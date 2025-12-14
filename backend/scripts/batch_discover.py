#!/usr/bin/env python3
"""
Batch discovery script for multiple transactions
Usage: python batch_discover.py <tx_version1> <tx_version2> ... [dex_slug]
"""
import asyncio
import sys
from scripts.discover_dex_fees import discover_fees


async def batch_discover(tx_versions: list[int], dex_slug: str = None):
    """Run discovery for multiple transactions"""
    print(f"🚀 Batch discovery for {len(tx_versions)} transactions")
    if dex_slug:
        print(f"   DEX: {dex_slug}")
    print("=" * 80)
    
    results = []
    for i, tx_version in enumerate(tx_versions, 1):
        print(f"\n[{i}/{len(tx_versions)}] Processing transaction {tx_version}...")
        print("-" * 80)
        
        try:
            await discover_fees(tx_version, dex_slug)
            results.append({"tx_version": tx_version, "status": "success"})
        except Exception as e:
            print(f"❌ Error processing {tx_version}: {e}")
            results.append({"tx_version": tx_version, "status": "error", "error": str(e)})
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary:")
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    
    if failed > 0:
        print("\nFailed transactions:")
        for r in results:
            if r["status"] == "error":
                print(f"   - {r['tx_version']}: {r.get('error', 'Unknown error')}")
    
    return results


async def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_discover.py <tx_version1> <tx_version2> ... [dex_slug]")
        print("\nExample:")
        print("  python batch_discover.py 123456789 123456790 123456791 pancakeswap-amm")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    dex_slug = None
    
    # Last argument might be dex_slug if it's not a number
    if args and not args[-1].isdigit():
        dex_slug = args.pop()
    
    tx_versions = [int(v) for v in args]
    
    await batch_discover(tx_versions, dex_slug)


if __name__ == "__main__":
    asyncio.run(main())

