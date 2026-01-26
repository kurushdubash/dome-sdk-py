"""Dome Fee Escrow Module.

This module provides functionality for fee authorization with the Dome Fee Escrow contracts.

Supports two contracts:
1. DomeFeeEscrow (v1/MVP) - Single fee amount
2. DomeFeeEscrow (v2) - Independent dome and affiliate fees for order and performance fees

Key components:
- Order ID generation (deterministic, collision-resistant)
- Fee authorization creation and signing (EIP-712)
- Utility functions for USDC formatting

Example usage (v1/MVP - DomeFeeEscrow):
    ```python
    from dome_api_sdk.escrow import (
        generate_order_id,
        create_fee_authorization,
        sign_fee_authorization,
        OrderParams,
        ESCROW_CONTRACT_POLYGON,
    )
    import time

    # Generate order ID
    order_id = generate_order_id(OrderParams(
        user_address="0x...",
        market_id="12345",
        side="buy",
        size=1_000_000,  # $1 USDC
        price=0.65,
        timestamp=int(time.time() * 1000),
        chain_id=137,
    ))

    # Create fee authorization
    fee_auth = create_fee_authorization(
        order_id=order_id,
        payer="0x...",
        fee_amount=2500,  # $0.0025 USDC
        deadline_seconds=3600,
    )

    # Sign with private key
    signed = sign_fee_authorization(
        private_key="0x...",
        escrow_address=ESCROW_CONTRACT_POLYGON,
        fee_auth=fee_auth,
        chain_id=137,
    )
    ```

Example usage (v2 - DomeFeeEscrow):
    ```python
    from dome_api_sdk.escrow import DomeFeeEscrowClient

    # Create client
    client = DomeFeeEscrowClient(
        escrow_address="0x...",  # DomeFeeEscrow address
        chain_id=137,
    )

    # Sign order fee authorization (with independent dome + affiliate fees)
    auth, signature = client.sign_order_fee_auth(
        private_key="0x...",
        order_id="0x...",
        dome_amount=25000,      # $0.025 USDC to Dome
        affiliate_amount=5000,  # $0.005 USDC to Affiliate
    )

    # Sign performance fee authorization
    auth, signature = client.sign_performance_fee_auth(
        private_key="0x...",
        position_id="0x...",
        expected_winnings=100_000_000,  # $100
        dome_amount=500_000,            # $0.50 (5% of winnings)
        affiliate_amount=100_000,       # $0.10 (1% of winnings)
    )

    # Calculate fees
    fees = client.calculate_order_fees(
        order_size=10_000_000,  # $10 USDC
        dome_fee_bps=25,        # 0.25%
        affiliate_fee_bps=5,    # 0.05%
    )
    print(f"Total fee: ${fees.total_fee / 1_000_000}")
    ```
"""

# v1/MVP DomeFeeEscrow types and functions
from .types import (
    OrderParams,
    FeeAuthorization,
    SignedFeeAuthorization,
    FEE_AUTHORIZATION_TYPES,
)
from .order_id import generate_order_id, verify_order_id
from .signing import (
    create_eip712_domain,
    create_fee_authorization,
    sign_fee_authorization,
    sign_fee_authorization_with_signer,
    verify_fee_authorization_signature,
    TypedDataSigner,
)
from .utils import (
    USDC_POLYGON,
    ESCROW_CONTRACT_POLYGON,
    ESCROW_CONTRACT_V2_POLYGON,
    ZERO_ADDRESS,
    format_usdc,
    parse_usdc,
    format_bps,
    calculate_fee,
    calculate_order_size_usdc,
)

# v2 DomeFeeEscrow types and functions
from .dome_types import (
    OrderFeeAuthorization,
    SignedOrderFeeAuthorization,
    PerformanceFeeAuthorization,
    SignedPerformanceFeeAuthorization,
    ORDER_FEE_AUTHORIZATION_TYPES,
    PERFORMANCE_FEE_AUTHORIZATION_TYPES,
    CalculatedFees,
    EscrowStatus,
    RemainingEscrow,
)
from .dome_signing import (
    create_eip712_domain as create_dome_eip712_domain,
    create_order_fee_authorization,
    create_performance_fee_authorization,
    sign_order_fee_authorization,
    sign_performance_fee_authorization,
    sign_order_fee_authorization_with_signer,
    sign_performance_fee_authorization_with_signer,
    verify_order_fee_authorization_signature,
    verify_performance_fee_authorization_signature,
    MIN_ORDER_FEE,
    MIN_PERF_FEE,
    MAX_FEE_ABSOLUTE,
    MAX_ORDER_FEE_BPS,
    MAX_PERF_FEE_BPS,
)
from .dome_client import DomeFeeEscrowClient

__all__ = [
    # ============ v1/MVP DomeFeeEscrow ============
    # Types
    "OrderParams",
    "FeeAuthorization",
    "SignedFeeAuthorization",
    "FEE_AUTHORIZATION_TYPES",
    "TypedDataSigner",
    # Order ID
    "generate_order_id",
    "verify_order_id",
    # Signing
    "create_dome_eip712_domain",
    "create_fee_authorization",
    "sign_fee_authorization",
    "sign_fee_authorization_with_signer",
    "verify_fee_authorization_signature",
    # Utils
    "USDC_POLYGON",
    "ESCROW_CONTRACT_POLYGON",
    "ESCROW_CONTRACT_V2_POLYGON",
    "ZERO_ADDRESS",
    "format_usdc",
    "parse_usdc",
    "format_bps",
    "calculate_fee",
    "calculate_order_size_usdc",
    # ============ v2 DomeFeeEscrow ============
    # Client
    "DomeFeeEscrowClient",
    # Types
    "OrderFeeAuthorization",
    "SignedOrderFeeAuthorization",
    "PerformanceFeeAuthorization",
    "SignedPerformanceFeeAuthorization",
    "ORDER_FEE_AUTHORIZATION_TYPES",
    "PERFORMANCE_FEE_AUTHORIZATION_TYPES",
    "CalculatedFees",
    "EscrowStatus",
    "RemainingEscrow",
    # Signing functions
    "create_dome_eip712_domain",
    "create_order_fee_authorization",
    "create_performance_fee_authorization",
    "sign_order_fee_authorization",
    "sign_performance_fee_authorization",
    "sign_order_fee_authorization_with_signer",
    "sign_performance_fee_authorization_with_signer",
    "verify_order_fee_authorization_signature",
    "verify_performance_fee_authorization_signature",
    # Constants
    "MIN_ORDER_FEE",
    "MIN_PERF_FEE",
    "MAX_FEE_ABSOLUTE",
    "MAX_ORDER_FEE_BPS",
    "MAX_PERF_FEE_BPS",
]
