"""Privy + Polymarket with Fee Escrow Example.

This example demonstrates placing orders with automatic fee escrow using
Privy server wallets. The fee is collected upfront and:
- Distributed to Dome + affiliate on fill
- Refunded to user on cancel

Prerequisites:
1. pip install dome-api-sdk
2. Set environment variables (see .env.example)
3. Fund your Privy wallet with USDC and MATIC on Polygon

Usage:
    python privy_with_escrow.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    # Import here to show what's needed
    from dome_api_sdk import (
        PolymarketRouterWithEscrow,
        create_privy_signer_from_env,
        format_usdc,
    )

    # Configuration from environment
    DOME_API_KEY = os.environ.get("DOME_API_KEY")
    PRIVY_APP_ID = os.environ.get("PRIVY_APP_ID")
    PRIVY_APP_SECRET = os.environ.get("PRIVY_APP_SECRET")
    PRIVY_AUTHORIZATION_KEY = os.environ.get("PRIVY_AUTHORIZATION_KEY")
    PRIVY_WALLET_ID = os.environ.get("PRIVY_WALLET_ID")
    PRIVY_WALLET_ADDRESS = os.environ.get("PRIVY_WALLET_ADDRESS")

    # Validate required env vars
    required = [
        "DOME_API_KEY",
        "PRIVY_APP_ID",
        "PRIVY_APP_SECRET",
        "PRIVY_AUTHORIZATION_KEY",
        "PRIVY_WALLET_ID",
        "PRIVY_WALLET_ADDRESS",
    ]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("See .env.example for required variables.")
        return

    print("=" * 60)
    print("  PRIVY + POLYMARKET WITH FEE ESCROW")
    print("=" * 60)

    # Create router with escrow configuration
    router = PolymarketRouterWithEscrow({
        "api_key": DOME_API_KEY,
        "privy": {
            "app_id": PRIVY_APP_ID,
            "app_secret": PRIVY_APP_SECRET,
            "authorization_key": PRIVY_AUTHORIZATION_KEY,
        },
        "escrow": {
            "fee_bps": 25,  # 0.25% fee
            # "affiliate": "0x...",  # Optional: affiliate address for fee sharing
        },
    })

    try:
        # Create signer from environment
        print("\n[1] Creating Privy signer...")
        signer = create_privy_signer_from_env()
        address = await signer.get_address()
        print(f"    Wallet: {address}")

        # Link user to Polymarket (creates API credentials)
        print("\n[2] Linking user to Polymarket...")
        credentials = await router.link_user({
            "user_id": "escrow-demo-user",
            "signer": signer,
            "privy_wallet_id": PRIVY_WALLET_ID,
            "auto_set_allowances": True,
        })
        print("    API credentials obtained")

        # Calculate fee preview
        size = 10  # shares
        price = 0.50  # $0.50 per share
        fee = router.calculate_order_fee(size, price)
        print(f"\n[3] Order preview:")
        print(f"    Size: {size} shares @ ${price}")
        print(f"    Cost: ${size * price:.2f} USDC")
        print(f"    Fee:  ${format_usdc(fee)} USDC (0.25%)")

        # Example market (replace with real token ID)
        # You can find token IDs from Polymarket or Dome API
        EXAMPLE_MARKET_ID = "21742633143463906290569050155826241533067272736897614950488156847949938836455"

        print("\n[4] Placing order with fee escrow...")
        print("    (Fee will be pulled to escrow contract before order placement)")

        # Place order - escrow happens automatically
        result = await router.place_order({
            "user_id": "escrow-demo-user",
            "market_id": EXAMPLE_MARKET_ID,
            "side": "buy",
            "size": size,
            "price": price,
            "signer": signer,
        })

        print("\n[5] Order placed successfully!")
        print(f"    Order ID: {result.get('orderID', result.get('id', 'N/A'))}")
        if result.get("pullFeeTxHash"):
            print(f"    Fee TX: https://polygonscan.com/tx/{result['pullFeeTxHash']}")

        print("\n" + "=" * 60)
        print("  Order flow with escrow:")
        print("  1. Fee pulled to escrow contract (on-chain)")
        print("  2. Order submitted to Polymarket")
        print("  3. On fill: Fee distributed to Dome + affiliate")
        print("  4. On cancel: Fee refunded to your wallet")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        raise

    finally:
        await router.close()


if __name__ == "__main__":
    asyncio.run(main())
