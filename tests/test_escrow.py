"""Tests for the escrow module."""

import time
import pytest
from eth_account import Account

from src.dome_api_sdk.escrow import (
    OrderParams,
    FeeAuthorization,
    SignedFeeAuthorization,
    generate_order_id,
    verify_order_id,
    create_fee_authorization,
    sign_fee_authorization,
    verify_fee_authorization_signature,
    format_usdc,
    parse_usdc,
    calculate_fee,
    calculate_order_size_usdc,
    ESCROW_CONTRACT_POLYGON,
    # V2 imports
    DomeFeeEscrowClient,
    OrderFeeAuthorization,
    SignedOrderFeeAuthorization,
    CalculatedFees,
    MIN_ORDER_FEE,
)


# Test wallet (DO NOT use in production)
TEST_PRIVATE_KEY = "0x" + "ab" * 32  # Deterministic test key
TEST_ACCOUNT = Account.from_key(TEST_PRIVATE_KEY)
TEST_ADDRESS = TEST_ACCOUNT.address


class TestOrderId:
    """Tests for order ID generation."""

    def test_generate_order_id_basic(self):
        """Test basic order ID generation."""
        params = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,  # $1 USDC
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )

        order_id = generate_order_id(params)

        assert order_id.startswith("0x")
        assert len(order_id) == 66  # 0x + 64 hex chars

    def test_generate_order_id_deterministic(self):
        """Test that order ID generation is deterministic."""
        params = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )

        order_id_1 = generate_order_id(params)
        order_id_2 = generate_order_id(params)

        assert order_id_1 == order_id_2

    def test_generate_order_id_different_timestamps(self):
        """Test that different timestamps produce different IDs."""
        params_1 = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )
        params_2 = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000001,  # 1ms different
            chain_id=137,
        )

        assert generate_order_id(params_1) != generate_order_id(params_2)

    def test_generate_order_id_different_users(self):
        """Test that different users produce different IDs."""
        other_address = Account.create().address

        params_1 = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )
        params_2 = OrderParams(
            user_address=other_address,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )

        assert generate_order_id(params_1) != generate_order_id(params_2)

    def test_generate_order_id_invalid_price(self):
        """Test that invalid price raises error."""
        params = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=1.5,  # Invalid: > 1
            timestamp=1700000000000,
            chain_id=137,
        )

        with pytest.raises(ValueError, match="Invalid price"):
            generate_order_id(params)

    def test_generate_order_id_invalid_address(self):
        """Test that invalid address raises error."""
        params = OrderParams(
            user_address="invalid",
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )

        with pytest.raises(ValueError, match="Invalid user_address"):
            generate_order_id(params)

    def test_verify_order_id(self):
        """Test order ID verification."""
        params = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345",
            side="buy",
            size=1_000_000,
            price=0.65,
            timestamp=1700000000000,
            chain_id=137,
        )

        order_id = generate_order_id(params)
        assert verify_order_id(order_id, params) is True

        # Modify params
        params.timestamp = 1700000000001
        assert verify_order_id(order_id, params) is False


class TestFeeAuthorization:
    """Tests for fee authorization creation."""

    def test_create_fee_authorization(self):
        """Test basic fee authorization creation."""
        order_id = "0x" + "ab" * 32

        fee_auth = create_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            fee_amount=2500,  # $0.0025
            deadline_seconds=3600,
        )

        assert fee_auth.order_id == order_id
        assert fee_auth.payer == TEST_ADDRESS
        assert fee_auth.fee_amount == 2500
        assert fee_auth.deadline > int(time.time())

    def test_create_fee_authorization_invalid_payer(self):
        """Test that invalid payer raises error."""
        with pytest.raises(ValueError, match="Invalid payer"):
            create_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer="invalid",
                fee_amount=2500,
            )

    def test_create_fee_authorization_deadline_too_short(self):
        """Test that deadline too short raises error."""
        with pytest.raises(ValueError, match="Deadline too short"):
            create_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer=TEST_ADDRESS,
                fee_amount=2500,
                deadline_seconds=30,  # < 60s minimum
            )

    def test_create_fee_authorization_deadline_too_long(self):
        """Test that deadline too long raises error."""
        with pytest.raises(ValueError, match="Deadline too long"):
            create_fee_authorization(
                order_id="0x" + "ab" * 32,
                payer=TEST_ADDRESS,
                fee_amount=2500,
                deadline_seconds=100000,  # > 24h maximum
            )


class TestSigning:
    """Tests for EIP-712 signing."""

    def test_sign_fee_authorization(self):
        """Test fee authorization signing."""
        order_id = "0x" + "ab" * 32
        fee_auth = create_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            fee_amount=2500,
        )

        signed = sign_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=ESCROW_CONTRACT_POLYGON,
            fee_auth=fee_auth,
            chain_id=137,
        )

        assert isinstance(signed, SignedFeeAuthorization)
        assert signed.signature is not None
        assert len(signed.signature) > 0

    def test_verify_fee_authorization_signature(self):
        """Test signature verification."""
        order_id = "0x" + "ab" * 32
        fee_auth = create_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            fee_amount=2500,
        )

        signed = sign_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=ESCROW_CONTRACT_POLYGON,
            fee_auth=fee_auth,
            chain_id=137,
        )

        # Verify with correct signer
        assert verify_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=ESCROW_CONTRACT_POLYGON,
            chain_id=137,
            expected_signer=TEST_ADDRESS,
        ) is True

        # Verify with wrong signer
        wrong_address = Account.create().address
        assert verify_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=ESCROW_CONTRACT_POLYGON,
            chain_id=137,
            expected_signer=wrong_address,
        ) is False


class TestUtils:
    """Tests for utility functions."""

    def test_format_usdc(self):
        """Test USDC formatting."""
        assert format_usdc(1_000_000) == "1"
        assert format_usdc(1_500_000) == "1.5"
        assert format_usdc(1_234_567) == "1.234567"
        assert format_usdc(100) == "0.0001"

    def test_parse_usdc(self):
        """Test USDC parsing."""
        assert parse_usdc(1.0) == 1_000_000
        assert parse_usdc(1.5) == 1_500_000
        assert parse_usdc(0.01) == 10_000
        assert parse_usdc(100) == 100_000_000

    def test_calculate_fee(self):
        """Test fee calculation."""
        # 0.25% of $100
        assert calculate_fee(100_000_000, 25) == 250_000  # $0.25

        # 0.25% of $1
        assert calculate_fee(1_000_000, 25) == 2500  # $0.0025

        # 1% of $10
        assert calculate_fee(10_000_000, 100) == 100_000  # $0.10

    def test_calculate_order_size_usdc(self):
        """Test order size calculation."""
        # 10 shares at $0.50 = $5
        assert calculate_order_size_usdc(10, 0.50) == 5_000_000

        # 100 shares at $0.65 = $65
        assert calculate_order_size_usdc(100, 0.65) == 65_000_000


class TestIntegration:
    """Integration tests for the full flow."""

    def test_full_escrow_flow(self):
        """Test the complete escrow flow: generate ID -> create auth -> sign."""
        # 1. Generate order ID
        timestamp = int(time.time() * 1000)
        params = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345678901234567890",
            side="buy",
            size=calculate_order_size_usdc(10, 0.65),  # 10 shares @ $0.65
            price=0.65,
            timestamp=timestamp,
            chain_id=137,
        )
        order_id = generate_order_id(params)

        # 2. Calculate fee
        fee_amount = calculate_fee(params.size, 25)  # 0.25%
        assert fee_amount > 0

        # 3. Create fee authorization
        fee_auth = create_fee_authorization(
            order_id=order_id,
            payer=TEST_ADDRESS,
            fee_amount=fee_amount,
            deadline_seconds=3600,
        )

        # 4. Sign fee authorization
        signed = sign_fee_authorization(
            private_key=TEST_PRIVATE_KEY,
            escrow_address=ESCROW_CONTRACT_POLYGON,
            fee_auth=fee_auth,
            chain_id=137,
        )

        # 5. Verify
        assert verify_order_id(order_id, params)
        assert verify_fee_authorization_signature(
            signed_auth=signed,
            escrow_address=ESCROW_CONTRACT_POLYGON,
            chain_id=137,
            expected_signer=TEST_ADDRESS,
        )

        print(f"\nFull flow test passed:")
        print(f"  Order ID: {order_id[:20]}...")
        print(f"  Fee: ${format_usdc(fee_amount)} USDC")
        print(f"  Deadline: {fee_auth.deadline}")
        print(f"  Signature: {signed.signature[:20]}...")


class TestDomeFeeEscrowClientOrderFees:
    """Tests for DomeFeeEscrowClient order fee signing (V2 split model)."""

    def setup_method(self):
        self.client = DomeFeeEscrowClient(
            escrow_address=ESCROW_CONTRACT_POLYGON,
            chain_id=137,
        )

    def test_sign_order_fee_auth(self):
        """Test order fee auth signing with split dome/affiliate amounts."""
        order_id = "0x" + "ab" * 32
        dome_amount = 200_000  # $0.20
        affiliate_amount = 50_000  # $0.05

        auth, signature = self.client.sign_order_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            order_id=order_id,
            dome_amount=dome_amount,
            affiliate_amount=affiliate_amount,
        )

        assert isinstance(auth, OrderFeeAuthorization)
        assert auth.order_id == order_id
        assert auth.dome_amount == dome_amount
        assert auth.affiliate_amount == affiliate_amount
        assert auth.chain_id == 137
        assert auth.deadline > int(time.time())
        assert len(signature) > 0

    def test_sign_and_verify_order_fee_auth(self):
        """Test round-trip: sign then verify order fee auth."""
        order_id = "0x" + "cd" * 32

        auth, signature = self.client.sign_order_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            order_id=order_id,
            dome_amount=140_000,
            affiliate_amount=35_000,
        )

        signed_auth = SignedOrderFeeAuthorization(
            order_id=auth.order_id,
            payer=auth.payer,
            dome_amount=auth.dome_amount,
            affiliate_amount=auth.affiliate_amount,
            chain_id=auth.chain_id,
            deadline=auth.deadline,
            signature=signature,
        )

        assert self.client.verify_order_fee_signature(
            signed_auth=signed_auth,
            expected_signer=TEST_ADDRESS,
        ) is True

        # Wrong signer should fail
        wrong_address = Account.create().address
        assert self.client.verify_order_fee_signature(
            signed_auth=signed_auth,
            expected_signer=wrong_address,
        ) is False

    def test_calculate_order_fees_split(self):
        """Test V2 fee calculation with split dome/affiliate amounts."""
        order_size = 100_000_000  # $100
        fees = DomeFeeEscrowClient.calculate_order_fees(
            order_size=order_size,
            dome_fee_bps=20,
            affiliate_fee_bps=5,
        )

        assert isinstance(fees, CalculatedFees)
        assert fees.dome_fee == 200_000  # $0.20 (20 bps)
        assert fees.affiliate_fee == 50_000  # $0.05 (5 bps)
        assert fees.total_fee == 250_000  # $0.25 total

    def test_calculate_order_fees_minimum_applied(self):
        """Test that minimum fee floor is enforced."""
        # Very small order where calculated fee < MIN_ORDER_FEE
        order_size = 10_000  # $0.01
        fees = DomeFeeEscrowClient.calculate_order_fees(
            order_size=order_size,
            dome_fee_bps=20,
            affiliate_fee_bps=5,
        )

        # Total should be at least MIN_ORDER_FEE
        assert fees.total_fee >= MIN_ORDER_FEE


class TestDomeFeeEscrowClientIntegration:
    """Integration tests for the full V2 escrow flow."""

    def test_full_v2_flow(self):
        """Test complete V2 flow: order ID -> split fees -> sign -> verify."""
        # 1. Generate order ID
        timestamp = int(time.time() * 1000)
        params = OrderParams(
            user_address=TEST_ADDRESS,
            market_id="12345678901234567890",
            side="buy",
            size=calculate_order_size_usdc(50, 0.70),  # 50 shares @ $0.70 = $35
            price=0.70,
            timestamp=timestamp,
            chain_id=137,
        )
        order_id = generate_order_id(params)

        # 2. Calculate split fees
        fees = DomeFeeEscrowClient.calculate_order_fees(
            order_size=params.size,
            dome_fee_bps=20,
            affiliate_fee_bps=5,
        )
        assert fees.dome_fee > 0
        assert fees.affiliate_fee > 0

        # 3. Sign with DomeFeeEscrowClient
        client = DomeFeeEscrowClient(
            escrow_address=ESCROW_CONTRACT_POLYGON,
            chain_id=137,
        )

        auth, signature = client.sign_order_fee_auth(
            private_key=TEST_PRIVATE_KEY,
            order_id=order_id,
            dome_amount=fees.dome_fee,
            affiliate_amount=fees.affiliate_fee,
        )

        # 4. Verify
        assert verify_order_id(order_id, params)

        signed_auth = SignedOrderFeeAuthorization(
            order_id=auth.order_id,
            payer=auth.payer,
            dome_amount=auth.dome_amount,
            affiliate_amount=auth.affiliate_amount,
            chain_id=auth.chain_id,
            deadline=auth.deadline,
            signature=signature,
        )
        assert client.verify_order_fee_signature(
            signed_auth=signed_auth,
            expected_signer=TEST_ADDRESS,
        )

        print(f"\nV2 full flow test passed:")
        print(f"  Order ID: {order_id[:20]}...")
        print(f"  Dome fee: ${format_usdc(fees.dome_fee)} USDC")
        print(f"  Affiliate fee: ${format_usdc(fees.affiliate_fee)} USDC")
        print(f"  Deadline: {auth.deadline}")
        print(f"  Signature: {signature[:20]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
