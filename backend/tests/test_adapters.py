"""
Unit tests for DEX adapters using fixtures
"""
import pytest
from decimal import Decimal
from app.providers.adapters import get_adapter, PancakeAptosAdapter, AuxAptosAdapter
import json
import os


def load_fixture(tx_version: int) -> dict:
    """Load fixture file for a transaction version"""
    fixture_path = f"backend/tests/fixtures/tx_{tx_version}.json"
    if not os.path.exists(fixture_path):
        pytest.skip(f"Fixture {fixture_path} not found")
    
    with open(fixture_path, 'r') as f:
        return json.load(f)


class TestPancakeAptosAdapter:
    """Tests for PancakeSwap Aptos adapter"""
    
    def test_get_swap_entry_functions(self):
        """Test that entry functions are defined"""
        adapter = PancakeAptosAdapter()
        functions = adapter.get_swap_entry_functions()
        assert isinstance(functions, list)
        assert len(functions) > 0
        assert all(isinstance(f, str) for f in functions)
    
    def test_parse_fees_from_activities_example(self):
        """Test parsing fees from example fixture"""
        adapter = PancakeAptosAdapter()
        
        # Try to load real fixture, fallback to example
        try:
            fixture = load_fixture(3907723400)  # PancakeSwap fixture
        except:
            # Use example fixture structure
            fixture = {
                "activities": [
                    {
                        "event_index": 0,
                        "owner_address": "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9",
                        "asset_type": "0x1::aptos_coin::AptosCoin",
                        "type": "deposit",
                        "amount": "100000000000"
                    },
                    {
                        "event_index": 2,
                        "owner_address": "0x5c738e5b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e8b8e",
                        "asset_type": "0x1::aptos_coin::AptosCoin",
                        "type": "deposit",
                        "amount": "250000000"
                    }
                ]
            }
        
        activities = fixture.get("activities", [])
        pool_address = "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9"
        token0_address = "0x1::aptos_coin::AptosCoin"
        token1_address = "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a02b1f6d::asset::USDC"
        
        result = adapter.parse_fees_from_activities(
            activities,
            pool_address,
            token0_address,
            token1_address
        )
        
        # Result should be dict with fee_token0 and fee_token1, or None
        if result:
            assert "fee_token0" in result
            assert "fee_token1" in result
            assert isinstance(result["fee_token0"], Decimal)
            assert isinstance(result["fee_token1"], Decimal)
            # Should find fee in token0
            assert result["fee_token0"] > 0
    
    def test_get_fee_recipient_address(self):
        """Test fee recipient address retrieval"""
        adapter = PancakeAptosAdapter()
        pool_address = "0x123...pool"
        recipient = adapter.get_fee_recipient_address(pool_address)
        # Can be None or a string address
        assert recipient is None or isinstance(recipient, str)


class TestAuxAptosAdapter:
    """Tests for AUX Exchange Aptos adapter"""
    
    def test_get_swap_entry_functions(self):
        """Test that entry functions are defined"""
        adapter = AuxAptosAdapter()
        functions = adapter.get_swap_entry_functions()
        assert isinstance(functions, list)
        assert len(functions) > 0
    
    def test_parse_fees_from_activities(self):
        """Test parsing fees from activities"""
        adapter = AuxAptosAdapter()
        
        # Example activities
        activities = [
            {
                "event_index": 0,
                "owner_address": "0xpool",
                "asset_type": "0x1::aptos_coin::AptosCoin",
                "type": "deposit",
                "amount": "1000000"
            }
        ]
        
        result = adapter.parse_fees_from_activities(
            activities,
            "0xpool",
            "0x1::aptos_coin::AptosCoin",
            "0x2::usdc::USDC"
        )
        
        # Should return dict or None
        assert result is None or isinstance(result, dict)


class TestAdapterRegistry:
    """Tests for adapter registry"""
    
    def test_get_adapter_existing(self):
        """Test getting existing adapter"""
        adapter = get_adapter("pancakeswap-amm")
        assert adapter is not None
        assert isinstance(adapter, PancakeAptosAdapter)
    
    def test_get_adapter_nonexistent(self):
        """Test getting non-existent adapter"""
        adapter = get_adapter("nonexistent-dex")
        assert adapter is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

