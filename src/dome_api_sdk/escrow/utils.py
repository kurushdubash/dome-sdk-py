"""Utility functions for Dome Fee Escrow."""

# USDC on Polygon
USDC_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# Default Escrow Contract on Polygon
ESCROW_CONTRACT_POLYGON = "0x989876083eD929BE583b8138e40D469ea3E53a37"

# Zero address
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def format_usdc(amount: int) -> str:
    """Format USDC amount (6 decimals) to human readable string.

    Args:
        amount: USDC amount in 6 decimals (e.g., 1000000 = $1)

    Returns:
        Human readable string (e.g., "1.00")
    """
    return f"{amount / 1_000_000:.6f}".rstrip("0").rstrip(".")


def parse_usdc(amount: float) -> int:
    """Parse human readable amount to USDC (6 decimals).

    Args:
        amount: Human readable amount (e.g., 1.50)

    Returns:
        USDC amount in 6 decimals (e.g., 1500000)
    """
    return int(amount * 1_000_000)


def format_bps(bps: int) -> str:
    """Format basis points to percentage string.

    Args:
        bps: Basis points (e.g., 25 = 0.25%)

    Returns:
        Percentage string (e.g., "0.25%")
    """
    return f"{bps / 100}%"


def calculate_fee(order_size: int, fee_bps: int) -> int:
    """Calculate fee amount from order size and basis points.

    Args:
        order_size: Order size in USDC (6 decimals)
        fee_bps: Fee in basis points (e.g., 25 = 0.25%)

    Returns:
        Fee amount in USDC (6 decimals)
    """
    return (order_size * fee_bps) // 10000


def calculate_order_size_usdc(size: float, price: float) -> int:
    """Calculate order size in USDC from shares and price.

    For a BUY order: you pay (size * price) USDC to receive (size) shares
    For a SELL order: you sell (size) shares to receive (size * price) USDC

    Args:
        size: Number of shares
        price: Price per share (0.00 to 1.00)

    Returns:
        USDC cost/proceeds in 6 decimals
    """
    return parse_usdc(size * price)
