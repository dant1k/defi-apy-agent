#!/usr/bin/env python3
"""
Analyze multiple fixtures and generate adapter recommendations
"""
import json
import sys
import os
from pathlib import Path
from collections import defaultdict


def analyze_fixtures(dex_slug: str):
    """Analyze all fixtures for a DEX"""
    # Try both relative and absolute paths
    fixtures_dir = Path("tests/fixtures")
    if not fixtures_dir.exists():
        fixtures_dir = Path("backend/tests/fixtures")
    if not fixtures_dir.exists():
        fixtures_dir = Path("/app/tests/fixtures")
    
    # Find all fixtures for this DEX
    fixtures = []
    for fixture_file in fixtures_dir.glob("tx_*.json"):
        try:
            with open(fixture_file, 'r') as f:
                data = json.load(f)
                # Match by dex_slug or by filename pattern
                if data.get("dex_slug") == dex_slug or dex_slug.replace("-", "_") in fixture_file.stem:
                    fixtures.append((fixture_file, data))
        except Exception as e:
            print(f"⚠️  Error reading {fixture_file}: {e}")
    
    if not fixtures:
        print(f"❌ No fixtures found for {dex_slug}")
        return
    
    print(f"📊 Analyzing {len(fixtures)} fixtures for {dex_slug}")
    print("=" * 80)
    
    # Aggregate analysis
    all_fee_candidates = []
    all_owners = set()
    all_asset_types = set()
    entry_functions = set()
    
    for fixture_file, data in fixtures:
        tx_version = data.get("transaction_version")
        print(f"\n📄 {fixture_file.name} (tx {tx_version})")
        
        activities = data.get("activities", [])
        analysis = data.get("analysis", {})
        fee_candidates = analysis.get("fee_candidates", [])
        
        print(f"   Activities: {len(activities)}")
        print(f"   Fee candidates: {len(fee_candidates)}")
        
        # Collect data
        all_fee_candidates.extend(fee_candidates)
        for activity in activities:
            all_owners.add(activity.get("owner_address", ""))
            all_asset_types.add(activity.get("asset_type", ""))
    
    # Analyze patterns
    print(f"\n🔍 Aggregate Analysis:")
    print("=" * 80)
    
    # Fee recipient analysis
    fee_recipients = defaultdict(int)
    for candidate in all_fee_candidates:
        owner = candidate.get("owner")
        if owner:
            fee_recipients[owner] += 1
    
    if fee_recipients:
        print(f"\n💰 Fee Recipients (by frequency):")
        for recipient, count in sorted(fee_recipients.items(), key=lambda x: x[1], reverse=True):
            print(f"   {recipient}: {count} transactions")
        most_common = max(fee_recipients.items(), key=lambda x: x[1])[0]
        print(f"\n   → Recommended fee recipient: {most_common}")
    else:
        print(f"\n⚠️  No fee recipients found in candidates")
        print(f"   Fees might be:")
        print(f"   - Stored in pool contract")
        print(f"   - Included in swap amounts")
        print(f"   - In raw events (not in activities)")
    
    # Asset types
    print(f"\n🪙 Asset Types ({len(all_asset_types)} unique):")
    for asset_type in sorted(list(all_asset_types))[:10]:  # Show first 10
        print(f"   - {asset_type}")
    if len(all_asset_types) > 10:
        print(f"   ... and {len(all_asset_types) - 10} more")
    
    # Generate recommendations
    print(f"\n💡 Recommendations:")
    print("=" * 80)
    
    if fee_recipients:
        most_common_recipient = max(fee_recipients.items(), key=lambda x: x[1])[0]
        print(f"\n1. Fee Recipient Address:")
        print(f"   def get_fee_recipient_address(self, pool_address: str) -> Optional[str]:")
        print(f"       return \"{most_common_recipient}\"")
    
    print(f"\n2. Entry Functions:")
    print(f"   # TODO: Extract from transaction details")
    print(f"   # Check fixtures for entry_function_id_str in transaction metadata")
    
    print(f"\n3. Fee Detection Logic:")
    if fee_recipients:
        print(f"   # Look for movements to fee recipient: {most_common_recipient}")
        print(f"   # Check asset_type matches token0_address or token1_address")
    else:
        print(f"   # Fees not found in activities - check raw events")
        print(f"   # Or fees might be calculated from swap amounts")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Update adapter with recommendations above")
    print(f"   2. Test with: pytest tests/test_adapters.py::Test{dex_slug.replace('-', '_').title()}Adapter -v")
    print(f"   3. Run integration test with real pool")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_fixtures.py <dex_slug>")
        print("\nExample:")
        print("  python analyze_fixtures.py pancakeswap-amm")
        sys.exit(1)
    
    dex_slug = sys.argv[1]
    analyze_fixtures(dex_slug)


if __name__ == "__main__":
    main()

