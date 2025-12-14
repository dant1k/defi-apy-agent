"""Base adapter interface for DEX-specific event parsing"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from decimal import Decimal


class DexAdapter(ABC):
    """Abstract base class for DEX-specific adapters"""
    
    @abstractmethod
    def get_swap_entry_functions(self) -> List[str]:
        """
        Return list of entry function identifiers for swaps
        
        Returns:
            List of entry function strings (e.g., ["0x1::dex::swap"])
        """
        pass
    
    @abstractmethod
    def parse_fees_from_activities(
        self,
        activities: List[Dict[str, Any]],
        pool_address: str,
        token0_address: str,
        token1_address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse fungible_asset_activities and extract fee information
        
        Args:
            activities: List of fungible asset activities from transaction
            pool_address: Pool contract address
            token0_address: Token0 contract address
            token1_address: Token1 contract address
        
        Returns:
            Dictionary with:
                - fee_token0: Decimal (fee in token0, raw with decimals)
                - fee_token1: Decimal (fee in token1, raw with decimals)
            Or None if no fees found
        """
        pass
    
    def get_fee_recipient_address(self, pool_address: str) -> Optional[str]:
        """
        Get fee recipient address for this DEX (if applicable)
        
        Args:
            pool_address: Pool contract address
        
        Returns:
            Fee recipient address or None
        """
        return None

