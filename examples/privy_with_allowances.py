#!/usr/bin/env python3
"""
Privy with Allowances Example

This example shows how to:
1. Check wallet token allowances
2. Set allowances using Privy's server-side transactions
3. Verify allowances are set correctly

This is a prerequisite step before trading on Polymarket.

Usage:
    export PRIVY_APP_ID=your_app_id
    export PRIVY_APP_SECRET=your_app_secret
    export PRIVY_AUTHORIZATION_KEY=wallet-auth:your_key
    export PRIVY_WALLET_ID=your_wallet_id
    export PRIVY_WALLET_ADDRESS=0x...
    python privy_with_allowances.py
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
    check_privy_wallet_allowances,
    set_privy_wallet_allowances,
    POLYGON_ADDRESSES,
)


async def test_check_allowances():
    """Test checking wallet allowances."""
    print("=" * 60)
    print("Test 1: Check Wallet Allowances")
    print("=" * 60)

    wallet_address = os.environ.get("PRIVY_WALLET_ADDRESS")

    if not wallet_address:
        print("[SKIP] PRIVY_WALLET_ADDRESS not set")
        return None

    print(f"   Checking allowances for: {wallet_address}")
    print(f"   RPC: https://polygon-rpc.com")

    allowances = await check_privy_wallet_allowances(wallet_address)

    print(f"\n   USDC Allowances:")
    print(f"     CTF Exchange:          {'[OK]' if allowances.usdc_ctf_exchange else '[MISSING]'}")
    print(f"     Neg Risk CTF Exchange: {'[OK]' if allowances.usdc_neg_risk_ctf_exchange else '[MISSING]'}")
    print(f"     Neg Risk Adapter:      {'[OK]' if allowances.usdc_neg_risk_adapter else '[MISSING]'}")

    print(f"\n   CTF (ERC1155) Allowances:")
    print(f"     CTF Exchange:          {'[OK]' if allowances.ctf_ctf_exchange else '[MISSING]'}")
    print(f"     Neg Risk CTF Exchange: {'[OK]' if allowances.ctf_neg_risk_ctf_exchange else '[MISSING]'}")
    print(f"     Neg Risk Adapter:      {'[OK]' if allowances.ctf_neg_risk_adapter else '[MISSING]'}")

    print(f"\n   All Set: {'Yes' if allowances.all_set else 'No'}")

    return allowances


async def test_set_allowances(dry_run: bool = True):
    """Test setting wallet allowances."""
    print("\n" + "=" * 60)
    print("Test 2: Set Wallet Allowances")
    print("=" * 60)

    wallet_id = os.environ.get("PRIVY_WALLET_ID")
    wallet_address = os.environ.get("PRIVY_WALLET_ADDRESS")

    if not wallet_id or not wallet_address:
        print("[SKIP] PRIVY_WALLET_ID and PRIVY_WALLET_ADDRESS not set")
        return

    # First check current allowances
    allowances = await check_privy_wallet_allowances(wallet_address)

    if allowances.all_set:
        print("[OK] All allowances already set - nothing to do")
        return

    if dry_run:
        print("[DRY RUN] Would set the following allowances:")

        if not allowances.usdc_ctf_exchange:
            print(f"   - USDC approve to CTF Exchange ({POLYGON_ADDRESSES['CTF_EXCHANGE']})")
        if not allowances.usdc_neg_risk_ctf_exchange:
            print(f"   - USDC approve to Neg Risk CTF Exchange ({POLYGON_ADDRESSES['NEG_RISK_CTF_EXCHANGE']})")
        if not allowances.usdc_neg_risk_adapter:
            print(f"   - USDC approve to Neg Risk Adapter ({POLYGON_ADDRESSES['NEG_RISK_ADAPTER']})")
        if not allowances.ctf_ctf_exchange:
            print(f"   - CTF setApprovalForAll to CTF Exchange ({POLYGON_ADDRESSES['CTF_EXCHANGE']})")
        if not allowances.ctf_neg_risk_ctf_exchange:
            print(f"   - CTF setApprovalForAll to Neg Risk CTF Exchange ({POLYGON_ADDRESSES['NEG_RISK_CTF_EXCHANGE']})")
        if not allowances.ctf_neg_risk_adapter:
            print(f"   - CTF setApprovalForAll to Neg Risk Adapter ({POLYGON_ADDRESSES['NEG_RISK_ADAPTER']})")

        print("\n   To actually set allowances, run with --set flag")
        return

    # Actually set allowances
    print("   Setting allowances...")

    privy = create_privy_client({
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    })

    def progress_callback(step: str, current: int, total: int):
        print(f"   [{current}/{total}] {step}...")

    tx_hashes = await set_privy_wallet_allowances(
        privy,
        wallet_id,
        wallet_address,
        on_progress=progress_callback,
        sponsor=False,  # Set to True to use Privy gas sponsorship
    )

    print("\n   Transaction Hashes:")
    if tx_hashes.get("usdc"):
        for key, tx in tx_hashes["usdc"].items():
            if tx:
                print(f"     USDC {key}: {tx}")
    if tx_hashes.get("ctf"):
        for key, tx in tx_hashes["ctf"].items():
            if tx:
                print(f"     CTF {key}: {tx}")

    await privy.close()

    # Verify allowances are now set
    print("\n   Verifying allowances...")
    new_allowances = await check_privy_wallet_allowances(wallet_address)

    if new_allowances.all_set:
        print("[OK] All allowances successfully set!")
    else:
        print("[WARN] Some allowances may still be pending (check tx status)")


async def show_contract_addresses():
    """Show the contract addresses used for allowances."""
    print("\n" + "=" * 60)
    print("Polygon Contract Addresses")
    print("=" * 60)

    print(f"   USDC:                     {POLYGON_ADDRESSES['USDC']}")
    print(f"   CTF (ERC1155):            {POLYGON_ADDRESSES['CTF']}")
    print(f"   CTF Exchange:             {POLYGON_ADDRESSES['CTF_EXCHANGE']}")
    print(f"   Neg Risk CTF Exchange:    {POLYGON_ADDRESSES['NEG_RISK_CTF_EXCHANGE']}")
    print(f"   Neg Risk Adapter:         {POLYGON_ADDRESSES['NEG_RISK_ADAPTER']}")


async def main():
    """Run all tests."""
    import sys

    print("\nPrivy Allowances Test Suite")
    print("Testing token allowance checking and setting")
    print()

    # Check for --set flag
    set_allowances = "--set" in sys.argv

    # Check required environment variables for setting allowances
    required_vars = ["PRIVY_APP_ID", "PRIVY_APP_SECRET", "PRIVY_AUTHORIZATION_KEY"]
    missing = [v for v in required_vars if not os.environ.get(v)]

    if missing and set_allowances:
        print(f"[ERROR] Missing environment variables: {', '.join(missing)}")
        print("\nSet these variables to set allowances:")
        for v in missing:
            print(f"  export {v}=your_value")
        return

    wallet_address = os.environ.get("PRIVY_WALLET_ADDRESS")
    if not wallet_address:
        print("[INFO] PRIVY_WALLET_ADDRESS not set - using example address")
        print("       Set PRIVY_WALLET_ADDRESS to check your own wallet\n")
        # Use a known address for demo
        os.environ["PRIVY_WALLET_ADDRESS"] = "0x0000000000000000000000000000000000000000"

    try:
        await show_contract_addresses()
        await test_check_allowances()
        await test_set_allowances(dry_run=not set_allowances)

        print("\n" + "=" * 60)
        print("Test completed!")
        if not set_allowances:
            print("\nTo actually set allowances, run: python privy_with_allowances.py --set")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
