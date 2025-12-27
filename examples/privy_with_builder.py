#!/usr/bin/env python3
"""
Privy with PolymarketRouter Example

This example shows how to use the PolymarketRouter builder pattern:
1. Initialize the router with Privy config
2. Link a user to Polymarket
3. Use the router's convenience methods

This demonstrates the high-level API without placing actual orders.

Usage:
    export PRIVY_APP_ID=your_app_id
    export PRIVY_APP_SECRET=your_app_secret
    export PRIVY_AUTHORIZATION_KEY=wallet-auth:your_key
    export PRIVY_WALLET_ID=your_wallet_id
    export PRIVY_WALLET_ADDRESS=0x...
    python privy_with_builder.py
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
    PolymarketRouter,
    create_privy_client,
    create_privy_signer,
)


async def test_router_initialization():
    """Test PolymarketRouter initialization with Privy config."""
    print("=" * 60)
    print("Test 1: Router Initialization")
    print("=" * 60)

    # Initialize without Privy
    router_basic = PolymarketRouter()
    print(f"[OK] Basic router created")
    print(f"     Chain ID: {router_basic.chain_id}")
    print(f"     CLOB Endpoint: {router_basic.clob_endpoint}")
    print(f"     API Key Configured: {router_basic.is_api_key_configured()}")
    await router_basic.close()

    # Initialize with Privy config
    privy_config = {
        "app_id": os.environ.get("PRIVY_APP_ID", "test-app-id"),
        "app_secret": os.environ.get("PRIVY_APP_SECRET", "test-secret"),
        "authorization_key": os.environ.get("PRIVY_AUTHORIZATION_KEY", "test-key"),
    }

    router_with_privy = PolymarketRouter({
        "privy": privy_config,
    })
    print(f"[OK] Router with Privy config created")
    await router_with_privy.close()

    # Initialize with API key for order placement
    router_full = PolymarketRouter({
        "api_key": os.environ.get("DOME_API_KEY", "test-dome-key"),
        "privy": privy_config,
    })
    print(f"[OK] Router with API key created")
    print(f"     API Key Configured: {router_full.is_api_key_configured()}")
    await router_full.close()


async def test_user_linking():
    """Test linking a user to Polymarket."""
    print("\n" + "=" * 60)
    print("Test 2: User Linking (Dry Run)")
    print("=" * 60)

    wallet_id = os.environ.get("PRIVY_WALLET_ID")
    wallet_address = os.environ.get("PRIVY_WALLET_ADDRESS")

    if not wallet_id or not wallet_address:
        print("[SKIP] PRIVY_WALLET_ID and PRIVY_WALLET_ADDRESS not set")
        print("       Set these to test actual user linking")
        return

    # Check if we have all Privy credentials
    required = ["PRIVY_APP_ID", "PRIVY_APP_SECRET", "PRIVY_AUTHORIZATION_KEY"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"[SKIP] Missing: {', '.join(missing)}")
        return

    # Create router with Privy
    router = PolymarketRouter({
        "privy": {
            "app_id": os.environ["PRIVY_APP_ID"],
            "app_secret": os.environ["PRIVY_APP_SECRET"],
            "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
        },
    })

    # Create signer
    privy = create_privy_client({
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    })
    signer = create_privy_signer(privy, wallet_id, wallet_address)

    print(f"   Wallet Address: {wallet_address}")
    print(f"   User ID: test-user-123")
    print()

    # Check if user is already linked
    is_linked = router.is_user_linked("test-user-123")
    print(f"   Already linked: {is_linked}")

    # Link user (this will sign an EIP-712 message)
    print("   Linking user to Polymarket...")
    print("   (This signs ONE message to derive API credentials)")
    print()

    try:
        credentials = await router.link_user({
            "user_id": "test-user-123",
            "signer": signer,
            "auto_set_allowances": False,  # Skip allowances for this test
        })

        print(f"[OK] User linked successfully!")
        print(f"     API Key: {credentials.api_key[:10]}...")
        print(f"     API Secret: {credentials.api_secret[:10]}...")

        # Verify user is now linked
        is_linked = router.is_user_linked("test-user-123")
        print(f"     Is Linked: {is_linked}")

        # Get stored credentials
        stored = router.get_credentials("test-user-123")
        print(f"     Stored Credentials: {'Yes' if stored else 'No'}")

    except Exception as e:
        print(f"[ERROR] Linking failed: {e}")

    await router.close()
    await privy.close()


async def test_check_allowances_via_router():
    """Test checking allowances through the router."""
    print("\n" + "=" * 60)
    print("Test 3: Check Allowances via Router")
    print("=" * 60)

    wallet_address = os.environ.get("PRIVY_WALLET_ADDRESS")

    if not wallet_address:
        # Use example address
        wallet_address = "0x0000000000000000000000000000000000000000"
        print(f"   Using example address: {wallet_address}")

    router = PolymarketRouter()

    print(f"   Checking allowances for: {wallet_address}")

    allowances = await router.check_allowances(wallet_address)

    print(f"\n   All Allowances Set: {allowances.all_set}")
    print(f"   USDC CTF Exchange: {allowances.usdc_ctf_exchange}")
    print(f"   CTF CTF Exchange: {allowances.ctf_ctf_exchange}")

    await router.close()
    print("[OK] Allowance check completed")


async def test_manual_credential_management():
    """Test manually setting credentials."""
    print("\n" + "=" * 60)
    print("Test 4: Manual Credential Management")
    print("=" * 60)

    from dome_api_sdk import PolymarketCredentials

    router = PolymarketRouter()

    # Manually set credentials
    test_credentials = PolymarketCredentials(
        api_key="test-api-key",
        api_secret="test-api-secret",
        api_passphrase="test-passphrase",
    )

    router.set_credentials("manual-user", test_credentials)
    print("[OK] Credentials set manually")

    # Retrieve credentials
    retrieved = router.get_credentials("manual-user")
    assert retrieved is not None
    assert retrieved.api_key == "test-api-key"
    print(f"[OK] Retrieved credentials: {retrieved.api_key}")

    # Check user is linked
    is_linked = router.is_user_linked("manual-user")
    assert is_linked
    print(f"[OK] User is linked: {is_linked}")

    # Set Safe address
    router.set_safe_address("manual-user", "0x1234567890123456789012345678901234567890")
    safe_addr = router.get_safe_address("manual-user")
    print(f"[OK] Safe address set: {safe_addr}")

    await router.close()


async def main():
    """Run all tests."""
    print("\nPolymarketRouter Builder Pattern Test Suite")
    print("Testing the high-level router API")
    print()

    try:
        await test_router_initialization()
        await test_user_linking()
        await test_check_allowances_via_router()
        await test_manual_credential_management()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
