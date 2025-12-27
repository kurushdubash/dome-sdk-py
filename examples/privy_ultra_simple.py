#!/usr/bin/env python3
"""
Privy Ultra Simple Example

This is the simplest possible example showing how to:
1. Create a Privy client
2. Create a signer for a wallet
3. Sign an EIP-712 message

This script tests the basic Privy integration without requiring
Polymarket connectivity.

Usage:
    export PRIVY_APP_ID=your_app_id
    export PRIVY_APP_SECRET=your_app_secret
    export PRIVY_AUTHORIZATION_KEY=wallet-auth:your_key
    export PRIVY_WALLET_ID=your_wallet_id
    export PRIVY_WALLET_ADDRESS=0x...
    python privy_ultra_simple.py
"""

import asyncio
import os

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use environment variables directly

from dome_api_sdk import (
    create_privy_client,
    create_privy_signer,
    create_privy_signer_from_env,
)

# Hardcoded test user data (same as TypeScript SDK for testing parity)
TEST_USER = {
    "id": "user-123",
    "privy_wallet_id": "uecc6exvtwc66dv10ffazzn0",
    "wallet_address": "0xC6702E6d5C7D2B1E94e0E407a73bcf13B7A7B5e8",
}


async def test_privy_client():
    """Test basic Privy client initialization."""
    print("=" * 60)
    print("Test 1: Privy Client Initialization")
    print("=" * 60)

    # Create client from config
    privy = create_privy_client({
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    })

    print(f"[OK] Privy client created")
    print(f"     App ID: {privy.app_id[:10]}...")

    await privy.close()
    print("[OK] Privy client closed")


async def test_privy_signer():
    """Test creating a signer for a wallet."""
    print("\n" + "=" * 60)
    print("Test 2: Privy Signer Creation")
    print("=" * 60)

    # Use hardcoded test user data
    wallet_id = TEST_USER["privy_wallet_id"]
    wallet_address = TEST_USER["wallet_address"]

    # Create signer from environment
    signer = create_privy_signer_from_env(wallet_id, wallet_address)

    # Test get_address
    address = await signer.get_address()
    print(f"[OK] Got wallet address: {address}")
    assert address.lower() == wallet_address.lower(), "Address mismatch!"

    # Close the privy client inside the signer
    await signer.privy.close()
    print("[OK] Signer test passed")


async def test_sign_typed_data():
    """Test signing EIP-712 typed data."""
    print("\n" + "=" * 60)
    print("Test 3: EIP-712 Signing")
    print("=" * 60)

    # Use hardcoded test user data
    wallet_id = TEST_USER["privy_wallet_id"]
    wallet_address = TEST_USER["wallet_address"]

    # Create signer
    signer = create_privy_signer_from_env(wallet_id, wallet_address)

    # Test EIP-712 signing with a simple message
    test_payload = {
        "domain": {
            "name": "Test Domain",
            "version": "1",
            "chainId": 137,
        },
        "types": {
            "TestMessage": [
                {"name": "message", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
            ],
        },
        "primaryType": "TestMessage",
        "message": {
            "message": "Hello from Dome SDK!",
            "timestamp": 1234567890,
        },
    }

    print("   Signing test message...")
    signature = await signer.sign_typed_data(test_payload)

    print(f"[OK] Signature: {signature[:20]}...{signature[-10:]}")
    print(f"     Length: {len(signature)} chars")
    assert signature.startswith("0x"), "Signature should start with 0x"
    assert len(signature) == 132, f"Signature should be 132 chars (got {len(signature)})"

    await signer.privy.close()
    print("[OK] Signing test passed")


async def main():
    """Run all tests."""
    print("\nPrivy Ultra Simple Test Suite")
    print("Testing basic Privy integration")
    print()

    # Check required environment variables
    required_vars = ["PRIVY_APP_ID", "PRIVY_APP_SECRET", "PRIVY_AUTHORIZATION_KEY"]
    missing = [v for v in required_vars if not os.environ.get(v)]

    if missing:
        print(f"[ERROR] Missing environment variables: {', '.join(missing)}")
        print("\nSet these variables and try again:")
        for v in missing:
            print(f"  export {v}=your_value")
        return

    try:
        await test_privy_client()
        await test_privy_signer()
        await test_sign_typed_data()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
