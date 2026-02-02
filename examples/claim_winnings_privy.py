"""Privy Server Wallet -- Claim Winnings with Performance Fee.

This example shows how to claim winnings from a resolved Polymarket
market using the Dome SDK with a Privy server-managed wallet.

Flow:
[1] Validate config (PRIVY_*, DOME_API_KEY, CONDITION_ID)
[2] Setup Privy signer + escrow client
[3] Calculate performance fees (local)
[4] Sign performance fee authorization (via Privy TypedDataSigner)
[5] Submit claim_winnings(wallet_type='privy', privy_wallet_id=...)
[6] Display results

No signed redeemPositions tx needed -- Dome builds and submits via Privy API.

Prerequisites:
1. pip install dome-api-sdk
2. Set environment variables:
   - PRIVY_APP_ID, PRIVY_APP_SECRET, PRIVY_AUTHORIZATION_KEY
   - PRIVY_WALLET_ID, PRIVY_WALLET_ADDRESS
   - DOME_API_KEY
   - CONDITION_ID: Condition ID of a resolved market (bytes32 hex)

Optional:
- OUTCOME_INDEX: Winning outcome index, 0 or 1 (defaults to 1)

Usage:
    PRIVY_APP_ID=... PRIVY_APP_SECRET=... PRIVY_AUTHORIZATION_KEY=... \\
    PRIVY_WALLET_ID=... PRIVY_WALLET_ADDRESS=0x... \\
    DOME_API_KEY=... CONDITION_ID=0x... \\
    python examples/claim_winnings_privy.py
"""

import asyncio
import os
import sys
import secrets

from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    from dome_api_sdk import (
        PolymarketRouterWithEscrow,
        DomeFeeEscrowClient,
        create_privy_signer_from_env,
        format_usdc,
        ESCROW_CONTRACT_POLYGON,
    )

    print("=== Privy Server Wallet -- Claim Winnings with Performance Fee ===\n")

    # -- [1] Validate configuration ----------------------------------------
    print("[1] Validating configuration...")

    privy_app_id = os.environ.get("PRIVY_APP_ID", "")
    privy_app_secret = os.environ.get("PRIVY_APP_SECRET", "")
    privy_auth_key = os.environ.get("PRIVY_AUTHORIZATION_KEY", "")
    privy_wallet_id = os.environ.get("PRIVY_WALLET_ID", "")
    privy_wallet_address = os.environ.get("PRIVY_WALLET_ADDRESS", "")
    dome_api_key = os.environ.get("DOME_API_KEY", "")
    condition_id = os.environ.get("CONDITION_ID", "")
    outcome_index = int(os.environ.get("OUTCOME_INDEX", "1"))
    chain_id = 137

    required = {
        "PRIVY_APP_ID": privy_app_id,
        "PRIVY_APP_SECRET": privy_app_secret,
        "PRIVY_AUTHORIZATION_KEY": privy_auth_key,
        "PRIVY_WALLET_ID": privy_wallet_id,
        "PRIVY_WALLET_ADDRESS": privy_wallet_address,
        "DOME_API_KEY": dome_api_key,
        "CONDITION_ID": condition_id,
    }

    missing = [name for name, val in required.items() if not val]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    print(f"  Wallet:         {privy_wallet_address}")
    print(f"  Condition ID:   {condition_id}")
    print(f"  Outcome Index:  {outcome_index}")

    # -- [2] Setup Privy signer + escrow client ----------------------------
    print("\n[2] Setting up Privy signer and escrow client...")

    signer = create_privy_signer_from_env()

    escrow_client = DomeFeeEscrowClient(
        escrow_address=ESCROW_CONTRACT_POLYGON,
        chain_id=chain_id,
    )

    print(f"  Escrow contract: {ESCROW_CONTRACT_POLYGON}")
    print("  Privy signer initialized")

    # -- [3] Calculate performance fees ------------------------------------
    print("\n[3] Calculating performance fees (local)...")

    expected_winnings = 100_000_000  # $100 USDC
    dome_fee_bps = 250  # 2.5%
    affiliate_fee_bps = 50  # 0.5%

    fees = DomeFeeEscrowClient.calculate_performance_fees(
        expected_winnings=expected_winnings,
        dome_fee_bps=dome_fee_bps,
        affiliate_fee_bps=affiliate_fee_bps,
    )

    print(f"  Expected winnings: ${format_usdc(expected_winnings)}")
    print(f"  Dome fee:          ${format_usdc(fees.dome_fee)} ({dome_fee_bps / 100}%)")
    print(
        f"  Affiliate fee:     ${format_usdc(fees.affiliate_fee)} "
        f"({affiliate_fee_bps / 100}%)"
    )
    print(f"  Total fee:         ${format_usdc(fees.total_fee)}")

    # -- [4] Sign performance fee authorization ----------------------------
    print("\n[4] Signing performance fee authorization (via Privy wallet)...")

    position_id = "0x" + secrets.token_hex(32)

    signed_auth = await escrow_client.sign_performance_fee_auth_with_signer(
        signer=signer,
        position_id=position_id,
        expected_winnings=expected_winnings,
        dome_amount=fees.dome_fee,
        affiliate_amount=fees.affiliate_fee,
    )

    print(f"  Position ID: {position_id[:18]}...")
    print(f"  Deadline:    {signed_auth.deadline}")
    print(f"  Signature:   {signed_auth.signature[:18]}...")

    # -- [5] Submit claim via router ---------------------------------------
    print("\n[5] Submitting claim winnings via Dome API...")

    router = PolymarketRouterWithEscrow({
        "api_key": dome_api_key,
        "escrow": {"chain_id": chain_id},
    })

    try:
        result = await router.claim_winnings({
            "position_id": position_id,
            "wallet_type": "privy",
            "payer_address": privy_wallet_address,
            "signer_address": privy_wallet_address,
            "privy_wallet_id": privy_wallet_id,
            "condition_id": condition_id,
            "outcome_index": outcome_index,
            "performance_fee_auth": {
                "positionId": signed_auth.position_id,
                "payer": signed_auth.payer,
                "expectedWinnings": str(signed_auth.expected_winnings),
                "domeAmount": str(signed_auth.dome_amount),
                "affiliateAmount": str(signed_auth.affiliate_amount),
                "chainId": signed_auth.chain_id,
                "deadline": signed_auth.deadline,
                "signature": signed_auth.signature,
            },
        })

        # -- [6] Display results -------------------------------------------
        print("\n[6] Claim winnings result:")
        print(f"  Success:      {result.success}")
        print(f"  Status:       {result.status}")
        print(f"  Position ID:  {result.position_id}")
        print(f"  Wallet Type:  {result.wallet_type}")
        if result.fee_pulled is not None:
            print(f"  Fee Pulled:   {result.fee_pulled}")
        if result.dome_amount is not None:
            print(f"  Dome Amount:  {result.dome_amount}")
        if result.affiliate_amount is not None:
            print(f"  Affiliate:    {result.affiliate_amount}")
        if result.claim_tx_hash:
            print(f"  Claim TX:     {result.claim_tx_hash}")

    except Exception as e:
        print(f"\nClaim failed: {e}")
        sys.exit(1)
    finally:
        await router.close()


if __name__ == "__main__":
    asyncio.run(main())
