"""
Unit tests for Hyperion adapter
"""
import pytest
from decimal import Decimal
from app.providers.adapters.hyperion_aptos_adapter import HyperionAptosAdapter
import json
import os


def load_fixture(tx_version: int) -> dict:
    """Load fixture file for a transaction version"""
    fixture_path = f"tests/fixtures/tx_hyperion_{tx_version % 10}.json"
    if not os.path.exists(fixture_path):
        # Try alternative path
        fixture_path = f"backend/tests/fixtures/tx_hyperion_{tx_version % 10}.json"
    if not os.path.exists(fixture_path):
        pytest.skip(f"Fixture {fixture_path} not found")
    
    with open(fixture_path, 'r') as f:
        return json.load(f)


class TestHyperionAptosAdapter:
    """Tests for Hyperion Aptos adapter"""
    
    def test_get_swap_entry_functions(self):
        """Test that entry functions are defined"""
        adapter = HyperionAptosAdapter()
        functions = adapter.get_swap_entry_functions()
        assert isinstance(functions, list)
        assert len(functions) > 0
        assert all(isinstance(f, str) for f in functions)
    
    def test_parse_fees_from_activities(self):
        """Test parsing fees from Hyperion fixture"""
        adapter = HyperionAptosAdapter()
        
        # Load fixture
        try:
            fixture = load_fixture(3907723500)
        except:
            # Use example structure
            fixture = {
                "activities": [
                    {
                        "event_index": 0,
                        "owner_address": "0xuser123...",
                        "asset_type": "0x1::aptos_coin::AptosCoin",
                        "type": "withdraw",
                        "amount": "-100000000000"
                    },
                    {
                        "event_index": 1,
                        "owner_address": "0xuser123...",
                        "asset_type": "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a02b1f6d::asset::USDC",
                        "type": "deposit",
                        "amount": "95000000000"
                    },
                    {
                        "event_index": 2,
                        "owner_address": "0xhyperion_pool...",
                        "asset_type": "0x1::aptos_coin::AptosCoin",
                        "type": "deposit",
                        "amount": "250000000"
                    }
                ]
            }
        
        activities = fixture.get("activities", [])
        pool_address = "0xhyperion_pool..."
        token0_address = "0x1::aptos_coin::AptosCoin"
        token1_address = "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a02b1f6d::asset::USDC"
        
        result = adapter.parse_fees_from_activities(
            activities,
            pool_address,
            token0_address,
            token1_address
        )
        
        # Should find fee in token0 (AptosCoin)
        assert result is not None
        assert "fee_token0" in result
        assert "fee_token1" in result
        assert isinstance(result["fee_token0"], Decimal)
        assert isinstance(result["fee_token1"], Decimal)
        # Fee should be found in token0
        assert result["fee_token0"] > 0
    
    def test_parse_fees_no_fee_found(self):
        """Test parsing when no fee is found"""
        adapter = HyperionAptosAdapter()
        
        # Activities without fee
        activities = [
            {
                "event_index": 0,
                "owner_address": "0xuser123...",
                "asset_type": "0x1::aptos_coin::AptosCoin",
                "type": "withdraw",
                "amount": "-100000000000"
            },
            {
                "event_index": 1,
                "owner_address": "0xuser123...",
                "asset_type": "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a02b1f6d::asset::USDC",
                "type": "deposit",
                "amount": "95000000000"
            }
        ]
        
        result = adapter.parse_fees_from_activities(
            activities,
            "0xpool",
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a02b1f6d::asset::USDC"
        )
        
        # Should return None when no fee found
        assert result is None
    
    def test_get_fee_recipient_address(self):
        """Test fee recipient address"""
        adapter = HyperionAptosAdapter()
        result = adapter.get_fee_recipient_address("0xpool")
        # Hyperion uses activity-based detection, so returns None
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

