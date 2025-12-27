# External Wallet (EOA) Integration

This guide explains how to integrate external wallets (MetaMask, Rabby, etc.) with Polymarket trading using Safe smart contract wallets.

## Overview

Unlike Privy-managed embedded wallets, external wallets require a different architecture:

- **EOA (Externally Owned Account)**: Your browser wallet (MetaMask, Rabby) that signs transactions
- **Safe Wallet**: A smart contract wallet that holds your funds (USDC) for trading
- **Builder Signer**: Dome's remote signing service for order attribution

```
User's MetaMask (EOA)
       |
       | signs transactions
       v
Safe Smart Account (holds USDC)
       |
       | trades via
       v
Polymarket CLOB
```

## Key Concepts

### Wallet Types

| Type | Description                   | Signature Type      |
| ---- | ----------------------------- | ------------------- |
| EOA  | Direct wallet signing (Privy) | `signatureType = 0` |
| Safe | Smart contract wallet         | `signatureType = 2` |

### Safe Address Derivation

Safe addresses are **deterministically derived** from your EOA address using CREATE2. This means:

- The Safe address is always the same for a given EOA
- You can know the Safe address before deploying it
- Users fund the Safe address, not their EOA

## Python Integration

### Quick Start

```bash
pip install dome-api-sdk web3
```

### Core Implementation

#### 1. Create a Custom Signer

```python
from typing import Dict, Any
from web3 import Web3
from eth_account.messages import encode_typed_data

class Web3Signer:
    """RouterSigner implementation using web3.py."""

    def __init__(self, web3: Web3, private_key: str):
        self.web3 = web3
        self.account = web3.eth.account.from_key(private_key)

    async def get_address(self) -> str:
        return self.account.address

    async def sign_typed_data(self, payload: Dict[str, Any]) -> str:
        signable_message = encode_typed_data(
            domain_data=payload["domain"],
            message_types=payload["types"],
            message_data=payload["message"],
        )
        signed = self.account.sign_message(signable_message)
        return signed.signature.hex()
```

#### 2. Initialize Router and Link User

```python
import asyncio
import os
from dome_api_sdk import PolymarketRouter

async def main():
    # Initialize
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    signer = Web3Signer(web3, os.environ["PRIVATE_KEY"])

    router = PolymarketRouter({
        "api_key": os.environ["DOME_API_KEY"],
    })

    # Link user with Safe wallet
    result = await router.link_user({
        "user_id": "user-123",
        "signer": signer,
        "wallet_type": "safe",
        "auto_deploy_safe": True,
        "auto_set_allowances": True,
    })

    print(f"EOA Address: {result.signer_address}")
    print(f"Safe Address: {result.safe_address}")
    print("Fund this Safe with USDC before trading!")

    return result

asyncio.run(main())
```

#### 3. Place Orders

```python
async def place_order(router, signer, link_result, credentials):
    result = await router.place_order({
        "user_id": "user-123",
        "market_id": "104173557214744537570424345347209544585775842950109756851652855913015295701992",
        "side": "buy",
        "size": 100,  # 100 shares
        "price": 0.01,  # $0.01 per share
        "signer": signer,
        "wallet_type": "safe",
        "funder_address": link_result.safe_address,  # Safe holds the USDC
        "order_type": "GTC",
    }, credentials)

    print(f"Order placed! Status: {result['status']}")
```

## Session Flow

1. **Connect Wallet**: User connects MetaMask/Rabby
2. **Derive Safe Address**: Deterministically compute Safe address from EOA
3. **Check Deployment**: See if Safe is already deployed
4. **Deploy Safe** (if needed): Prompts user for signature
5. **Set Allowances**: Approve USDC for Polymarket contracts
6. **Fund Safe**: User sends USDC to Safe address
7. **Ready to Trade**: Safe is ready for order placement

## Builder Signing

All requests are signed through Dome's builder-signer service:

```
https://builder-signer.domeapi.io/builder-signer/sign
```

This provides:

- Better order routing and execution
- Reduced MEV exposure
- Priority order matching
- No local credentials needed

## Differences from Privy Integration

| Feature        | Privy (EOA)               | External Wallet (Safe)  |
| -------------- | ------------------------- | ----------------------- |
| Wallet         | Embedded, server-managed  | User's browser wallet   |
| Funds          | Held in EOA               | Held in Safe            |
| Signing        | Server-side via Privy API | Client-side via browser |
| Signature Type | 0                         | 2                       |
| Deployment     | None needed               | Safe must be deployed   |
| Gas            | Can be sponsored          | User pays (or relayer)  |

## Order Types

When placing orders, you can specify the `order_type` parameter:

| Type  | Name             | Behavior                                                |
| ----- | ---------------- | ------------------------------------------------------- |
| `GTC` | Good Till Cancel | Order stays on book until filled or cancelled (default) |
| `GTD` | Good Till Date   | Order expires at specified time                         |
| `FOK` | Fill Or Kill     | Must fill completely immediately or cancel entirely     |
| `FAK` | Fill And Kill    | Fills as much as possible immediately, cancels the rest |

```python
await router.place_order({
    "user_id": "user-123",
    "market_id": "...",
    "side": "buy",
    "size": 100,
    "price": 0.5,
    "order_type": "FOK",  # For copy trading - instant fill or cancel
    "signer": signer,
    "wallet_type": "safe",
    "funder_address": safe_address,
}, credentials)
```

**Copy Trading Tip**: Use `FOK` or `FAK` for instant confirmation of whether an order was filled.

## Next Steps

After initializing a trading session:

1. **Fund your Safe**: Send USDC to the Safe address shown in the UI
2. **Place Orders**: Use the Polymarket CLOB client with `signature_type: 2`
3. **Monitor Positions**: Query the CLOB API for your positions

## Troubleshooting

### "Safe deployment failed"

- Ensure you're connected to Polygon network
- Check that you approved the signature request in your wallet

### "Allowances not set"

- The RelayClient handles this automatically
- If it fails, you may need to set approvals manually via the Safe

### "Wrong network"

- The app should auto-switch to Polygon (chain ID 137)
- If not, manually switch in your wallet

## Resources

- [Polymarket CLOB Client](https://github.com/Polymarket/clob-client)
- [Safe Smart Accounts](https://safe.global/)
- [web3.py Documentation](https://web3py.readthedocs.io/)
- [Dome SDK](https://github.com/domeapi/dome-sdk-py)
