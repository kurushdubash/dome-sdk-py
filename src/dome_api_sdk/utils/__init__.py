"""Utility modules for the Dome SDK."""

from .allowances import (
    POLYGON_ADDRESSES,
    check_all_allowances,
    get_polygon_provider,
    set_all_allowances,
)
from .privy import (
    PrivyClient,
    RouterSigner,
    check_privy_wallet_allowances,
    create_privy_client,
    create_privy_signer,
    create_privy_signer_from_env,
    set_privy_wallet_allowances,
)

__all__ = [
    # Privy utilities
    "PrivyClient",
    "RouterSigner",
    "create_privy_client",
    "create_privy_signer",
    "create_privy_signer_from_env",
    "check_privy_wallet_allowances",
    "set_privy_wallet_allowances",
    # Allowance utilities
    "POLYGON_ADDRESSES",
    "check_all_allowances",
    "set_all_allowances",
    "get_polygon_provider",
]
