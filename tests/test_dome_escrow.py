"""Tests for the Unified Fee Escrow module (v2).

Tests for OrderFeeAuthorization and PerformanceFeeAuthorization
with independent dome and affiliate fees.
"""

import time
import pytest
from eth_account import Account

from src.dome_api_sdk.escrow import (
    # Types
    OrderFeeAuthorization,
    SignedOrderFeeAuthorization,
    PerformanceFeeAuthorization,
    SignedPerformanceFeeAuthorization,
    ORDER_FEE_AUTHORIZATION_TYPES,
    PERFORMANCE_FEE_AUTHORIZATION_TYPES,
    CalculatedFees,
    # Client
    DomeFeeEscrowClient,
    # Signing functions
    create_order_fee_authorization,
    create_performance_fee_authorization,
    sign_order_fee_authorization,
    sign_performance_fee_authorization,
    verify_order_fee_authorization_signature,
    verify_performance_fee_authorization_signature,
    create_dome_eip712_domain,
    # Constants
    MIN_ORDER_FEE,
    MIN_PERF_FEE,
    MAX_ORDER_FEE_BPS,
    MAX_PERF_FEE_BPS,
    # Utils
    format_usdc,
)


# Test wallet (DO NOT use in production)
TEST_PRIVATE_KEY = "0x" + "ab" * 32  # Deterministic test key
TEST_ACCOUNT = Account.from_key(TEST_PRIVATE_KEY)
TEST_ADDRESS = TEST_ACCOUNT.address

# Test escrow address (NOT a real deployment)
TEST_ESCROW_ADDRESS = "0x1234567890123456789012345678901234567890"

# Test chain ID (Polygon)
TEST_CHAIN_ID = 137


class TestUnifiedEIP712Domain:
    """Tests for EIP-712 domain creation."""

    def test_create_dome_eip712_domain(self):
        """Test domain creation."""
        domain = create_dome_eip712_domain(TEST_ESCROW_ADDRESS, TEST_CHAIN_ID)

        assert domain["name"] == "DomeFeeEscrow"
        assert domain["version"] == "1"
        assert domain["chainId"] == TEST_CHAIN_ID
        assert domain["verifyingContract"].lower() == TEST_ESCROW_ADDRESS.lower()

    def test_create_dome_eip712_domain_invalid_address(self):
        """Test that invalid address raises error."""
        with pytest.raises(ValueError, match="Invalid escrow address"):
            create_dome_eip712_domain("invalid", TEST_CHAIN_ID)


class TestOrderFeeAuthorization:
    """Tests for order fee authorization creation."""

    def test_create_order_fee_authorization(self):
        """Test basic order fee authorization creation."""
        order_id = "0x" + "ab" * 32

        auth = create_order_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            dome_amount=25000,      # $0.025
            affiliate_amount=5000,  # $0.005
            chain_id=TEST_CHAIN_ID,
            deadline_seconds=3600,
        )

        assert auth.order_id == order_id
        assert auth.payer == TEST_ADDRESS
        assert auth.dome_amount == 25000
        assert auth.affiliate_amount == 5000
        assert auth.chain_id == TEST_CHAIN_ID
        assert auth.deadline > int(time.time())
        assert auth.total_fee == 30000

    def test_create_order_fee_authorization_invalid_payer(self):
        """Test that invalid payer raises error."""
        with pytest.raises(ValueError, match="Invalid payer"):
            create_order_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer="invalid",
                dome_amount=25000,
                affiliate_amount=5000,
            )

    def test_create_order_fee_authorization_deadline_too_short(self):
        """Test that deadline too short raises error."""
        with pytest.raises(ValueError, match="Deadline too short"):
            create_order_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer=TEST_ADDRESS,
                dome_amount=25000,
                affiliate_amount=5000,
                deadline_seconds=30,  # < 60s minimum
            )

    def test_create_order_fee_authorization_zero_fee(self):
        """Test that zero total fee raises error."""
        with pytest.raises(ValueError, match="Total fee cannot be zero"):
            create_order_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer=TEST_ADDRESS,
                dome_amount=0,
                affiliate_amount=0,
            )

    def test_create_order_fee_authorization_fee_too_low(self):
        """Test that fee below minimum raises error."""
        with pytest.raises(ValueError, match="Total fee too low"):
            create_order_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer=TEST_ADDRESS,
                dome_amount=100,  # $0.0001 (below $0.01 minimum)
                affiliate_amount=0,
            )


class TestPerformanceFeeAuthorization:
    """Tests for performance fee authorization creation."""

    def test_create_performance_fee_authorization(self):
        """Test basic performance fee authorization creation."""
        position_id = "0x" + "cd" * 32

        auth = create_performance_fee_authorization(
            position_id=position_id,
            payer=TEST_ADDRESS,
            expected_winnings=100_000_000,  # $100
            dome_amount=500_000,             # $0.50 (0.5%)
            affiliate_amount=100_000,        # $0.10 (0.1%)
            chain_id=TEST_CHAIN_ID,
            deadline_seconds=3600,
        )

        assert auth.position_id == position_id
        assert auth.payer == TEST_ADDRESS
        assert auth.expected_winnings == 100_000_000
        assert auth.dome_amount == 500_000
        assert auth.affiliate_amount == 100_000
        assert auth.chain_id == TEST_CHAIN_ID
        assert auth.deadline > int(time.time())
        assert auth.total_fee == 600_000

    def test_create_performance_fee_authorization_fee_too_low(self):
        """Test that fee below minimum raises error."""
        with pytest.raises(ValueError, match="Total fee too low"):
            create_performance_fee_authorization(
                position_id="0x" + "cd" * 32,
                payer=TEST_ADDRESS,
                expected_winnings=100_000_000,
                dome_amount=50_000,  # $0.05 (below $0.10 minimum)
                affiliate_amount=0,
            )

    def test_create_performance_fee_authorization_zero_winnings(self):
        """Test that zero expected winnings raises error."""
        with pytest.raises(ValueError, match="Expected winnings must be positive"):
            create_performance_fee_authorization(
                position_id="0x" + "cd" * 32,
                payer=TEST_ADDRESS,
                expected_winnings=0,
                dome_amount=500_000,
                affiliate_amount=100_000,
            )


class TestOrderFeeSigning:
    """Tests for order fee EIP-712 signing."""

    def test_sign_order_fee_authorization(self):
        """Test order fee authorization signing."""
        order_id = "0x" + "ab" * 32
        auth = create_order_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            dome_amount=25000,
            affiliate_amount=5000,
            chain_id=TEST_CHAIN_ID,
        )

        signed = sign_order_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=TEST_ESCROW_ADDRESS,
            auth=auth,
        )

        assert isinstance(signed, SignedOrderFeeAuthorization)
        assert signed.signature is not None
        assert len(signed.signature) > 0
        assert signed.order_id == auth.order_id
        assert signed.dome_amount == auth.dome_amount
        assert signed.affiliate_amount == auth.affiliate_amount
        assert signed.chain_id == auth.chain_id

    def test_verify_order_fee_authorization_signature(self):
        """Test order fee signature verification."""
        order_id = "0x" + "ab" * 32
        auth = create_order_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            dome_amount=25000,
            affiliate_amount=5000,
            chain_id=TEST_CHAIN_ID,
        )

        signed = sign_order_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=TEST_ESCROW_ADDRESS,
            auth=auth,
        )

        # Verify with correct signer
        assert verify_order_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=TEST_ESCROW_ADDRESS,
            expected_signer=TEST_ADDRESS,
        ) is True

        # Verify with wrong signer
        wrong_address = Account.create().address
        assert verify_order_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=TEST_ESCROW_ADDRESS,
            expected_signer=wrong_address,
        ) is False


class TestPerformanceFeeSigning:
    """Tests for performance fee EIP-712 signing."""

    def test_sign_performance_fee_authorization(self):
        """Test performance fee authorization signing."""
        position_id = "0x" + "cd" * 32
        auth = create_performance_fee_authorization(
            position_id=position_id,
            payer=TEST_ADDRESS,
            expected_winnings=100_000_000,
            dome_amount=500_000,
            affiliate_amount=100_000,
            chain_id=TEST_CHAIN_ID,
        )

        signed = sign_performance_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=TEST_ESCROW_ADDRESS,
            auth=auth,
        )

        assert isinstance(signed, SignedPerformanceFeeAuthorization)
        assert signed.signature is not None
        assert len(signed.signature) > 0
        assert signed.position_id == auth.position_id
        assert signed.expected_winnings == auth.expected_winnings
        assert signed.dome_amount == auth.dome_amount
        assert signed.affiliate_amount == auth.affiliate_amount
        assert signed.chain_id == auth.chain_id

    def test_verify_performance_fee_authorization_signature(self):
        """Test performance fee signature verification."""
        position_id = "0x" + "cd" * 32
        auth = create_performance_fee_authorization(
            position_id=position_id,
            payer=TEST_ADDRESS,
            expected_winnings=100_000_000,
            dome_amount=500_000,
            affiliate_amount=100_000,
            chain_id=TEST_CHAIN_ID,
        )

        signed = sign_performance_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=TEST_ESCROW_ADDRESS,
            auth=auth,
        )

        # Verify with correct signer
        assert verify_performance_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=TEST_ESCROW_ADDRESS,
            expected_signer=TEST_ADDRESS,
        ) is True

        # Verify with wrong signer
        wrong_address = Account.create().address
        assert verify_performance_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=TEST_ESCROW_ADDRESS,
            expected_signer=wrong_address,
        ) is False


class TestDomeFeeEscrowClient:
    """Tests for the DomeFeeEscrowClient."""

    def test_client_creation(self):
        """Test client creation."""
        client = DomeFeeEscrowClient(
            escrow_address=TEST_ESCROW_ADDRESS,
            chain_id=TEST_CHAIN_ID,
        )

        assert client.escrow_address == TEST_ESCROW_ADDRESS
        assert client.chain_id == TEST_CHAIN_ID

    def test_sign_order_fee_auth(self):
        """Test client order fee signing."""
        client = DomeFeeEscrowClient(
            escrow_address=TEST_ESCROW_ADDRESS,
            chain_id=TEST_CHAIN_ID,
        )

        order_id = "0x" + "ab" * 32
        auth, signature = client.sign_order_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            order_id=order_id,
            dome_amount=25000,
            affiliate_amount=5000,
        )

        assert auth.order_id == order_id
        assert auth.dome_amount == 25000
        assert auth.affiliate_amount == 5000
        assert auth.chain_id == TEST_CHAIN_ID
        assert signature is not None
        assert len(signature) > 0

    def test_sign_performance_fee_auth(self):
        """Test client performance fee signing."""
        client = DomeFeeEscrowClient(
            escrow_address=TEST_ESCROW_ADDRESS,
            chain_id=TEST_CHAIN_ID,
        )

        position_id = "0x" + "cd" * 32
        auth, signature = client.sign_performance_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            position_id=position_id,
            expected_winnings=100_000_000,
            dome_amount=500_000,
            affiliate_amount=100_000,
        )

        assert auth.position_id == position_id
        assert auth.expected_winnings == 100_000_000
        assert auth.dome_amount == 500_000
        assert auth.affiliate_amount == 100_000
        assert auth.chain_id == TEST_CHAIN_ID
        assert signature is not None
        assert len(signature) > 0


class TestFeeCalculation:
    """Tests for fee calculation methods."""

    def test_calculate_order_fees_basic(self):
        """Test basic order fee calculation."""
        fees = DomeFeeEscrowClient.calculate_order_fees(
            order_size=10_000_000,  # $10 USDC
            dome_fee_bps=25,        # 0.25%
            affiliate_fee_bps=5,    # 0.05%
        )

        assert fees.dome_fee == 25000       # $0.025
        assert fees.affiliate_fee == 5000   # $0.005
        assert fees.total_fee == 30000      # $0.03

    def test_calculate_order_fees_applies_minimum(self):
        """Test that minimum fee is applied when fee is too low."""
        # Very small order would result in fee below minimum
        fees = DomeFeeEscrowClient.calculate_order_fees(
            order_size=100_000,   # $0.10 USDC
            dome_fee_bps=25,      # 0.25% = $0.00025
            affiliate_fee_bps=5,  # 0.05% = $0.00005
        )

        # Should be scaled up to minimum
        assert fees.total_fee == MIN_ORDER_FEE  # $0.01

    def test_calculate_order_fees_no_affiliate(self):
        """Test order fee calculation with no affiliate."""
        fees = DomeFeeEscrowClient.calculate_order_fees(
            order_size=10_000_000,  # $10 USDC
            dome_fee_bps=25,        # 0.25%
            affiliate_fee_bps=0,    # No affiliate
        )

        assert fees.dome_fee == 25000
        assert fees.affiliate_fee == 0
        assert fees.total_fee == 25000

    def test_calculate_order_fees_exceeds_max_bps(self):
        """Test that exceeding max bps raises error."""
        with pytest.raises(ValueError, match="Dome fee rate too high"):
            DomeFeeEscrowClient.calculate_order_fees(
                order_size=10_000_000,
                dome_fee_bps=200,  # 2% > 1% max
                affiliate_fee_bps=5,
            )

        with pytest.raises(ValueError, match="Affiliate fee rate too high"):
            DomeFeeEscrowClient.calculate_order_fees(
                order_size=10_000_000,
                dome_fee_bps=25,
                affiliate_fee_bps=200,  # 2% > 1% max
            )

    def test_calculate_performance_fees_basic(self):
        """Test basic performance fee calculation."""
        fees = DomeFeeEscrowClient.calculate_performance_fees(
            winnings=100_000_000,   # $100 USDC winnings
            dome_fee_bps=500,       # 5%
            affiliate_fee_bps=100,  # 1%
        )

        assert fees.dome_fee == 5_000_000      # $5.00
        assert fees.affiliate_fee == 1_000_000 # $1.00
        assert fees.total_fee == 6_000_000     # $6.00

    def test_calculate_performance_fees_applies_minimum(self):
        """Test that minimum performance fee is applied."""
        # Small winnings would result in fee below minimum
        fees = DomeFeeEscrowClient.calculate_performance_fees(
            winnings=1_000_000,    # $1 USDC winnings
            dome_fee_bps=50,       # 0.5% = $0.005
            affiliate_fee_bps=10,  # 0.1% = $0.001
        )

        # Should be scaled up to minimum ($0.10)
        assert fees.total_fee == MIN_PERF_FEE

    def test_calculate_performance_fees_exceeds_max_bps(self):
        """Test that exceeding max performance bps raises error."""
        with pytest.raises(ValueError, match="Dome fee rate too high"):
            DomeFeeEscrowClient.calculate_performance_fees(
                winnings=100_000_000,
                dome_fee_bps=1500,  # 15% > 10% max
                affiliate_fee_bps=100,
            )


class TestEIP712Types:
    """Tests for EIP-712 type definitions."""

    def test_order_fee_authorization_types(self):
        """Test ORDER_FEE_AUTHORIZATION_TYPES matches contract."""
        types = ORDER_FEE_AUTHORIZATION_TYPES["OrderFeeAuthorization"]

        # Verify field order and types match contract
        expected_fields = [
            ("orderId", "bytes32"),
            ("payer", "address"),
            ("domeAmount", "uint256"),
            ("affiliateAmount", "uint256"),
            ("chainId", "uint256"),
            ("deadline", "uint256"),
        ]

        assert len(types) == len(expected_fields)
        for i, (name, typ) in enumerate(expected_fields):
            assert types[i]["name"] == name
            assert types[i]["type"] == typ

    def test_performance_fee_authorization_types(self):
        """Test PERFORMANCE_FEE_AUTHORIZATION_TYPES matches contract."""
        types = PERFORMANCE_FEE_AUTHORIZATION_TYPES["PerformanceFeeAuthorization"]

        # Verify field order and types match contract
        expected_fields = [
            ("positionId", "bytes32"),
            ("payer", "address"),
            ("expectedWinnings", "uint256"),
            ("domeAmount", "uint256"),
            ("affiliateAmount", "uint256"),
            ("chainId", "uint256"),
            ("deadline", "uint256"),
        ]

        assert len(types) == len(expected_fields)
        for i, (name, typ) in enumerate(expected_fields):
            assert types[i]["name"] == name
            assert types[i]["type"] == typ


class TestIntegration:
    """Integration tests for the full unified escrow flow."""

    def test_full_order_fee_flow(self):
        """Test the complete order fee flow."""
        client = DomeFeeEscrowClient(
            escrow_address=TEST_ESCROW_ADDRESS,
            chain_id=TEST_CHAIN_ID,
        )

        # 1. Calculate fees
        order_size = 10_000_000  # $10 USDC
        fees = client.calculate_order_fees(
            order_size=order_size,
            dome_fee_bps=25,        # 0.25%
            affiliate_fee_bps=10,   # 0.10%
        )

        # 2. Sign authorization
        order_id = "0x" + "ab" * 32
        auth, signature = client.sign_order_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            order_id=order_id,
            dome_amount=fees.dome_fee,
            affiliate_amount=fees.affiliate_fee,
        )

        # 3. Verify
        signed_auth = SignedOrderFeeAuthorization(
            order_id=auth.order_id,
            payer=auth.payer,
            dome_amount=auth.dome_amount,
            affiliate_amount=auth.affiliate_amount,
            chain_id=auth.chain_id,
            deadline=auth.deadline,
            signature=signature,
        )

        assert client.verify_order_fee_signature(signed_auth, TEST_ADDRESS)

        print(f"\nOrder fee flow test passed:")
        print(f"  Order Size: ${format_usdc(order_size)} USDC")
        print(f"  Dome Fee: ${format_usdc(fees.dome_fee)} USDC")
        print(f"  Affiliate Fee: ${format_usdc(fees.affiliate_fee)} USDC")
        print(f"  Total Fee: ${format_usdc(fees.total_fee)} USDC")
        print(f"  Chain ID: {auth.chain_id}")
        print(f"  Signature: {signature[:20]}...")

    def test_full_performance_fee_flow(self):
        """Test the complete performance fee flow."""
        client = DomeFeeEscrowClient(
            escrow_address=TEST_ESCROW_ADDRESS,
            chain_id=TEST_CHAIN_ID,
        )

        # 1. Calculate fees on winnings
        winnings = 100_000_000  # $100 USDC
        fees = client.calculate_performance_fees(
            winnings=winnings,
            dome_fee_bps=500,       # 5%
            affiliate_fee_bps=100,  # 1%
        )

        # 2. Sign authorization
        position_id = "0x" + "cd" * 32
        auth, signature = client.sign_performance_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            position_id=position_id,
            expected_winnings=winnings,
            dome_amount=fees.dome_fee,
            affiliate_amount=fees.affiliate_fee,
        )

        # 3. Verify
        signed_auth = SignedPerformanceFeeAuthorization(
            position_id=auth.position_id,
            payer=auth.payer,
            expected_winnings=auth.expected_winnings,
            dome_amount=auth.dome_amount,
            affiliate_amount=auth.affiliate_amount,
            chain_id=auth.chain_id,
            deadline=auth.deadline,
            signature=signature,
        )

        assert client.verify_performance_fee_signature(signed_auth, TEST_ADDRESS)

        print(f"\nPerformance fee flow test passed:")
        print(f"  Expected Winnings: ${format_usdc(winnings)} USDC")
        print(f"  Dome Fee: ${format_usdc(fees.dome_fee)} USDC (5%)")
        print(f"  Affiliate Fee: ${format_usdc(fees.affiliate_fee)} USDC (1%)")
        print(f"  Total Fee: ${format_usdc(fees.total_fee)} USDC")
        print(f"  Net Winnings: ${format_usdc(winnings - fees.total_fee)} USDC")
        print(f"  Chain ID: {auth.chain_id}")
        print(f"  Signature: {signature[:20]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
