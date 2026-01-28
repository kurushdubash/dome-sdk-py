"""Escrow Types for Dome Fee Escrow.

User-facing types for fee authorization signing.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class OrderParams:
    """Parameters used to generate a unique order ID."""

    user_address: str
    """Wallet address of the user (EOA or SAFE)."""

    market_id: str
    """Polymarket token ID."""

    side: Literal["buy", "sell"]
    """Order side."""

    size: int
    """USDC amount in 6 decimals (e.g., 1000000 = $1)."""

    price: float
    """Price from 0.00 to 1.00."""

    timestamp: int
    """Unix timestamp in milliseconds (e.g., int(time.time() * 1000))."""

    chain_id: int
    """Chain ID for cross-chain replay protection (137 for Polygon)."""


@dataclass
class FeeAuthorization:
    """Fee authorization to be signed by the user."""

    order_id: str
    """Unique order ID (bytes32 hex string)."""

    payer: str
    """Address that will pay the fee (EOA or SAFE)."""

    fee_amount: int
    """Fee amount in USDC (6 decimals)."""

    deadline: int
    """Unix timestamp deadline for the authorization."""


@dataclass
class SignedFeeAuthorization(FeeAuthorization):
    """Fee authorization with signature."""

    signature: str
    """EIP-712 signature (65 bytes packed hex string)."""


# EIP-712 types for fee authorization
FEE_AUTHORIZATION_TYPES = {
    "FeeAuthorization": [
        {"name": "orderId", "type": "bytes32"},
        {"name": "payer", "type": "address"},
        {"name": "feeAmount", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ],
}
