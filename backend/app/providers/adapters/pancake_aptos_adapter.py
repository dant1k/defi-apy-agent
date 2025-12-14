"""PancakeSwap Aptos adapter"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from app.providers.adapters.base_adapter import DexAdapter


class PancakeAptosAdapter(DexAdapter):
    """Adapter for PancakeSwap on Aptos"""
    
    def get_swap_entry_functions(self) -> List[str]:
        """PancakeSwap swap entry functions"""
        # TODO: Update with actual PancakeSwap entry functions
        # Example: "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9::router::swap_exact_input"
        return [
            "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9::router::swap_exact_input",
            "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9::router::swap_exact_output",
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
        
        Strategy:
        1. Look for fee movements (separate from swap amounts)
        2. Fee recipient or pool fee store address
        3. Calculate delta for fee tokens
        """
        try:
            fee_token0 = Decimal("0")
            fee_token1 = Decimal("0")
            
            # Get fee recipient address (if known)
            fee_recipient = self.get_fee_recipient_address(pool_address)
            
            # Group activities by owner and asset type
            # Look for movements to fee recipient or pool fee store
            for activity in activities:
                owner = activity.get("owner_address", "")
                asset_type = activity.get("asset_type", "")
                amount = Decimal(str(activity.get("amount", 0)))
                activity_type = activity.get("type", "")
                
                # Check if this is a fee movement
                # Fee recipient receives fees, or pool stores fees
                if fee_recipient and owner == fee_recipient:
                    # Fee recipient received tokens
                    if asset_type == token0_address:
                        fee_token0 += abs(amount)
                    elif asset_type == token1_address:
                        fee_token1 += abs(amount)
                elif owner == pool_address and "fee" in activity_type.lower():
                    # Pool fee store
                    if asset_type == token0_address:
                        fee_token0 += abs(amount)
                    elif asset_type == token1_address:
                        fee_token1 += abs(amount)
            
            # If no fees found via activities, return None
            if fee_token0 == 0 and fee_token1 == 0:
                return None
            
            return {
                "fee_token0": fee_token0,
                "fee_token1": fee_token1,
            }
        except Exception as e:
            print(f"Error parsing PancakeSwap activities: {e}")
            return None
    
    def get_fee_recipient_address(self, pool_address: str) -> Optional[str]:
        """Get PancakeSwap fee recipient address"""
        # Based on fixture analysis: fee recipient is separate address
        # This is a placeholder - should be updated with real address from fixtures
        # Common pattern: protocol treasury or fee collector
        return "0x5c738e5b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e"

