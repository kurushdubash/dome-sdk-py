"""Dome Fee Escrow Module.

This module provides functionality for fee authorization with the Dome Fee Escrow contract.

Key components:
- Order ID generation (deterministic, collision-resistant)
- Fee authorization creation and signing (EIP-712)
- Utility functions for USDC formatting

Example usage:
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
"""

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
    ZERO_ADDRESS,
    format_usdc,
    parse_usdc,
    format_bps,
    calculate_fee,
    calculate_order_size_usdc,
)

__all__ = [
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
    "create_eip712_domain",
    "create_fee_authorization",
    "sign_fee_authorization",
    "sign_fee_authorization_with_signer",
    "verify_fee_authorization_signature",
    # Utils
    "USDC_POLYGON",
    "ESCROW_CONTRACT_POLYGON",
    "ZERO_ADDRESS",
    "format_usdc",
    "parse_usdc",
    "format_bps",
    "calculate_fee",
    "calculate_order_size_usdc",
]
