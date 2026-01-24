"""Unified Fee Escrow Types.

User-facing types for the DomeFeeEscrow contract that supports both
order fees and performance fees with independent dome and affiliate fee amounts.
"""

from dataclasses import dataclass
from typing import Dict, List, TypedDict


@dataclass
class OrderFeeAuthorization:
    """Order fee authorization to be signed by the user.

    Authorizes the escrow contract to pull order fees for a specific order.
    Supports independent dome and affiliate fees (not a split of one fee).

    Attributes:
        order_id: Unique order ID (bytes32 hex string)
        payer: Address that will pay the fee (EOA or SAFE)
        dome_amount: Dome's fee amount in USDC (6 decimals) - goes 100% to Dome
        affiliate_amount: Affiliate's fee amount in USDC (6 decimals) - goes 100% to Affiliate
        chain_id: Chain ID for cross-chain replay protection (137 for Polygon)
        deadline: Unix timestamp deadline for the authorization
    """

    order_id: str
    """Unique order ID (bytes32 hex string)."""

    payer: str
    """Address that will pay the fee (EOA or SAFE)."""

    dome_amount: int
    """Dome's fee amount in USDC (6 decimals) - goes 100% to Dome."""

    affiliate_amount: int
    """Affiliate's fee amount in USDC (6 decimals) - goes 100% to Affiliate."""

    chain_id: int
    """Chain ID for cross-chain replay protection (137 for Polygon)."""

    deadline: int
    """Unix timestamp deadline for the authorization."""

    @property
    def total_fee(self) -> int:
        """Total fee amount (dome_amount + affiliate_amount)."""
        return self.dome_amount + self.affiliate_amount


@dataclass
class SignedOrderFeeAuthorization(OrderFeeAuthorization):
    """Order fee authorization with signature."""

    signature: str
    """EIP-712 signature (65 bytes packed hex string)."""


@dataclass
class PerformanceFeeAuthorization:
    """Performance fee authorization to be signed by the user.

    Authorizes the escrow contract to pull performance fees for a winning position.
    Supports independent dome and affiliate fees (not a split of one fee).

    Attributes:
        position_id: Position identifier (bytes32 hex string, can be same as order_id)
        payer: Address that will pay the fee (EOA or SAFE)
        expected_winnings: Expected winnings amount in USDC (6 decimals)
        dome_amount: Dome's fee amount in USDC (6 decimals) - goes 100% to Dome
        affiliate_amount: Affiliate's fee amount in USDC (6 decimals) - goes 100% to Affiliate
        chain_id: Chain ID for cross-chain replay protection (137 for Polygon)
        deadline: Unix timestamp deadline for the authorization
    """

    position_id: str
    """Position identifier (bytes32 hex string)."""

    payer: str
    """Address that will pay the fee (EOA or SAFE)."""

    expected_winnings: int
    """Expected winnings amount in USDC (6 decimals)."""

    dome_amount: int
    """Dome's fee amount in USDC (6 decimals) - goes 100% to Dome."""

    affiliate_amount: int
    """Affiliate's fee amount in USDC (6 decimals) - goes 100% to Affiliate."""

    chain_id: int
    """Chain ID for cross-chain replay protection (137 for Polygon)."""

    deadline: int
    """Unix timestamp deadline for the authorization."""

    @property
    def total_fee(self) -> int:
        """Total fee amount (dome_amount + affiliate_amount)."""
        return self.dome_amount + self.affiliate_amount


@dataclass
class SignedPerformanceFeeAuthorization(PerformanceFeeAuthorization):
    """Performance fee authorization with signature."""

    signature: str
    """EIP-712 signature (65 bytes packed hex string)."""


class EIP712Type(TypedDict):
    """EIP-712 type definition."""
    name: str
    type: str


# EIP-712 types for order fee authorization
# Matches the contract's ORDER_FEE_TYPEHASH
ORDER_FEE_AUTHORIZATION_TYPES: Dict[str, List[EIP712Type]] = {
    "OrderFeeAuthorization": [
        {"name": "orderId", "type": "bytes32"},
        {"name": "payer", "type": "address"},
        {"name": "domeAmount", "type": "uint256"},
        {"name": "affiliateAmount", "type": "uint256"},
        {"name": "chainId", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ],
}


# EIP-712 types for performance fee authorization
# Matches the contract's PERFORMANCE_FEE_TYPEHASH
PERFORMANCE_FEE_AUTHORIZATION_TYPES: Dict[str, List[EIP712Type]] = {
    "PerformanceFeeAuthorization": [
        {"name": "positionId", "type": "bytes32"},
        {"name": "payer", "type": "address"},
        {"name": "expectedWinnings", "type": "uint256"},
        {"name": "domeAmount", "type": "uint256"},
        {"name": "affiliateAmount", "type": "uint256"},
        {"name": "chainId", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ],
}


@dataclass
class CalculatedFees:
    """Result of fee calculation.

    Attributes:
        dome_fee: Dome's fee amount in USDC (6 decimals)
        affiliate_fee: Affiliate's fee amount in USDC (6 decimals)
        total_fee: Total fee (dome_fee + affiliate_fee)
    """

    dome_fee: int
    """Dome's fee amount in USDC (6 decimals)."""

    affiliate_fee: int
    """Affiliate's fee amount in USDC (6 decimals)."""

    total_fee: int
    """Total fee (dome_fee + affiliate_fee)."""


@dataclass
class EscrowStatus:
    """Escrow status for an order/position.

    Attributes:
        payer: Address that paid the fees
        affiliate: Affiliate wallet address
        order_fee_dome_amount: Dome's order fee amount
        order_fee_affiliate_amount: Affiliate's order fee amount
        perf_fee_dome_amount: Dome's performance fee amount
        perf_fee_affiliate_amount: Affiliate's performance fee amount
        is_complete: Whether all fees are settled
        time_until_withdraw: Time until user can emergency withdraw (0 if available)
    """

    payer: str
    affiliate: str
    order_fee_dome_amount: int
    order_fee_affiliate_amount: int
    perf_fee_dome_amount: int
    perf_fee_affiliate_amount: int
    is_complete: bool
    time_until_withdraw: int

    @property
    def total_order_fee(self) -> int:
        """Total order fee amount."""
        return self.order_fee_dome_amount + self.order_fee_affiliate_amount

    @property
    def total_perf_fee(self) -> int:
        """Total performance fee amount."""
        return self.perf_fee_dome_amount + self.perf_fee_affiliate_amount


@dataclass
class RemainingEscrow:
    """Remaining escrow amounts for an order/position.

    Attributes:
        order_fee_dome_remaining: Remaining dome order fee
        order_fee_affiliate_remaining: Remaining affiliate order fee
        perf_fee_dome_remaining: Remaining dome performance fee
        perf_fee_affiliate_remaining: Remaining affiliate performance fee
        total_remaining: Total remaining across all fee types
    """

    order_fee_dome_remaining: int
    order_fee_affiliate_remaining: int
    perf_fee_dome_remaining: int
    perf_fee_affiliate_remaining: int
    total_remaining: int
