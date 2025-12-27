# External Wallet Quickstart (MetaMask, Rabby, etc.)

This guide shows how to integrate external wallets (MetaMask, Rabby, etc.) with Dome SDK for Polymarket trading using Safe smart contract wallets.

## Overview

When using external wallets (non-custodial wallets that users control directly), Polymarket uses a **Safe smart contract wallet** pattern:

1. **EOA (Externally Owned Account)** - The user's MetaMask/Rabby wallet that signs transactions
2. **Safe Wallet** - A smart contract wallet that holds the USDC and positions

This pattern provides:
- Enhanced security through multi-sig capabilities
- Deterministic addresses derived from the EOA
- Gasless trading once set up

## Flow Overview

```
1. User connects wallet (MetaMask/Rabby)
2. Derive Safe address from EOA
3. Deploy Safe (if not already deployed)
4. Fund Safe with USDC
5. Set token allowances
6. Derive API credentials
7. Trade!
```

## Prerequisites

1. **Dome API Key** - Get from [Dome Dashboard](https://domeapi.io)
2. **User's wallet** with some MATIC for gas

## Installation

```bash
pip install dome-api-sdk
```

## Basic Usage

### Step 1: Create a Custom Signer

For external wallets, you need to implement the `RouterSigner` protocol. Here's an example using web3.py:

```python
from typing import Dict, Any
from web3 import Web3
from eth_account.messages import encode_typed_data, SignableMessage

class Web3Signer:
    """RouterSigner implementation using web3.py."""

    def __init__(self, web3: Web3, private_key: str):
        self.web3 = web3
        self.account = web3.eth.account.from_key(private_key)

    async def get_address(self) -> str:
        return self.account.address

    async def sign_typed_data(self, payload: Dict[str, Any]) -> str:
        # Create EIP-712 message
        signable_message = encode_typed_data(
            domain_data=payload["domain"],
            message_types=payload["types"],
            message_data=payload["message"],
        )

        # Sign the message
        signed = self.account.sign_message(signable_message)
        return signed.signature.hex()
```

### Step 2: Initialize the Router

```python
import asyncio
import os
from dome_api_sdk import PolymarketRouter

# Initialize router
router = PolymarketRouter({
    "api_key": os.environ["DOME_API_KEY"],
    "chain_id": 137,  # Polygon mainnet
})
```

### Step 3: Link User with Safe Wallet

```python
async def link_user_with_safe():
    # Create signer from user's wallet
    from web3 import Web3

    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    signer = Web3Signer(web3, os.environ["PRIVATE_KEY"])

    # Link user with Safe wallet
    result = await router.link_user({
        "user_id": "user-123",
        "signer": signer,
        "wallet_type": "safe",
        "auto_deploy_safe": True,  # Deploy Safe if not exists
        "auto_set_allowances": True,  # Set token approvals
    })

    print(f"EOA Address: {result.signer_address}")
    print(f"Safe Address: {result.safe_address}")
    print(f"API Key: {result.credentials.api_key[:10]}...")

    return result
```

### Step 4: Place Orders

```python
async def place_order(link_result):
    result = await router.place_order({
        "user_id": "user-123",
        "market_id": "60487116984468020978247225474488676749601001829886755968952521846780452448915",
        "side": "buy",
        "size": 10,  # 10 shares
        "price": 0.65,  # $0.65 per share
        "signer": signer,
        "wallet_type": "safe",
        "funder_address": link_result.safe_address,  # Safe holds the USDC
    }, link_result.credentials)

    print(f"Order placed! Status: {result['status']}")
```

## Complete Example

```python
import asyncio
import os
from typing import Dict, Any
from web3 import Web3
from eth_account.messages import encode_typed_data
from dome_api_sdk import PolymarketRouter

class Web3Signer:
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

async def main():
    # Initialize
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    signer = Web3Signer(web3, os.environ["PRIVATE_KEY"])

    router = PolymarketRouter({
        "api_key": os.environ["DOME_API_KEY"],
    })

    # Link user
    result = await router.link_user({
        "user_id": "user-123",
        "signer": signer,
        "wallet_type": "safe",
        "auto_deploy_safe": True,
    })

    print(f"Safe Address: {result.safe_address}")
    print("Fund this Safe with USDC before trading!")

    # Place order (after funding)
    order = await router.place_order({
        "user_id": "user-123",
        "market_id": "...",
        "side": "buy",
        "size": 10,
        "price": 0.65,
        "signer": signer,
        "wallet_type": "safe",
        "funder_address": result.safe_address,
    }, result.credentials)

    print(f"Order: {order}")

    await router.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Differences from Privy Integration

| Feature | Privy (EOA) | External (Safe) |
|---------|-------------|-----------------|
| Wallet Type | `eoa` | `safe` |
| Signature Type | 0 | 2 |
| Funder | EOA address | Safe address |
| USDC Location | EOA wallet | Safe wallet |
| Gas Sponsorship | Privy supports | Not supported |

## Checking Allowances

```python
from dome_api_sdk import check_all_allowances

async def check_wallet_setup():
    # For Safe wallets, check the Safe address
    allowances = await router.check_allowances(safe_address)

    if not allowances.all_set:
        print("Missing allowances:")
        if not allowances.usdc_ctf_exchange:
            print("  - USDC -> CTF Exchange")
        if not allowances.usdc_neg_risk_ctf_exchange:
            print("  - USDC -> Neg Risk CTF Exchange")
        if not allowances.ctf_ctf_exchange:
            print("  - CTF -> CTF Exchange")
        # ... etc
```

## Manual Safe Address Derivation

If you need to derive the Safe address before linking:

```python
from dome_api_sdk import PolymarketRouter

router = PolymarketRouter()

# Derive Safe address from any EOA
eoa_address = "0x..."
safe_address = router.derive_safe_address(eoa_address)  # Not yet implemented in Python SDK
print(f"Safe will be at: {safe_address}")
```

## Error Handling

```python
async def safe_trading():
    try:
        result = await router.link_user({
            "user_id": "user-123",
            "signer": signer,
            "wallet_type": "safe",
        })
    except ValueError as e:
        if "Safe not deployed" in str(e):
            print("Safe needs to be deployed first")
        else:
            raise

    try:
        order = await router.place_order({
            "user_id": "user-123",
            "market_id": "...",
            "side": "buy",
            "size": 10,
            "price": 0.65,
            "signer": signer,
            "wallet_type": "safe",
            "funder_address": result.safe_address,
        }, result.credentials)
    except Exception as e:
        if "insufficient funds" in str(e).lower():
            print(f"Fund your Safe at {result.safe_address}")
        else:
            raise
```

## Notes

1. **Funding**: Users must fund their Safe wallet with USDC before trading
2. **Gas**: The EOA needs MATIC for signing (minimal amounts)
3. **Allowances**: Set once per Safe wallet
4. **API Credentials**: Derived from signature, stored in-memory by default

## Next Steps

- Check out [PRIVY_QUICKSTART.md](./PRIVY_QUICKSTART.md) for Privy embedded wallet integration
- See the example scripts in this directory
- Visit [Dome API Documentation](https://docs.domeapi.io) for full API reference
