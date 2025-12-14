#!/usr/bin/env python3
"""Verify script for Aptos Indexer connection"""
import asyncio
import sys
from app.providers.aptos_indexer import AptosIndexerProvider
from app.core.config import settings


async def main():
    """Verify Aptos Indexer connection"""
    print(f"🔍 Verifying Aptos Indexer connection...")
    print(f"   URL: {settings.APTOS_INDEXER_URL}")
    
    provider = AptosIndexerProvider()
    
    try:
        # Verify connection
        is_connected = await provider.verify_connection()
        
        if is_connected:
            print("✅ Aptos Indexer connection verified!")
            print("   Schema matches expected format")
            return 0
        else:
            print("❌ Aptos Indexer connection failed!")
            print("   Check URL and network connectivity")
            return 1
    except Exception as e:
        print(f"❌ Error verifying connection: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await provider.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

