# Dome SDK Examples

This directory contains example implementations showing how to integrate the Dome SDK with various wallet providers and use cases.

## Quick Start: Privy + Polymarket (Server-Side)

**The simplest way to integrate Polymarket trading with Privy-managed wallets.**

See [`privy_polymarket_simple.py`](./privy_polymarket_simple.py) for a complete, production-ready example.

### 30-Second Setup

```bash
# 1. Install dependencies
pip install dome-api-sdk python-dotenv

# 2. Set environment variables
export PRIVY_APP_ID="your-privy-app-id"
export PRIVY_APP_SECRET="your-privy-app-secret"
export PRIVY_AUTHORIZATION_KEY="wallet-auth:..." # From Privy dashboard
```

### 3-Step Integration

```python
from dome_api_sdk import (
    PolymarketRouter,
    create_privy_client,
    create_privy_signer,
)

# Step 1: Initialize router with Privy config (ONCE in your app)
router = PolymarketRouter({
    "chain_id": 137,
    "privy": {
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    },
})

# Step 2: Link user (one-time per user, store credentials in your DB)
privy = create_privy_client({
    "app_id": os.environ["PRIVY_APP_ID"],
    "app_secret": os.environ["PRIVY_APP_SECRET"],
    "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
})
signer = create_privy_signer(privy, user.privy_wallet_id, user.wallet_address)

credentials = await router.link_user({
    "user_id": user.id,
    "signer": signer,
})

# Step 3: Place orders
await router.place_order({
    "user_id": user.id,
    "market_id": "104173557214744537570424345347209544585775842950109756851652855913015295701992",
    "side": "buy",
    "size": 100,
    "price": 0.01,
    "order_type": "GTC",  # 'GTC' | 'GTD' | 'FOK' | 'FAK'
    "signer": signer,
}, credentials)
```

### What This Does

1. **Server-side signing** - No user popups, completely backend-driven
2. **One-time setup** - User signs once to create Polymarket API credentials
3. **Persistent credentials** - Store in your database, reuse forever
4. **Direct CLOB access** - Places orders directly on Polymarket (no Dome backend needed)
5. **Same wallet** - EOA wallet is both signer and funder

### Order Types

| Type  | Description                                             |
| ----- | ------------------------------------------------------- |
| `GTC` | Good Till Cancel - stays on book until filled (default) |
| `GTD` | Good Till Date - expires at specified time              |
| `FOK` | Fill Or Kill - fill completely immediately or cancel    |
| `FAK` | Fill And Kill - fill as much as possible, cancel rest   |

Use `FOK` or `FAK` for copy trading where instant fill confirmation is needed.

### Running the Example

```bash
# Set your Privy credentials
export PRIVY_APP_ID="..."
export PRIVY_APP_SECRET="..."
export PRIVY_AUTHORIZATION_KEY="wallet-auth:..."

# Run the example
python privy_polymarket_simple.py

# To actually place an order (use with caution!)
python privy_polymarket_simple.py --place-order
```

---

## Examples

### Privy Integration (`privy_polymarket_simple.py`)

Demonstrates end-to-end integration with [Privy](https://privy.io) for wallet-agnostic Polymarket trading.

**Key Features:**

- Server-side signing with Privy authorization keys
- One-time EIP-712 signature to create Polymarket CLOB API key
- All subsequent trading uses API keys (no wallet signatures)
- Wallet-agnostic design (works with any signer implementation)

**What it demonstrates:**

1. Creating a `RouterSigner` adapter for Privy
2. Linking users to Polymarket via the Dome router
3. Placing orders using API keys
4. Checking and setting token allowances

**Setup:**

```bash
# Install dependencies
pip install dome-api-sdk python-dotenv

# Set environment variables
export PRIVY_APP_ID="your-privy-app-id"
export PRIVY_APP_SECRET="your-privy-app-secret"
export PRIVY_AUTHORIZATION_KEY="your-privy-auth-key"
export DOME_API_KEY="your-dome-api-key"
```

### Privy Ultra Simple (`privy_ultra_simple.py`)

A minimal example showing just Privy client setup and EIP-712 signing.

### Privy with Allowances (`privy_with_allowances.py`)

Shows how to check and set token allowances for Polymarket trading.

### Privy with Builder (`privy_with_builder.py`)

Demonstrates using the builder-signer for order placement.

## Architecture Overview

The router integration follows this flow:

```
┌──────────────┐
│   Frontend   │
│  (Privy UI)  │
└──────┬───────┘
       │ 1. User logs in
       │
       v
┌──────────────────────────────────────────┐
│         Dome SDK Router Layer            │
│  ┌────────────────────────────────────┐  │
│  │  RouterSigner (wallet-agnostic)    │  │
│  │  • get_address()                   │  │
│  │  • sign_typed_data()               │  │
│  └────────────────────────────────────┘  │
│                                          │
│  2. ONE signature to create API key      │
│  3. Store API key in Dome backend        │
└──────────┬───────────────────────────────┘
           │
           v
┌──────────────────────────────────────────┐
│         Dome Router Backend              │
│  • Stores Polymarket CLOB API keys       │
│  • Handles all Polymarket CLOB signing   │
│  • Routes orders to exchanges            │
└──────────┬───────────────────────────────┘
           │
           v
┌──────────────────────────────────────────┐
│      Polymarket CLOB API                 │
│  • Receives signed orders                │
│  • Executes trades                       │
└──────────────────────────────────────────┘
```

## Benefits of This Approach

1. **Single Signature:** Users only sign once to create the API key
2. **Wallet-Agnostic:** Works with Privy, MetaMask, RainbowKit, WalletConnect, etc.
3. **Backend Abstraction:** Your backend handles all exchange-specific logic
4. **Better UX:** No signature prompts for every trade
5. **Scalable:** Easy to add more exchanges (Kalshi, Manifold, etc.)

## Creating Custom Signers

To integrate with a different wallet provider, implement the `RouterSigner` protocol:

```python
from typing import Dict, Any, Protocol

class RouterSigner(Protocol):
    async def get_address(self) -> str:
        """Return the user's wallet address."""
        ...

    async def sign_typed_data(self, payload: Dict[str, Any]) -> str:
        """Sign the EIP-712 payload and return a 0x-prefixed signature."""
        ...
```

### web3.py Example

```python
from web3 import Web3
from eth_account.messages import encode_typed_data

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
        return "0x" + signed.signature.hex()
```

## Testing

To test the router integration locally:

1. Set up environment variables
2. Run the example:

```bash
python privy_polymarket_simple.py
```

## Additional Resources

- [Privy Documentation](https://docs.privy.io)
- [Privy Authorization Keys](https://docs.privy.io/controls/authorization-keys)
- [Dome API Documentation](https://domeapi.io)
- [EIP-712 Specification](https://eips.ethereum.org/EIPS/eip-712)
- [Polymarket CLOB API](https://docs.polymarket.com)

## Questions?

For questions about the router integration:

- Email: kurush@domeapi.com or kunal@domeapi.com
- See main README for additional support options
