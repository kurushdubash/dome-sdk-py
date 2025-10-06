"""Tests for the endpoint classes."""

from unittest.mock import patch

import pytest

from dome_api_sdk import DomeClient
from dome_api_sdk.types import (
    CandlesticksResponse,
    MarketPriceResponse,
    MatchingMarketsBySportResponse,
    MatchingMarketsResponse,
    OrdersResponse,
    WalletPnLResponse,
)


class TestMarketEndpoints:
    """Test cases for MarketEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    def test_get_market_price_success(self, client):
        """Test successful market price fetch."""
        mock_response = {
            "price": 0.215,
            "at_time": 1757008834,
        }

        with patch.object(client.polymarket.markets, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.polymarket.markets.get_market_price(
                {"token_id": "1234567890"}
            )

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/market-price/1234567890",
                {},
                None,
            )

            assert isinstance(result, MarketPriceResponse)
            assert result.price == 0.215
            assert result.at_time == 1757008834

    def test_get_market_price_with_at_time(self, client):
        """Test market price fetch with at_time parameter."""
        mock_response = {
            "price": 0.220,
            "at_time": 1757008834,
        }

        with patch.object(client.polymarket.markets, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.polymarket.markets.get_market_price(
                {"token_id": "1234567890", "at_time": 1757008834}
            )

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/market-price/1234567890",
                {"at_time": 1757008834},
                None,
            )

            assert isinstance(result, MarketPriceResponse)
            assert result.price == 0.220

    def test_get_candlesticks_success(self, client):
        """Test successful candlesticks fetch."""
        mock_response = {
            "candlesticks": [
                [
                    [
                        {
                            "end_period_ts": 1757008834,
                            "open_interest": 1000,
                            "price": 0.215,
                            "volume": 500,
                            "yes_ask": 0.220,
                            "yes_bid": 0.210,
                        }
                    ],
                    {"token_id": "1234567890"},
                ]
            ]
        }

        with patch.object(client.polymarket.markets, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.polymarket.markets.get_candlesticks(
                {
                    "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                    "start_time": 1640995200,
                    "end_time": 1672531200,
                    "interval": 60,
                }
            )

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/candlesticks/0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                {"start_time": 1640995200, "end_time": 1672531200, "interval": 60},
                None,
            )

            assert isinstance(result, CandlesticksResponse)
            assert len(result.candlesticks) == 1
            assert (
                len(result.candlesticks[0]) == 2
            )  # One CandlestickData and one TokenMetadata
            assert result.candlesticks[0][0].price == 0.215
            assert result.candlesticks[0][1].token_id == "1234567890"


class TestWalletEndpoints:
    """Test cases for WalletEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    def test_get_wallet_pnl_success(self, client):
        """Test successful wallet PnL fetch."""
        mock_response = {
            "granularity": "day",
            "start_time": 1726857600,
            "end_time": 1758316829,
            "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
            "pnl_over_time": [
                {"timestamp": 1726857600, "pnl_to_date": 100.50},
                {"timestamp": 1726944000, "pnl_to_date": 150.75},
            ],
        }

        with patch.object(client.polymarket.wallet, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.polymarket.wallet.get_wallet_pnl(
                {
                    "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                    "granularity": "day",
                    "start_time": 1726857600,
                    "end_time": 1758316829,
                }
            )

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/wallet/pnl/0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                {
                    "granularity": "day",
                    "start_time": "1726857600",
                    "end_time": "1758316829",
                },
                None,
            )

            assert isinstance(result, WalletPnLResponse)
            assert result.granularity == "day"
            assert result.wallet_address == "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
            assert len(result.pnl_over_time) == 2
            assert result.pnl_over_time[0].pnl_to_date == 100.50


class TestOrdersEndpoints:
    """Test cases for OrdersEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    def test_get_orders_success(self, client):
        """Test successful orders fetch."""
        mock_response = {
            "orders": [
                {
                    "token_id": "1234567890",
                    "side": "buy",
                    "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                    "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                    "shares": 100,
                    "shares_normalized": 0.1,
                    "price": 0.65,
                    "tx_hash": "0x1234567890abcdef",
                    "title": "Bitcoin Price Test",
                    "timestamp": 1640995200,
                    "order_hash": "0xabcdef1234567890",
                    "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                }
            ],
            "pagination": {"limit": 10, "offset": 0, "total": 1, "has_more": False},
        }

        with patch.object(client.polymarket.orders, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.polymarket.orders.get_orders(
                {
                    "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                    "limit": 10,
                    "offset": 0,
                }
            )

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/orders",
                {
                    "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                    "limit": "10",
                    "offset": "0",
                },
                None,
            )

            assert isinstance(result, OrdersResponse)
            assert len(result.orders) == 1
            assert result.orders[0].token_id == "1234567890"
            assert result.orders[0].side == "buy"
            assert result.pagination.total == 1
            assert result.pagination.has_more is False


class TestMatchingMarketsEndpoints:
    """Test cases for MatchingMarketsEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    def test_get_matching_markets_success(self, client):
        """Test successful matching markets fetch."""
        mock_response = {
            "markets": {
                "nfl-ari-den-2025-08-16": [
                    {
                        "platform": "POLYMARKET",
                        "market_slug": "nfl-ari-den-2025-08-16",
                        "token_ids": ["1234567890", "0987654321"],
                    },
                    {
                        "platform": "KALSHI",
                        "event_ticker": "KXNFLGAME-25AUG16ARIDEN",
                        "market_tickers": [
                            "KXNFLGAME-25AUG16ARIDEN-Y",
                            "KXNFLGAME-25AUG16ARIDEN-N",
                        ],
                    },
                ]
            }
        }

        with patch.object(client.matching_markets, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.matching_markets.get_matching_markets(
                {"polymarket_market_slug": ["nfl-ari-den-2025-08-16"]}
            )

            mock_request.assert_called_once_with(
                "GET",
                "/matching-markets/sports/",
                {"polymarket_market_slug": ["nfl-ari-den-2025-08-16"]},
                None,
            )

            assert isinstance(result, MatchingMarketsResponse)
            assert len(result.markets) == 1
            assert "nfl-ari-den-2025-08-16" in result.markets
            assert len(result.markets["nfl-ari-den-2025-08-16"]) == 2

    def test_get_matching_markets_by_sport_success(self, client):
        """Test successful matching markets by sport fetch."""
        mock_response = {
            "markets": {
                "nfl-ari-den-2025-08-16": [
                    {
                        "platform": "POLYMARKET",
                        "market_slug": "nfl-ari-den-2025-08-16",
                        "token_ids": ["1234567890", "0987654321"],
                    }
                ]
            },
            "sport": "nfl",
            "date": "2025-08-16",
        }

        with patch.object(client.matching_markets, "_make_request") as mock_request:
            mock_request.return_value = mock_response

            result = client.matching_markets.get_matching_markets_by_sport(
                {"sport": "nfl", "date": "2025-08-16"}
            )

            mock_request.assert_called_once_with(
                "GET",
                "/matching-markets/sports/nfl/",
                {"date": "2025-08-16"},
                None,
            )

            assert isinstance(result, MatchingMarketsBySportResponse)
            assert result.sport == "nfl"
            assert result.date == "2025-08-16"
            assert len(result.markets) == 1
