#!/usr/bin/env python3
"""
Helper script to generate adapter code from fixture analysis
"""
import json
import sys
import os
from pathlib import Path


def analyze_fixture_for_adapter(fixture_path: str) -> dict:
    """Analyze fixture and generate adapter hints"""
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    activities = data.get("activities", [])
    analysis = data.get("analysis", {})
    fee_candidates = analysis.get("fee_candidates", [])
    
    # Find unique owners
    owners = set()
    asset_types = set()
    for activity in activities:
        owners.add(activity.get("owner_address", ""))
        asset_types.add(activity.get("asset_type", ""))
    
    # Find potential fee recipient
    fee_recipient = None
    if fee_candidates:
        # Use the first fee candidate as potential recipient
        fee_recipient = fee_candidates[0].get("owner")
    
    # Find entry function (would need transaction details)
    # For now, return hints
    
    return {
        "fee_recipient": fee_recipient,
        "owners": list(owners),
        "asset_types": list(asset_types),
        "fee_candidates": fee_candidates,
        "total_activities": len(activities)
    }


def generate_adapter_code(hints: dict, dex_slug: str) -> str:
    """Generate adapter code template"""
    fee_recipient = hints.get("fee_recipient")
    
    code = f'''"""Auto-generated adapter for {dex_slug}"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from app.providers.adapters.base_adapter import DexAdapter


class {dex_slug.replace("-", "_").title()}Adapter(DexAdapter):
    """Adapter for {dex_slug}"""
    
    def get_swap_entry_functions(self) -> List[str]:
        """TODO: Add actual entry functions from transaction details"""
        return [
            # Example: "0x1::dex::swap",
        ]
    
    def parse_fees_from_activities(
        self,
        activities: List[Dict[str, Any]],
        pool_address: str,
        token0_address: str,
        token1_address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse fungible_asset_activities to extract fees
        
        Analysis from fixture:
        - Fee recipient: {fee_recipient or "Not found"}
        - Total activities: {hints.get("total_activities", 0)}
        """
        try:
            fee_token0 = Decimal("0")
            fee_token1 = Decimal("0")
            
            fee_recipient = self.get_fee_recipient_address(pool_address)
            
            # Analyze activities
            for activity in activities:
                owner = activity.get("owner_address", "")
                asset_type = activity.get("asset_type", "")
                amount = Decimal(str(activity.get("amount", 0)))
                
                # TODO: Implement fee detection logic based on fixture analysis
                # Check if this is a fee movement to fee recipient
                if fee_recipient and owner == fee_recipient:
                    if asset_type == token0_address:
                        fee_token0 += abs(amount)
                    elif asset_type == token1_address:
                        fee_token1 += abs(amount)
            
            if fee_token0 == 0 and fee_token1 == 0:
                return None
            
            return {{
                "fee_token0": fee_token0,
                "fee_token1": fee_token1,
            }}
        except Exception as e:
            print(f"Error parsing {dex_slug} activities: {{e}}")
            return None
    
    def get_fee_recipient_address(self, pool_address: str) -> Optional[str]:
        """Get fee recipient address"""
        # TODO: Update with actual fee recipient from fixture analysis
        return {f'"{fee_recipient}"' if fee_recipient else "None"}
'''
    
    return code


def main():
    if len(sys.argv) < 3:
        print("Usage: python update_adapter_from_fixture.py <fixture_file> <dex_slug>")
        print("\nExample:")
        print("  python update_adapter_from_fixture.py tests/fixtures/tx_123456789.json pancakeswap-amm")
        sys.exit(1)
    
    fixture_path = sys.argv[1]
    dex_slug = sys.argv[2]
    
    if not os.path.exists(fixture_path):
        print(f"❌ Fixture not found: {fixture_path}")
        sys.exit(1)
    
    print(f"🔍 Analyzing fixture: {fixture_path}")
    hints = analyze_fixture_for_adapter(fixture_path)
    
    print(f"\n📊 Analysis:")
    print(f"   Fee recipient: {hints.get('fee_recipient', 'Not found')}")
    print(f"   Unique owners: {len(hints.get('owners', []))}")
    print(f"   Asset types: {len(hints.get('asset_types', []))}")
    print(f"   Fee candidates: {len(hints.get('fee_candidates', []))}")
    
    code = generate_adapter_code(hints, dex_slug)
    
    output_file = f"backend/app/providers/adapters/{dex_slug.replace('-', '_')}_adapter_generated.py"
    print(f"\n💾 Generated adapter code:")
    print(f"   {output_file}")
    
    with open(output_file, 'w') as f:
        f.write(code)
    
    print(f"\n✅ Adapter code generated!")
    print(f"   Review and update: {output_file}")
    print(f"   Then rename to: {dex_slug.replace('-', '_')}_aptos_adapter.py")


if __name__ == "__main__":
    main()

