"""Hyperion DEX Aptos adapter"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from collections import defaultdict
from app.providers.adapters.base_adapter import DexAdapter


class HyperionAptosAdapter(DexAdapter):
    """Adapter for Hyperion DEX on Aptos"""
    
    def get_swap_entry_functions(self) -> List[str]:
        """Hyperion swap entry functions"""
        # Found from Aptos Indexer: real Hyperion router entry functions
        return [
            "0xc1ccc37cfe6e2daf58194d0deeaa097b65642cc810cb66ba937460a9b8f283ba::hyperion_restricted_router::exact_input_swap_entry",
            "0xc1ccc37cfe6e2daf58194d0deeaa097b65642cc810cb66ba937460a9b8f283ba::hyperion_restricted_router::exact_output_swap_entry",
            # Also check for other router addresses
            "0x5d7e6a82568f191159b8ec05c4cf741e7610dab826f777288904c4d736e2e2d::hyperion_restricted_router::exact_input_swap_entry",
        ]
    
    def parse_fees_from_activities(
        self,
        activities: List[Dict[str, Any]],
        pool_address: str,
        token0_address: str,
        token1_address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse fungible_asset_activities to extract Hyperion fees
        
        Strategy:
        1. Group activities by asset_type
        2. For each asset_type:
           - Find main swap amount (largest movement)
           - Find small deposit not to user (this is fee)
        3. Fee is the smallest stable deposit to pool/fee vault
        """
        try:
            if not activities:
                return None
            
            # Group activities by asset_type
            asset_groups = defaultdict(list)
            user_addresses = set()
            
            # First pass: identify user addresses
            # Users are those with both withdraw and deposit (swap participants)
            # Pool address is NOT a user
            owners_with_withdraw = set()
            owners_with_deposit = set()
            for activity in activities:
                owner = activity.get("owner_address", "")
                activity_type = activity.get("type", "")
                # Exclude pool address from user detection
                if owner == pool_address or pool_address.lower() in owner.lower():
                    continue
                if activity_type == "withdraw":
                    owners_with_withdraw.add(owner)
                elif activity_type == "deposit":
                    owners_with_deposit.add(owner)
            # Users are those with both withdraw and deposit (swap participants)
            user_addresses = owners_with_withdraw.intersection(owners_with_deposit)
            
            # Also add addresses with large movements as potential users (but not pool)
            for activity in activities:
                owner = activity.get("owner_address", "")
                amount = abs(Decimal(str(activity.get("amount", 0))))
                # Exclude pool address
                if (amount > 1000000 and 
                    owner not in user_addresses and
                    owner != pool_address and 
                    pool_address.lower() not in owner.lower()):
                    user_addresses.add(owner)
            
            # Second pass: group by asset and identify fees
            for activity in activities:
                asset_type = activity.get("asset_type", "")
                owner = activity.get("owner_address", "")
                activity_type = activity.get("type", "")
                amount = Decimal(str(activity.get("amount", 0)))
                
                if not asset_type:
                    continue
                
                asset_groups[asset_type].append({
                    "owner": owner,
                    "type": activity_type,
                    "amount": amount,
                    "is_user": owner in user_addresses,
                    "is_pool": owner == pool_address or pool_address.lower() in owner.lower(),
                })
            
            fee_token0 = Decimal("0")
            fee_token1 = Decimal("0")
            
            # Process each asset type
            for asset_type, group_activities in asset_groups.items():
                # Find main swap amount (largest movement)
                main_amounts = [
                    abs(a["amount"]) for a in group_activities 
                    if abs(a["amount"]) > 1000000
                ]
                
                if not main_amounts:
                    continue
                
                main_swap_amount = max(main_amounts)
                
                # Find small deposits not to user (these are fees)
                # Fee is typically:
                # - deposit type
                # - positive amount
                # - not to user (not in user_addresses)
                # - to pool or separate fee address
                # - amount < 10% of main swap
                fee_deposits = []
                for activity in group_activities:
                    amount_abs = abs(activity["amount"])
                    # Fee is a deposit (positive amount) not to user
                    if (activity["type"] == "deposit" and 
                        activity["amount"] > 0 and 
                        not activity["is_user"] and
                        amount_abs < main_swap_amount * Decimal("0.1") and  # Fee is < 10% of swap
                        amount_abs > 0):  # Non-zero
                        fee_deposits.append(activity["amount"])
                
                if fee_deposits:
                    # Take the smallest stable deposit (most likely to be fee)
                    # Sort by amount and take the smallest non-zero
                    fee_deposits = sorted([d for d in fee_deposits if d > 0])
                    if fee_deposits:
                        fee_amount = fee_deposits[0]  # Smallest deposit
                        
                        # Determine which token this fee is for
                        if asset_type == token0_address:
                            fee_token0 += fee_amount
                        elif asset_type == token1_address:
                            fee_token1 += fee_amount
            
            if fee_token0 == 0 and fee_token1 == 0:
                return None
            
            return {
                "fee_token0": fee_token0,
                "fee_token1": fee_token1,
            }
        except Exception as e:
            print(f"Error parsing Hyperion activities: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_fee_recipient_address(self, pool_address: str) -> Optional[str]:
        """Get Hyperion fee recipient address"""
        # Hyperion fees are stored in pool or fee vault
        # Return None to use activity-based detection
        return None

