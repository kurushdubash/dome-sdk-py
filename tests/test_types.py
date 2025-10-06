"""Tests for type definitions."""

import pytest

from dome_api_sdk.types import (
    ApiError,
    CandlestickAskBid,
    CandlestickData,
    CandlestickPrice,
    GetMarketPriceParams,
    KalshiMarket,
    MarketPriceResponse,
    MatchingMarketsResponse,
    Order,
    OrdersResponse,
    Pagination,
    PnLDataPoint,
    PolymarketMarket,
    RequestConfig,
    ValidationError,
    WalletPnLResponse,
)


class TestMarketPriceResponse:
    """Test cases for MarketPriceResponse."""

    def test_creation(self) -> None:
        """Test creating MarketPriceResponse."""
        response = MarketPriceResponse(price=0.5, at_time=1234567890)
        assert response.price == 0.5
        assert response.at_time == 1234567890

    def test_frozen_dataclass(self) -> None:
        """Test that MarketPriceResponse is immutable."""
        response = MarketPriceResponse(price=0.5, at_time=1234567890)

        with pytest.raises(AttributeError):
            response.price = 0.6  # type: ignore


class TestGetMarketPriceParams:
    """Test cases for GetMarketPriceParams."""

    def test_required_fields(self) -> None:
        """Test required fields."""
        params = GetMarketPriceParams(token_id="123")
        assert params["token_id"] == "123"

    def test_optional_fields(self) -> None:
        """Test optional fields."""
        params = GetMarketPriceParams(token_id="123", at_time=1234567890)
        assert params["token_id"] == "123"
        assert params["at_time"] == 1234567890


class TestCandlestickTypes:
    """Test cases for candlestick types."""

    def test_candlestick_price(self) -> None:
        """Test CandlestickPrice creation."""
        price = CandlestickPrice(
            open=0.1,
            high=0.2,
            low=0.05,
            close=0.15,
            open_dollars="0.10",
            high_dollars="0.20",
            low_dollars="0.05",
            close_dollars="0.15",
            mean=0.125,
            mean_dollars="0.125",
            previous=0.1,
            previous_dollars="0.10",
        )
        assert price.open == 0.1
        assert price.high == 0.2

    def test_candlestick_ask_bid(self) -> None:
        """Test CandlestickAskBid creation."""
        ask_bid = CandlestickAskBid(
            open=0.1,
            close=0.15,
            high=0.2,
            low=0.05,
            open_dollars="0.10",
            close_dollars="0.15",
            high_dollars="0.20",
            low_dollars="0.05",
        )
        assert ask_bid.open == 0.1
        assert ask_bid.close == 0.15

    def test_candlestick_data(self) -> None:
        """Test CandlestickData creation."""
        price = CandlestickPrice(
            open=0.1,
            high=0.2,
            low=0.05,
            close=0.15,
            open_dollars="0.10",
            high_dollars="0.20",
            low_dollars="0.05",
            close_dollars="0.15",
            mean=0.125,
            mean_dollars="0.125",
            previous=0.1,
            previous_dollars="0.10",
        )
        ask_bid = CandlestickAskBid(
            open=0.1,
            close=0.15,
            high=0.2,
            low=0.05,
            open_dollars="0.10",
            close_dollars="0.15",
            high_dollars="0.20",
            low_dollars="0.05",
        )

        data = CandlestickData(
            end_period_ts=1234567890,
            open_interest=1000,
            price=price,
            volume=500,
            yes_ask=ask_bid,
            yes_bid=ask_bid,
        )
        assert data.end_period_ts == 1234567890
        assert data.open_interest == 1000


class TestWalletTypes:
    """Test cases for wallet types."""

    def test_pnl_data_point(self) -> None:
        """Test PnLDataPoint creation."""
        point = PnLDataPoint(timestamp=1234567890, pnl_to_date=100.5)
        assert point.timestamp == 1234567890
        assert point.pnl_to_date == 100.5

    def test_wallet_pnl_response(self) -> None:
        """Test WalletPnLResponse creation."""
        point = PnLDataPoint(timestamp=1234567890, pnl_to_date=100.5)
        response = WalletPnLResponse(
            granularity="day",
            start_time=1234567890,
            end_time=1234567890,
            wallet_address="0x123",
            pnl_over_time=[point],
        )
        assert response.granularity == "day"
        assert len(response.pnl_over_time) == 1


class TestOrderTypes:
    """Test cases for order types."""

    def test_order(self) -> None:
        """Test Order creation."""
        order = Order(
            token_id="123",
            side="BUY",
            market_slug="test-market",
            condition_id="0x456",
            shares=1000,
            shares_normalized=1.0,
            price=0.5,
            tx_hash="0x789",
            title="Test Market",
            timestamp=1234567890,
            order_hash="0xabc",
            user="0xdef",
        )
        assert order.token_id == "123"
        assert order.side == "BUY"

    def test_pagination(self) -> None:
        """Test Pagination creation."""
        pagination = Pagination(limit=50, offset=0, total=100, has_more=True)
        assert pagination.limit == 50
        assert pagination.has_more is True

    def test_orders_response(self) -> None:
        """Test OrdersResponse creation."""
        order = Order(
            token_id="123",
            side="BUY",
            market_slug="test",
            condition_id="0x456",
            shares=1000,
            shares_normalized=1.0,
            price=0.5,
            tx_hash="0x789",
            title="Test",
            timestamp=1234567890,
            order_hash="0xabc",
            user="0xdef",
        )
        pagination = Pagination(limit=50, offset=0, total=100, has_more=True)

        response = OrdersResponse(orders=[order], pagination=pagination)
        assert len(response.orders) == 1
        assert response.pagination.total == 100


class TestMatchingMarketsTypes:
    """Test cases for matching markets types."""

    def test_kalshi_market(self) -> None:
        """Test KalshiMarket creation."""
        market = KalshiMarket(
            platform="KALSHI",
            event_ticker="TEST-TICKER",
            market_tickers=["TICKER1", "TICKER2"],
        )
        assert market.platform == "KALSHI"
        assert market.event_ticker == "TEST-TICKER"

    def test_polymarket_market(self) -> None:
        """Test PolymarketMarket creation."""
        market = PolymarketMarket(
            platform="POLYMARKET", market_slug="test-market", token_ids=["123", "456"]
        )
        assert market.platform == "POLYMARKET"
        assert market.market_slug == "test-market"

    def test_matching_markets_response(self) -> None:
        """Test MatchingMarketsResponse creation."""
        kalshi_market = KalshiMarket(
            platform="KALSHI", event_ticker="TEST-TICKER", market_tickers=["TICKER1"]
        )

        response = MatchingMarketsResponse(markets={"test-key": [kalshi_market]})
        assert "test-key" in response.markets
        assert len(response.markets["test-key"]) == 1


class TestErrorTypes:
    """Test cases for error types."""

    def test_api_error(self) -> None:
        """Test ApiError creation."""
        error = ApiError(error="BAD_REQUEST", message="Invalid parameters")
        assert error.error == "BAD_REQUEST"
        assert error.message == "Invalid parameters"

    def test_validation_error(self) -> None:
        """Test ValidationError creation."""
        error = ValidationError(
            error="VALIDATION_ERROR",
            message="Missing required field",
            required="token_id",
        )
        assert error.error == "VALIDATION_ERROR"
        assert error.required == "token_id"


class TestRequestConfig:
    """Test cases for RequestConfig."""

    def test_request_config(self) -> None:
        """Test RequestConfig creation."""
        config = RequestConfig(timeout=60.0, headers={"Custom": "Header"})
        assert config["timeout"] == 60.0
        assert config["headers"]["Custom"] == "Header"
