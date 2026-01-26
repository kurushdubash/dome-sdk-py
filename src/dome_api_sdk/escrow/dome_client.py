"""DomeFeeEscrow Client.

High-level client for interacting with the DomeFeeEscrow contract.
Provides methods for:
- Signing order and performance fee authorizations
- Calculating fees
- Querying escrow status (when connected to a provider)

Example usage:
    ```python
    from dome_api_sdk.escrow import DomeFeeEscrowClient

    # Create client
    client = DomeFeeEscrowClient(
        escrow_address="0x...",
        chain_id=137,
    )

    # Sign order fee authorization
    auth, signature = client.sign_order_fee_auth(
        private_key="0x...",
        order_id="0x...",
        dome_amount=25000,      # $0.025 USDC
        affiliate_amount=5000,  # $0.005 USDC
    )

    # Calculate order fees
    fees = client.calculate_order_fees(
        order_size=10_000_000,  # $10 USDC
        dome_fee_bps=25,        # 0.25%
        affiliate_fee_bps=5,    # 0.05%
    )
    print(f"Total fee: ${fees.total_fee / 1_000_000}")
    ```
"""

from typing import Optional, Tuple

from .dome_types import (
    OrderFeeAuthorization,
    SignedOrderFeeAuthorization,
    PerformanceFeeAuthorization,
    SignedPerformanceFeeAuthorization,
    CalculatedFees,
)
from .dome_signing import (
    create_order_fee_authorization,
    create_performance_fee_authorization,
    sign_order_fee_authorization,
    sign_performance_fee_authorization,
    sign_order_fee_authorization_with_signer,
    sign_performance_fee_authorization_with_signer,
    verify_order_fee_authorization_signature,
    verify_performance_fee_authorization_signature,
    TypedDataSigner,
    MIN_ORDER_FEE,
    MIN_PERF_FEE,
    MAX_ORDER_FEE_BPS,
    MAX_PERF_FEE_BPS,
)


class DomeFeeEscrowClient:
    """Client for the DomeFeeEscrow contract.

    Provides methods for creating and signing fee authorizations for both
    order fees and performance fees with independent dome and affiliate amounts.

    Attributes:
        escrow_address: Address of the DomeFeeEscrow contract
        chain_id: Chain ID (137 for Polygon)
    """

    def __init__(
        self,
        escrow_address: str,
        chain_id: int = 137,
    ):
        """Initialize the DomeFeeEscrowClient.

        Args:
            escrow_address: Address of the DomeFeeEscrow contract
            chain_id: Chain ID (default: 137 for Polygon)
        """
        self.escrow_address = escrow_address
        self.chain_id = chain_id

    def sign_order_fee_auth(
        self,
        private_key: str,
        order_id: str,
        dome_amount: int,
        affiliate_amount: int,
        payer: Optional[str] = None,
        deadline_seconds: int = 3600,
    ) -> Tuple[OrderFeeAuthorization, str]:
        """Sign an order fee authorization.

        Creates and signs an EIP-712 authorization for order fees.
        The user signs approval to pay both dome and affiliate fees.

        Args:
            private_key: Private key for signing (hex string)
            order_id: Unique order ID (bytes32 hex string)
            dome_amount: Dome's fee amount in USDC (6 decimals)
            affiliate_amount: Affiliate's fee amount in USDC (6 decimals)
            payer: Address to pay from (defaults to signer address)
            deadline_seconds: Authorization validity period (default: 1 hour)

        Returns:
            Tuple of (OrderFeeAuthorization, signature_hex_string)

        Example:
            ```python
            auth, sig = client.sign_order_fee_auth(
                private_key="0x...",
                order_id="0x...",
                dome_amount=25000,      # $0.025
                affiliate_amount=5000,  # $0.005
            )
            # Total fee: $0.03
            ```
        """
        from eth_account import Account

        # Derive payer address from private key if not provided
        if payer is None:
            account = Account.from_key(private_key)
            payer = account.address

        # Create authorization
        auth = create_order_fee_authorization(
            order_id=order_id,
            payer=payer,
            dome_amount=dome_amount,
            affiliate_amount=affiliate_amount,
            chain_id=self.chain_id,
            deadline_seconds=deadline_seconds,
        )

        # Sign
        signed = sign_order_fee_authorization(
            private_key=private_key,
            escrow_address=self.escrow_address,
            auth=auth,
        )

        return auth, signed.signature

    def sign_performance_fee_auth(
        self,
        private_key: str,
        position_id: str,
        expected_winnings: int,
        dome_amount: int,
        affiliate_amount: int,
        payer: Optional[str] = None,
        deadline_seconds: int = 3600,
    ) -> Tuple[PerformanceFeeAuthorization, str]:
        """Sign a performance fee authorization.

        Creates and signs an EIP-712 authorization for performance fees.
        The user signs approval to pay fees on their winning position.

        Args:
            private_key: Private key for signing (hex string)
            position_id: Position identifier (bytes32 hex string)
            expected_winnings: Expected winnings in USDC (6 decimals)
            dome_amount: Dome's fee amount in USDC (6 decimals)
            affiliate_amount: Affiliate's fee amount in USDC (6 decimals)
            payer: Address to pay from (defaults to signer address)
            deadline_seconds: Authorization validity period (default: 1 hour)

        Returns:
            Tuple of (PerformanceFeeAuthorization, signature_hex_string)

        Example:
            ```python
            auth, sig = client.sign_performance_fee_auth(
                private_key="0x...",
                position_id="0x...",
                expected_winnings=100_000_000,  # $100
                dome_amount=500_000,            # $0.50 (0.5%)
                affiliate_amount=100_000,       # $0.10 (0.1%)
            )
            ```
        """
        from eth_account import Account

        # Derive payer address from private key if not provided
        if payer is None:
            account = Account.from_key(private_key)
            payer = account.address

        # Create authorization
        auth = create_performance_fee_authorization(
            position_id=position_id,
            payer=payer,
            expected_winnings=expected_winnings,
            dome_amount=dome_amount,
            affiliate_amount=affiliate_amount,
            chain_id=self.chain_id,
            deadline_seconds=deadline_seconds,
        )

        # Sign
        signed = sign_performance_fee_authorization(
            private_key=private_key,
            escrow_address=self.escrow_address,
            auth=auth,
        )

        return auth, signed.signature

    async def sign_order_fee_auth_with_signer(
        self,
        signer: TypedDataSigner,
        order_id: str,
        dome_amount: int,
        affiliate_amount: int,
        deadline_seconds: int = 3600,
    ) -> Tuple[OrderFeeAuthorization, str]:
        """Sign an order fee authorization using an external signer.

        Use this with RouterSigner (Privy, MetaMask, etc.) or any wallet
        that implements the TypedDataSigner protocol.

        Args:
            signer: External signer (Privy, MetaMask, etc.)
            order_id: Unique order ID (bytes32 hex string)
            dome_amount: Dome's fee amount in USDC (6 decimals)
            affiliate_amount: Affiliate's fee amount in USDC (6 decimals)
            deadline_seconds: Authorization validity period (default: 1 hour)

        Returns:
            Tuple of (OrderFeeAuthorization, signature_hex_string)
        """
        payer = await signer.get_address()

        auth = create_order_fee_authorization(
            order_id=order_id,
            payer=payer,
            dome_amount=dome_amount,
            affiliate_amount=affiliate_amount,
            chain_id=self.chain_id,
            deadline_seconds=deadline_seconds,
        )

        signed = await sign_order_fee_authorization_with_signer(
            signer=signer,
            escrow_address=self.escrow_address,
            auth=auth,
        )

        return auth, signed.signature

    async def sign_performance_fee_auth_with_signer(
        self,
        signer: TypedDataSigner,
        position_id: str,
        expected_winnings: int,
        dome_amount: int,
        affiliate_amount: int,
        deadline_seconds: int = 3600,
    ) -> Tuple[PerformanceFeeAuthorization, str]:
        """Sign a performance fee authorization using an external signer.

        Use this with RouterSigner (Privy, MetaMask, etc.) or any wallet
        that implements the TypedDataSigner protocol.

        Args:
            signer: External signer (Privy, MetaMask, etc.)
            position_id: Position identifier (bytes32 hex string)
            expected_winnings: Expected winnings in USDC (6 decimals)
            dome_amount: Dome's fee amount in USDC (6 decimals)
            affiliate_amount: Affiliate's fee amount in USDC (6 decimals)
            deadline_seconds: Authorization validity period (default: 1 hour)

        Returns:
            Tuple of (PerformanceFeeAuthorization, signature_hex_string)
        """
        payer = await signer.get_address()

        auth = create_performance_fee_authorization(
            position_id=position_id,
            payer=payer,
            expected_winnings=expected_winnings,
            dome_amount=dome_amount,
            affiliate_amount=affiliate_amount,
            chain_id=self.chain_id,
            deadline_seconds=deadline_seconds,
        )

        signed = await sign_performance_fee_authorization_with_signer(
            signer=signer,
            escrow_address=self.escrow_address,
            auth=auth,
        )

        return auth, signed.signature

    def verify_order_fee_signature(
        self,
        signed_auth: SignedOrderFeeAuthorization,
        expected_signer: str,
    ) -> bool:
        """Verify an order fee authorization signature (EOA only).

        Note: This only works for EOA signatures. For SAFE/smart contract
        wallet signatures, verification must happen on-chain via EIP-1271.

        Args:
            signed_auth: Signed order fee authorization
            expected_signer: Expected signer address

        Returns:
            True if signature is valid and from expected signer
        """
        return verify_order_fee_authorization_signature(
            signed_auth=signed_auth,
            escrow_address=self.escrow_address,
            expected_signer=expected_signer,
        )

    def verify_performance_fee_signature(
        self,
        signed_auth: SignedPerformanceFeeAuthorization,
        expected_signer: str,
    ) -> bool:
        """Verify a performance fee authorization signature (EOA only).

        Note: This only works for EOA signatures. For SAFE/smart contract
        wallet signatures, verification must happen on-chain via EIP-1271.

        Args:
            signed_auth: Signed performance fee authorization
            expected_signer: Expected signer address

        Returns:
            True if signature is valid and from expected signer
        """
        return verify_performance_fee_authorization_signature(
            signed_auth=signed_auth,
            escrow_address=self.escrow_address,
            expected_signer=expected_signer,
        )

    @staticmethod
    def calculate_order_fees(
        order_size: int,
        dome_fee_bps: int,
        affiliate_fee_bps: int = 0,
    ) -> CalculatedFees:
        """Calculate order fees for a given order size.

        Calculates independent dome and affiliate fees based on basis points.
        Applies minimum fee floor if total is below minimum.

        Args:
            order_size: Order size in USDC (6 decimals)
            dome_fee_bps: Dome's fee rate in basis points (max: 100 = 1%)
            affiliate_fee_bps: Affiliate's fee rate in basis points (max: 100 = 1%)

        Returns:
            CalculatedFees with dome_fee, affiliate_fee, and total_fee

        Raises:
            ValueError: If fee rates exceed maximum

        Example:
            ```python
            fees = DomeFeeEscrowClient.calculate_order_fees(
                order_size=10_000_000,  # $10 USDC
                dome_fee_bps=25,        # 0.25%
                affiliate_fee_bps=5,    # 0.05%
            )
            # fees.dome_fee = 25000 ($0.025)
            # fees.affiliate_fee = 5000 ($0.005)
            # fees.total_fee = 30000 ($0.03)
            ```
        """
        if dome_fee_bps > MAX_ORDER_FEE_BPS:
            raise ValueError(
                f"Dome fee rate too high: {dome_fee_bps} bps. Maximum: {MAX_ORDER_FEE_BPS} bps (1%)"
            )
        if affiliate_fee_bps > MAX_ORDER_FEE_BPS:
            raise ValueError(
                f"Affiliate fee rate too high: {affiliate_fee_bps} bps. Maximum: {MAX_ORDER_FEE_BPS} bps (1%)"
            )

        dome_fee = (order_size * dome_fee_bps) // 10000
        affiliate_fee = (order_size * affiliate_fee_bps) // 10000
        total_fee = dome_fee + affiliate_fee

        # Apply minimum fee floor
        if total_fee < MIN_ORDER_FEE and total_fee > 0:
            # Scale up proportionally
            scale = MIN_ORDER_FEE * 10000 // total_fee
            dome_fee = (dome_fee * scale) // 10000
            affiliate_fee = MIN_ORDER_FEE - dome_fee
            total_fee = MIN_ORDER_FEE
        elif total_fee == 0:
            dome_fee = MIN_ORDER_FEE
            affiliate_fee = 0
            total_fee = MIN_ORDER_FEE

        return CalculatedFees(
            dome_fee=dome_fee,
            affiliate_fee=affiliate_fee,
            total_fee=total_fee,
        )

    @staticmethod
    def calculate_performance_fees(
        winnings: int,
        dome_fee_bps: int,
        affiliate_fee_bps: int = 0,
    ) -> CalculatedFees:
        """Calculate performance fees for given winnings.

        Calculates independent dome and affiliate fees based on basis points.
        Applies minimum fee floor if total is below minimum.

        Args:
            winnings: Winnings amount in USDC (6 decimals)
            dome_fee_bps: Dome's fee rate in basis points (max: 1000 = 10%)
            affiliate_fee_bps: Affiliate's fee rate in basis points (max: 1000 = 10%)

        Returns:
            CalculatedFees with dome_fee, affiliate_fee, and total_fee

        Raises:
            ValueError: If fee rates exceed maximum

        Example:
            ```python
            fees = DomeFeeEscrowClient.calculate_performance_fees(
                winnings=100_000_000,   # $100 USDC winnings
                dome_fee_bps=500,       # 5%
                affiliate_fee_bps=100,  # 1%
            )
            # fees.dome_fee = 5_000_000 ($5.00)
            # fees.affiliate_fee = 1_000_000 ($1.00)
            # fees.total_fee = 6_000_000 ($6.00)
            ```
        """
        if dome_fee_bps > MAX_PERF_FEE_BPS:
            raise ValueError(
                f"Dome fee rate too high: {dome_fee_bps} bps. Maximum: {MAX_PERF_FEE_BPS} bps (10%)"
            )
        if affiliate_fee_bps > MAX_PERF_FEE_BPS:
            raise ValueError(
                f"Affiliate fee rate too high: {affiliate_fee_bps} bps. Maximum: {MAX_PERF_FEE_BPS} bps (10%)"
            )

        dome_fee = (winnings * dome_fee_bps) // 10000
        affiliate_fee = (winnings * affiliate_fee_bps) // 10000
        total_fee = dome_fee + affiliate_fee

        # Apply minimum fee floor
        if total_fee < MIN_PERF_FEE and total_fee > 0:
            # Scale up proportionally
            scale = MIN_PERF_FEE * 10000 // total_fee
            dome_fee = (dome_fee * scale) // 10000
            affiliate_fee = MIN_PERF_FEE - dome_fee
            total_fee = MIN_PERF_FEE
        elif total_fee == 0:
            dome_fee = MIN_PERF_FEE
            affiliate_fee = 0
            total_fee = MIN_PERF_FEE

        return CalculatedFees(
            dome_fee=dome_fee,
            affiliate_fee=affiliate_fee,
            total_fee=total_fee,
        )
