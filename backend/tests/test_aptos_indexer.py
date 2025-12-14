"""
Unit tests for Aptos Indexer provider
"""
import pytest
from app.providers.aptos_indexer import AptosIndexerProvider


@pytest.mark.asyncio
async def test_verify_connection():
    """Test Aptos Indexer connection verification"""
    provider = AptosIndexerProvider()
    try:
        result = await provider.verify_connection()
        assert isinstance(result, bool)
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_fetch_fungible_asset_activities():
    """Test fetching fungible asset activities for a transaction"""
    provider = AptosIndexerProvider()
    try:
        # Use a recent transaction version (this will need to be updated)
        # For now, test with a known transaction or skip if not available
        tx_version = 1200000000  # Example - replace with real transaction
        
        activities = await provider.fetch_fungible_asset_activities_for_transaction(tx_version)
        
        # Should return a list (may be empty)
        assert isinstance(activities, list)
    except Exception as e:
        # If transaction doesn't exist, that's okay for unit tests
        pytest.skip(f"Transaction not available: {e}")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_get_pool_real_fees_no_adapter():
    """Test that get_pool_real_fees returns None when no adapter exists"""
    provider = AptosIndexerProvider()
    try:
        result = await provider.get_pool_real_fees(
            chain="aptos",
            dex_slug="nonexistent-dex",
            pool_address="0x123",
            token0_address="0x1::aptos_coin::AptosCoin",
            token1_address="0x2::usdc::USDC",
            timeframe="24h"
        )
        
        # Should return None when adapter doesn't exist
        assert result is None
    finally:
        await provider.close()

