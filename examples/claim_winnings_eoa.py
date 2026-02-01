"""EOA Wallet -- Claim Winnings with Performance Fee.

This example shows how to claim winnings from a resolved Polymarket
market using the Dome SDK with a standard EOA wallet (private key).

Flow:
[1] Validate config (PRIVATE_KEY, DOME_API_KEY, CONDITION_ID)
[2] Setup escrow client (DomeFeeEscrowClient)
[3] Calculate performance fees (local)
[4] Sign performance fee authorization (EIP-712 via private key)
[5] Build redeemPositions calldata, sign transaction (web3.py)
[6] Submit claim_winnings(wallet_type='eoa', signed_redeem_tx=...)
[7] Display results

Prerequisites:
1. pip install dome-api-sdk eth-account web3
2. Set environment variables:
   - PRIVATE_KEY: EOA private key (hex string)
   - DOME_API_KEY: Dome API key
   - CONDITION_ID: Condition ID of a resolved market (bytes32 hex)
3. Fund your wallet with MATIC on Polygon for gas

Optional:
- RPC_URL: Polygon RPC URL (defaults to https://polygon-rpc.com)
- OUTCOME_INDEX: Winning outcome index, 0 or 1 (defaults to 1)

Usage:
    PRIVATE_KEY=0x... DOME_API_KEY=... CONDITION_ID=0x... \\
    python examples/claim_winnings_eoa.py
"""

import asyncio
import os
import sys
import secrets

from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    from eth_account import Account
    from web3 import Web3

    from dome_api_sdk import (
        PolymarketRouterWithEscrow,
        DomeFeeEscrowClient,
        build_redeem_positions_tx,
        format_usdc,
        ESCROW_CONTRACT_POLYGON,
    )
    from dome_api_sdk.escrow import MIN_PERF_FEE

    print("=== EOA Wallet -- Claim Winnings with Performance Fee ===\n")

    # -- [1] Validate configuration ----------------------------------------
    print("[1] Validating configuration...")

    private_key = os.environ.get("PRIVATE_KEY", "")
    dome_api_key = os.environ.get("DOME_API_KEY", "")
    rpc_url = os.environ.get("RPC_URL", "https://polygon-rpc.com")
    condition_id = os.environ.get("CONDITION_ID", "")
    outcome_index = int(os.environ.get("OUTCOME_INDEX", "1"))
    chain_id = 137

    if not private_key:
        print("Missing PRIVATE_KEY environment variable")
        sys.exit(1)
    if not dome_api_key:
        print("Missing DOME_API_KEY environment variable")
        sys.exit(1)
    if not condition_id:
        print("Missing CONDITION_ID environment variable")
        sys.exit(1)

    account = Account.from_key(private_key)
    wallet_address = account.address

    print(f"  Wallet:         {wallet_address}")
    print(f"  Condition ID:   {condition_id}")
    print(f"  Outcome Index:  {outcome_index}")

    # -- [2] Setup escrow client -------------------------------------------
    print("\n[2] Setting up escrow client...")

    escrow_client = DomeFeeEscrowClient(
        escrow_address=ESCROW_CONTRACT_POLYGON,
        chain_id=chain_id,
    )

    print(f"  Escrow contract: {ESCROW_CONTRACT_POLYGON}")

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
    print("\n[4] Signing performance fee authorization (EIP-712)...")

    position_id = "0x" + secrets.token_hex(32)

    signed_auth = escrow_client.sign_performance_fee_auth(
        private_key=private_key,
        position_id=position_id,
        expected_winnings=expected_winnings,
        dome_amount=fees.dome_fee,
        affiliate_amount=fees.affiliate_fee,
    )

    print(f"  Position ID: {position_id[:18]}...")
    print(f"  Deadline:    {signed_auth.deadline}")
    print(f"  Signature:   {signed_auth.signature[:18]}...")

    # -- [5] Build and sign redeemPositions transaction --------------------
    print("\n[5] Building and signing redeemPositions transaction...")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    tx_template = build_redeem_positions_tx(condition_id, outcome_index)

    # Build a full transaction for signing
    tx = {
        "to": Web3.to_checksum_address(tx_template["to"]),
        "data": tx_template["data"],
        "value": tx_template["value"],
        "chainId": chain_id,
        "gas": 200_000,
        "nonce": w3.eth.get_transaction_count(wallet_address),
        "maxFeePerGas": w3.eth.gas_price,
        "maxPriorityFeePerGas": w3.to_wei(30, "gwei"),
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    signed_redeem_tx = signed_tx.raw_transaction.hex()

    print(f"  Signed TX: {signed_redeem_tx[:18]}...")

    # -- [6] Submit claim via router ---------------------------------------
    print("\n[6] Submitting claim winnings via Dome API...")

    router = PolymarketRouterWithEscrow({
        "api_key": dome_api_key,
        "escrow": {"chain_id": chain_id},
    })

    try:
        result = await router.claim_winnings({
            "position_id": position_id,
            "wallet_type": "eoa",
            "payer_address": wallet_address,
            "signer_address": wallet_address,
            "signed_redeem_tx": signed_redeem_tx,
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

        # -- [7] Display results -------------------------------------------
        print("\n[7] Claim winnings result:")
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
