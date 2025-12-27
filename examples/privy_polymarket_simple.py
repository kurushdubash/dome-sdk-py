#!/usr/bin/env python3
"""
Privy Polymarket Simple E2E Example

This is a complete end-to-end example showing how to:
1. Initialize the Dome SDK with Privy
2. Create a signer for a user's wallet
3. Check and set token allowances
4. Link user to Polymarket (derive API credentials)
5. Place an order on Polymarket

This example uses REAL API calls and can place REAL orders if configured.

Usage:
    # Copy .env.example to .env and fill in your values:
    cp .env.example .env

    # Or export directly:
    export PRIVY_APP_ID=your_app_id
    export PRIVY_APP_SECRET=your_app_secret
    export PRIVY_AUTHORIZATION_KEY=wallet-auth:your_key
    export PRIVY_WALLET_ID=your_wallet_id
    export PRIVY_WALLET_ADDRESS=0x...

    # Required for placing orders
    export DOME_API_KEY=your_dome_api_key

    # Run the example
    python privy_polymarket_simple.py

    # To actually place an order (use with caution!)
    python privy_polymarket_simple.py --place-order

Note: This example uses the same env vars as dome-sdk-ts for testing parity.
"""

import asyncio
import os
import sys

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use environment variables directly

from dome_api_sdk import (
    PolymarketRouter,
    PolymarketCredentials,
    create_privy_client,
    create_privy_signer,
    check_privy_wallet_allowances,
    set_privy_wallet_allowances,
)


# Example market - US recession in 2025?
# This is a real market on Polymarket. Change this to test with other markets.
EXAMPLE_MARKET = {
    "token_id": "104173557214744537570424345347209544585775842950109756851652855913015295701992",
    "name": "US recession in 2025?",
    "side": "YES",
}


# Hardcoded test user data (same as TypeScript SDK for testing parity)
# In production, this would come from your database
TEST_USER = {
    "id": "user-123",
    "privy_wallet_id": "uecc6exvtwc66dv10ffazzn0",
    "wallet_address": "0xC6702E6d5C7D2B1E94e0E407a73bcf13B7A7B5e8",
}


def check_environment():
    """Check that all required environment variables are set."""
    required = [
        "PRIVY_APP_ID",
        "PRIVY_APP_SECRET",
        "PRIVY_AUTHORIZATION_KEY",
    ]

    missing = [v for v in required if not os.environ.get(v)]

    if missing:
        print("Missing required environment variables:")
        for v in missing:
            print(f"  - {v}")
        print("\nSet these variables and try again.")
        return False

    return True


async def step1_setup():
    """Step 1: Set up Privy client and signer."""
    print("=" * 70)
    print("STEP 1: Setting up Privy client and signer")
    print("=" * 70)

    privy = create_privy_client({
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    })
    print("[OK] Privy client created")

    # Use hardcoded test user data (same as TypeScript SDK)
    wallet_id = TEST_USER["privy_wallet_id"]
    wallet_address = TEST_USER["wallet_address"]

    signer = create_privy_signer(privy, wallet_id, wallet_address)
    print(f"[OK] Signer created for {wallet_address}")

    return privy, signer, wallet_id, wallet_address


async def step2_check_allowances(wallet_address: str):
    """Step 2: Check token allowances."""
    print("\n" + "=" * 70)
    print("STEP 2: Checking token allowances")
    print("=" * 70)

    allowances = await check_privy_wallet_allowances(wallet_address)

    print(f"\nUSDC Allowances:")
    print(f"  CTF Exchange:          {'[OK]' if allowances.usdc_ctf_exchange else '[MISSING]'}")
    print(f"  Neg Risk CTF Exchange: {'[OK]' if allowances.usdc_neg_risk_ctf_exchange else '[MISSING]'}")
    print(f"  Neg Risk Adapter:      {'[OK]' if allowances.usdc_neg_risk_adapter else '[MISSING]'}")

    print(f"\nCTF (ERC1155) Allowances:")
    print(f"  CTF Exchange:          {'[OK]' if allowances.ctf_ctf_exchange else '[MISSING]'}")
    print(f"  Neg Risk CTF Exchange: {'[OK]' if allowances.ctf_neg_risk_ctf_exchange else '[MISSING]'}")
    print(f"  Neg Risk Adapter:      {'[OK]' if allowances.ctf_neg_risk_adapter else '[MISSING]'}")

    print(f"\nAll allowances set: {allowances.all_set}")

    return allowances


async def step3_set_allowances(privy, wallet_id: str, wallet_address: str, allowances):
    """Step 3: Set missing allowances if needed."""
    print("\n" + "=" * 70)
    print("STEP 3: Setting token allowances (if needed)")
    print("=" * 70)

    if allowances.all_set:
        print("[OK] All allowances already set - skipping")
        return

    print("Setting missing allowances...")
    print("(This will send transactions on Polygon)")

    def progress(step: str, current: int, total: int):
        print(f"  [{current}/{total}] {step}")

    tx_hashes = await set_privy_wallet_allowances(
        privy,
        wallet_id,
        wallet_address,
        on_progress=progress,
        sponsor=False,
    )

    print("\nTransaction hashes:")
    for token_type, txs in tx_hashes.items():
        for spender, tx_hash in txs.items():
            if tx_hash:
                print(f"  {token_type} -> {spender}: {tx_hash}")

    print("[OK] Allowances set")


async def step4_link_user(signer, wallet_id: str):
    """Step 4: Link user to Polymarket (derive API credentials)."""
    print("\n" + "=" * 70)
    print("STEP 4: Linking user to Polymarket")
    print("=" * 70)

    router = PolymarketRouter({
        "privy": {
            "app_id": os.environ["PRIVY_APP_ID"],
            "app_secret": os.environ["PRIVY_APP_SECRET"],
            "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
        },
    })

    print("Deriving API credentials from signature...")
    print("(This signs ONE EIP-712 message)")

    credentials = await router.link_user({
        "user_id": TEST_USER["id"],
        "signer": signer,
        "privy_wallet_id": wallet_id,
        "auto_set_allowances": False,  # We already handled this
    })

    print(f"\n[OK] User linked to Polymarket!")
    print(f"     API Key:        {credentials.api_key[:20]}...")
    print(f"     API Secret:     {credentials.api_secret[:10]}...")
    print(f"     API Passphrase: {credentials.api_passphrase[:10]}...")

    await router.close()
    return credentials


async def step5_place_order(signer, credentials: PolymarketCredentials, dry_run: bool = True):
    """Step 5: Place an order on Polymarket."""
    print("\n" + "=" * 70)
    print("STEP 5: Placing order on Polymarket")
    print("=" * 70)

    # Use env var or fallback to test API key (same as TypeScript SDK)
    dome_api_key = os.environ.get("DOME_API_KEY", "4d8e5410-e3bf-4abf-838b-0d3b0312bdd9")

    print(f"\nOrder Details:")
    print(f"  Market: {EXAMPLE_MARKET['name']}")
    print(f"  Token ID: {EXAMPLE_MARKET['token_id'][:30]}...")
    print(f"  Side: BUY")
    print(f"  Size: 100 shares")
    print(f"  Price: $0.01")

    if dry_run:
        print("\n[DRY RUN] Would place order with the above parameters")
        print("          Run with --place-order to actually place the order")
        return

    router = PolymarketRouter({
        "api_key": dome_api_key,
    })

    print("\nPlacing order...")

    try:
        result = await router.place_order({
            "user_id": TEST_USER["id"],
            "market_id": EXAMPLE_MARKET["token_id"],
            "side": "buy",
            "size": 100,  # 100 shares (min $1 order value)
            "price": 0.01,  # $0.01 per share
            "signer": signer,
            "order_type": "GTC",
        }, credentials)

        print(f"\n[OK] Order placed!")
        print(f"     Status: {result.get('status')}")
        print(f"     Order ID: {result.get('orderId')}")

        if result.get("orderHash"):
            print(f"     Order Hash: {result.get('orderHash')}")

    except Exception as e:
        print(f"\n[ERROR] Order placement failed: {e}")
        print("        This could be due to:")
        print("        - Insufficient USDC balance in wallet")
        print("        - Market is closed")
        print("        - Invalid price/size")

    await router.close()


async def main():
    """Run the complete E2E flow."""
    print()
    print("=" * 70)
    print("  PRIVY + POLYMARKET E2E EXAMPLE")
    print("  Using Dome SDK Python")
    print("=" * 70)
    print()

    # Check environment
    if not check_environment():
        return

    # Check for --place-order flag
    place_order = "--place-order" in sys.argv

    if place_order:
        print("WARNING: This will place a REAL order on Polymarket!")
        print("         Make sure you have USDC in your wallet.")
        print()
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    try:
        # Step 1: Setup
        privy, signer, wallet_id, wallet_address = await step1_setup()

        # Step 2: Check allowances
        allowances = await step2_check_allowances(wallet_address)

        # Step 3: Set allowances if needed
        if not allowances.all_set:
            print("\n[INFO] Some allowances are missing.")
            print("       These need to be set before trading.")
            print("       Run 'privy_with_allowances.py --set' to set them.")
            # Uncomment the next line to auto-set allowances:
            # await step3_set_allowances(privy, wallet_id, wallet_address, allowances)

        # Step 4: Link user
        credentials = await step4_link_user(signer, wallet_id)

        # Step 5: Place order
        await step5_place_order(signer, credentials, dry_run=not place_order)

        # Cleanup
        await privy.close()

        print("\n" + "=" * 70)
        print("E2E Example completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] E2E example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
