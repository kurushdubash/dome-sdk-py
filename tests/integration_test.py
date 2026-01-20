#!/usr/bin/env python3
"""
Integration test script for the Dome SDK

This script makes live calls to the real Dome API endpoints to verify
that the SDK works correctly with actual data.

Usage:
  python -m tests.integration_test YOUR_API_KEY
  or
  python tests/integration_test.py YOUR_API_KEY
"""

import asyncio
import json
import sys
from typing import Any, Callable, Dict, List, Optional

from dome_api_sdk import DomeClient, WebSocketOrderEvent


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []


async def run_integration_test(api_key: str) -> None:
    print("🚀 Starting Dome SDK Integration Test...\n")

    dome = DomeClient({"api_key": api_key})

    test_results = TestResults()

    # Helper function to run a test
    async def run_test(
        test_name: str,
        test_fn: Callable[[], Any],
        validate_response: Optional[Callable[[Any], None]] = None,
    ) -> None:
        try:
            print(f"📋 Testing: {test_name}")
            result = (
                await test_fn() if asyncio.iscoroutinefunction(test_fn) else test_fn()
            )

            # Validate that response has values
            if validate_response:
                validate_response(result)
            else:
                # Default validation: check that result is not null/undefined
                if result is None:
                    raise ValueError("Response is null or undefined")

            print(f"✅ PASSED: {test_name}")
            result_str = json.dumps(result, default=str, indent=2)[:200]
            print(f"   Response: {result_str}...\n")
            test_results.passed += 1
        except Exception as error:
            print(f"❌ FAILED: {test_name}")
            error_message = str(error) if isinstance(error, Exception) else str(error)
            print(f"   Error: {error_message}\n")
            test_results.failed += 1
            test_results.errors.append(f"{test_name}: {error_message}")

    # Test data - using provided base values
    test_token_id = (
        "56369772478534954338683665819559528414197495274302917800610633957542171787417"
    )
    test_condition_id = (
        "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57"
    )
    test_wallet_address = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
    test_market_slug = "bitcoin-up-or-down-july-25-8pm-et"
    test_start_time = 1760470000000  # milliseconds
    test_end_time = 1760480000000  # milliseconds
    test_start_time_seconds = test_start_time // 1000
    test_end_time_seconds = test_end_time // 1000

    # Kalshi test data
    test_market_ticker = "KXMAYORNYCPARTY-25-D"
    test_event_ticker = "KXMAYORNYCPARTY-25"
    test_kalshi_trades_ticker = "KXNFLGAME-25NOV09PITLAC-PIT"
    test_kalshi_market_with_special_chars = "538APPROVE-22AUG03-B38.4"

    # Matching markets test data
    test_matching_market_slug = "nfl-ari-den-2025-08-16"
    test_matching_event_ticker = "KXNFLGAME-25AUG16ARIDEN"

    # Crypto prices test data
    test_binance_currency = "btcusdt"
    test_chainlink_currency = "eth/usd"
    test_crypto_start_time = 1766130000000
    test_crypto_end_time = 1766131000000

    # ===== POLYMARKET MARKET ENDPOINTS =====
    print("📊 Testing Polymarket Market Endpoints...\n")

    def validate_market_price_current(result):
        if not isinstance(result.price, (int, float)):
            raise ValueError("Response must have price as number")
        if not isinstance(result.at_time, int):
            raise ValueError("Response must have at_time as number")
        if result.price < 0 or result.price > 1:
            raise ValueError("Price must be between 0 and 1")

    await run_test(
        "Polymarket: Get Market Price (current)",
        lambda: dome.polymarket.markets.get_market_price({"token_id": test_token_id}),
        validate_market_price_current,
    )

    def validate_market_price_historical(result):
        if not isinstance(result.price, (int, float)):
            raise ValueError("Response must have price as number")
        if not isinstance(result.at_time, int):
            raise ValueError("Response must have at_time as number")

    await run_test(
        "Polymarket: Get Market Price (historical)",
        lambda: dome.polymarket.markets.get_market_price(
            {"token_id": test_token_id, "at_time": test_start_time_seconds}
        ),
        validate_market_price_historical,
    )

    def validate_candlesticks(result):
        if not hasattr(result, "candlesticks") or not isinstance(
            result.candlesticks, list
        ):
            raise ValueError("Response must have candlesticks array")

    await run_test(
        "Polymarket: Get Candlesticks (1 hour intervals)",
        lambda: dome.polymarket.markets.get_candlesticks(
            {
                "condition_id": test_condition_id,
                "start_time": test_start_time_seconds,
                "end_time": test_end_time_seconds,
                "interval": 60,  # 1 hour
            }
        ),
        validate_candlesticks,
    )

    await run_test(
        "Polymarket: Get Candlesticks (1 day intervals)",
        lambda: dome.polymarket.markets.get_candlesticks(
            {
                "condition_id": test_condition_id,
                "start_time": test_start_time_seconds,
                "end_time": test_end_time_seconds,
                "interval": 1440,  # 1 day
            }
        ),
        validate_candlesticks,
    )

    def validate_orderbooks(result):
        if not hasattr(result, "snapshots") or not isinstance(result.snapshots, list):
            raise ValueError("Response must have snapshots array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")
        if len(result.snapshots) > 0:
            snapshot = result.snapshots[0]
            if not hasattr(snapshot, "asks") or not isinstance(snapshot.asks, list):
                raise ValueError("Snapshot must have asks array")
            if not hasattr(snapshot, "bids") or not isinstance(snapshot.bids, list):
                raise ValueError("Snapshot must have bids array")

    await run_test(
        "Polymarket: Get Orderbooks",
        lambda: dome.polymarket.markets.get_orderbooks(
            {
                "token_id": test_token_id,
                "start_time": test_start_time,
                "end_time": test_end_time,
                "limit": 10,
            }
        ),
        validate_orderbooks,
    )

    def validate_markets_by_slug(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, list):
            raise ValueError("Response must have markets array")
        if len(result.markets) == 0:
            raise ValueError("Markets array should not be empty")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")

    await run_test(
        "Polymarket: Get Markets (by slug)",
        lambda: dome.polymarket.markets.get_markets(
            {"market_slug": [test_market_slug], "limit": 10}
        ),
        validate_markets_by_slug,
    )

    # Comprehensive validation test for markets endpoint
    await run_test(
        "Polymarket: Get Markets - Full Field Validation",
        lambda: dome.polymarket.markets.get_markets(
            {
                "market_slug": [
                    "bitcoin-up-or-down-july-25-8pm-et",
                    "nfl-ari-den-2025-08-16",
                ],
                "limit": 10,
            }
        ),
        lambda response: _validate_markets_response(response),
    )

    await run_test(
        "Polymarket: Get Markets (by condition ID)",
        lambda: dome.polymarket.markets.get_markets(
            {"condition_id": [test_condition_id], "limit": 10}
        ),
    )

    await run_test(
        "Polymarket: Get Markets (with filters)",
        lambda: dome.polymarket.markets.get_markets({"status": "open", "limit": 20}),
    )

    # ===== POLYMARKET WALLET ENDPOINTS =====
    print("💰 Testing Polymarket Wallet Endpoints...\n")

    def validate_wallet(result):
        if not isinstance(result.eoa, str) or not result.eoa:
            raise ValueError("Response must have eoa as non-empty string")
        if not isinstance(result.proxy, str) or not result.proxy:
            raise ValueError("Response must have proxy as non-empty string")
        if not isinstance(result.wallet_type, str) or not result.wallet_type:
            raise ValueError("Response must have wallet_type as non-empty string")
        if result.wallet_metrics:
            if not isinstance(result.wallet_metrics.total_volume, (int, float)):
                raise ValueError("wallet_metrics.total_volume must be a number")
            if not isinstance(result.wallet_metrics.total_trades, int):
                raise ValueError("wallet_metrics.total_trades must be an integer")
            if not isinstance(result.wallet_metrics.total_markets, int):
                raise ValueError("wallet_metrics.total_markets must be an integer")

    await run_test(
        "Polymarket: Get Wallet",
        lambda: dome.polymarket.wallet.get_wallet(
            {"eoa": test_wallet_address, "with_metrics": True}
        ),
        validate_wallet,
    )

    def validate_wallet_pnl(result):
        if not isinstance(result.granularity, str):
            raise ValueError("Response must have granularity as string")
        if not hasattr(result, "pnl_over_time") or not isinstance(
            result.pnl_over_time, list
        ):
            raise ValueError("Response must have pnl_over_time array")
        if not isinstance(result.wallet_address, str):
            raise ValueError("Response must have wallet_address as string")

    await run_test(
        "Polymarket: Get Wallet PnL (daily granularity)",
        lambda: dome.polymarket.wallet.get_wallet_pnl(
            {
                "wallet_address": test_wallet_address,
                "granularity": "day",
                "start_time": test_start_time_seconds,
                "end_time": test_end_time_seconds,
            }
        ),
        validate_wallet_pnl,
    )

    def validate_wallet_pnl_all(result):
        if not isinstance(result.granularity, str):
            raise ValueError("Response must have granularity as string")
        if not hasattr(result, "pnl_over_time") or not isinstance(
            result.pnl_over_time, list
        ):
            raise ValueError("Response must have pnl_over_time array")

    await run_test(
        "Polymarket: Get Wallet PnL (all time)",
        lambda: dome.polymarket.wallet.get_wallet_pnl(
            {"wallet_address": test_wallet_address, "granularity": "all"}
        ),
        validate_wallet_pnl_all,
    )

    # ===== POLYMARKET ORDERS ENDPOINTS =====
    print("📋 Testing Polymarket Orders Endpoints...\n")

    def validate_orders(result):
        if not hasattr(result, "orders") or not isinstance(result.orders, list):
            raise ValueError("Response must have orders array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")
        if len(result.orders) > 0:
            order = result.orders[0]
            if not hasattr(order, "token_id"):
                raise ValueError("Order must have token_id")
            if not hasattr(order, "token_label"):
                raise ValueError("Order must have token_label")
            if not hasattr(order, "taker"):
                raise ValueError("Order must have taker")

    await run_test(
        "Polymarket: Get Orders (by market slug)",
        lambda: dome.polymarket.orders.get_orders(
            {"market_slug": test_market_slug, "limit": 10}
        ),
        validate_orders,
    )

    def validate_orders_basic(result):
        if not hasattr(result, "orders") or not isinstance(result.orders, list):
            raise ValueError("Response must have orders array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")

    await run_test(
        "Polymarket: Get Orders (by token ID)",
        lambda: dome.polymarket.orders.get_orders(
            {"token_id": test_token_id, "limit": 5}
        ),
        validate_orders_basic,
    )

    await run_test(
        "Polymarket: Get Orders (with time range)",
        lambda: dome.polymarket.orders.get_orders(
            {
                "market_slug": test_market_slug,
                "start_time": test_start_time_seconds,
                "end_time": test_end_time_seconds,
                "limit": 20,
            }
        ),
        validate_orders_basic,
    )

    await run_test(
        "Polymarket: Get Orders (by user)",
        lambda: dome.polymarket.orders.get_orders(
            {"user": test_wallet_address, "limit": 10}
        ),
        validate_orders_basic,
    )

    def validate_activity(result):
        if not hasattr(result, "activities") or not isinstance(result.activities, list):
            raise ValueError("Response must have activities array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")

    await run_test(
        "Polymarket: Get Activity (by user)",
        lambda: dome.polymarket.activity.get_activity(
            {"user": test_wallet_address, "limit": 10}
        ),
        validate_activity,
    )

    await run_test(
        "Polymarket: Get Activity (with time range)",
        lambda: dome.polymarket.activity.get_activity(
            {
                "user": test_wallet_address,
                "start_time": test_start_time_seconds,
                "end_time": test_end_time_seconds,
                "limit": 20,
            }
        ),
        validate_activity,
    )

    await run_test(
        "Polymarket: Get Activity (by market slug)",
        lambda: dome.polymarket.activity.get_activity(
            {
                "user": test_wallet_address,
                "market_slug": test_market_slug,
                "limit": 10,
            }
        ),
        validate_activity,
    )

    # ===== POLYMARKET WEBSOCKET ENDPOINTS =====
    print("🔌 Testing Polymarket WebSocket Endpoints...\n")

    async def test_websocket():
        test_user = "0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"
        ws = dome.polymarket.websocket

        # Connect to WebSocket
        await ws.connect()

        # Wait up to 30 seconds for an order event
        timeout = 30.0  # 30 seconds
        order_received = False
        received_event = None

        def on_order_event(event: WebSocketOrderEvent):
            nonlocal order_received, received_event
            if not order_received:
                order_received = True
                received_event = event
                print(
                    f"   ✅ Order received: {json.dumps({'token_id': event.data.token_id, 'side': event.data.side, 'market_slug': event.data.market_slug, 'user': event.data.user, 'timestamp': event.data.timestamp}, default=str)[:200]}..."
                )

        # Subscribe to orders for the test user
        subscription_id = await ws.subscribe(users=[test_user], on_event=on_order_event)

        print(f"   Subscribed with ID: {subscription_id}")

        try:
            # Wait for order event with timeout
            for _ in range(300):  # 30 seconds * 10 checks per second
                await asyncio.sleep(0.1)
                if order_received:
                    break

            if not order_received:
                raise TimeoutError(
                    f"No order events received within {timeout} seconds for user {test_user}"
                )

            if received_event is None:
                raise ValueError("Event received but data is None")

            return {
                "subscription_id": subscription_id,
                "order_received": True,
                "order": {
                    "token_id": received_event.data.token_id,
                    "side": received_event.data.side,
                    "market_slug": received_event.data.market_slug,
                    "user": received_event.data.user,
                    "timestamp": received_event.data.timestamp,
                },
            }
        finally:
            # Disconnect
            await ws.disconnect()

    await run_test(
        "Polymarket: WebSocket - Subscribe and receive order events", test_websocket
    )

    # ===== KALSHI ENDPOINTS =====
    print("🏈 Testing Kalshi Endpoints...\n")

    def validate_kalshi_markets(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, list):
            raise ValueError("Response must have markets array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")

    await run_test(
        "Kalshi: Get Markets (no filters)",
        lambda: dome.kalshi.markets.get_markets({"limit": 10}),
        validate_kalshi_markets,
    )

    await run_test(
        "Kalshi: Get Markets (by status)",
        lambda: dome.kalshi.markets.get_markets({"status": "open", "limit": 20}),
        validate_kalshi_markets,
    )

    await run_test(
        "Kalshi: Get Markets (by event ticker)",
        lambda: dome.kalshi.markets.get_markets(
            {"event_ticker": [test_event_ticker], "limit": 10}
        ),
        validate_kalshi_markets,
    )

    await run_test(
        "Kalshi: Get Markets (by market ticker)",
        lambda: dome.kalshi.markets.get_markets(
            {"market_ticker": [test_market_ticker], "limit": 10}
        ),
        validate_kalshi_markets,
    )

    def validate_kalshi_markets_special(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, list):
            raise ValueError("Response must have markets array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")
        if len(result.markets) > 0:
            market = result.markets[0]
            if not isinstance(market.market_ticker, str) or not market.market_ticker:
                raise ValueError("market.market_ticker must be a non-empty string")
            if "." not in market.market_ticker:
                raise ValueError(
                    "Market ticker should support special characters like '.'"
                )

    await run_test(
        "Kalshi: Get Markets (by market ticker with special characters)",
        lambda: dome.kalshi.markets.get_markets(
            {"market_ticker": [test_kalshi_market_with_special_chars], "limit": 10}
        ),
        validate_kalshi_markets_special,
    )

    def validate_kalshi_trades(result):
        if not hasattr(result, "trades") or not isinstance(result.trades, list):
            raise ValueError("Response must have trades array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")
        if len(result.trades) > 0:
            trade = result.trades[0]
            if not hasattr(trade, "trade_id"):
                raise ValueError("Trade must have trade_id")
            if not isinstance(trade.count, int):
                raise ValueError("Trade count must be an integer")
            if not isinstance(trade.yes_price, int):
                raise ValueError("Trade yes_price must be an integer")
            if not isinstance(trade.no_price, int):
                raise ValueError("Trade no_price must be an integer")

    await run_test(
        "Kalshi: Get Trades",
        lambda: dome.kalshi.markets.get_trades(
            {"ticker": test_kalshi_trades_ticker, "limit": 10}
        ),
        validate_kalshi_trades,
    )

    def validate_kalshi_orderbooks(result):
        if not hasattr(result, "snapshots") or not isinstance(result.snapshots, list):
            raise ValueError("Response must have snapshots array")
        if not hasattr(result, "pagination"):
            raise ValueError("Response must have pagination object")
        if len(result.snapshots) > 0:
            snapshot = result.snapshots[0]
            if not hasattr(snapshot, "orderbook"):
                raise ValueError("Snapshot must have orderbook object")
            if not isinstance(snapshot.orderbook.yes, list):
                raise ValueError("Orderbook must have yes array")
            if not isinstance(snapshot.orderbook.no, list):
                raise ValueError("Orderbook must have no array")

    await run_test(
        "Kalshi: Get Orderbooks",
        lambda: dome.kalshi.orderbooks.get_orderbooks(
            {
                "ticker": test_market_ticker,
                "start_time": test_start_time,
                "end_time": test_end_time,
                "limit": 10,
            }
        ),
        validate_kalshi_orderbooks,
    )

    # ===== MATCHING MARKETS ENDPOINTS =====
    print("🔗 Testing Matching Markets Endpoints...\n")

    def validate_matching_markets(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, dict):
            raise ValueError("Response must have markets object")
        if len(result.markets) == 0:
            raise ValueError("Markets object should not be empty")

    await run_test(
        "Matching Markets: Get by Polymarket slug",
        lambda: dome.matching_markets.get_matching_markets(
            {"polymarket_market_slug": [test_matching_market_slug]}
        ),
        validate_matching_markets,
    )

    def validate_matching_markets_basic(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, dict):
            raise ValueError("Response must have markets object")

    await run_test(
        "Matching Markets: Get by Kalshi ticker",
        lambda: dome.matching_markets.get_matching_markets(
            {"kalshi_event_ticker": [test_matching_event_ticker]}
        ),
        validate_matching_markets_basic,
    )

    await run_test(
        "Matching Markets: Get by sport and date (NFL)",
        lambda: dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "nfl", "date": "2025-08-16"}
        ),
    )

    await run_test(
        "Matching Markets: Get by sport and date (MLB)",
        lambda: dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "mlb", "date": "2025-08-16"}
        ),
    )

    await run_test(
        "Matching Markets: Get by sport and date (CFB)",
        lambda: dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "cfb", "date": "2025-09-14"}
        ),
    )

    await run_test(
        "Matching Markets: Get by sport and date (NBA)",
        lambda: dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "nba", "date": "2025-11-15"}
        ),
    )

    def validate_matching_markets_by_sport(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, dict):
            raise ValueError("Response must have markets object")
        if not isinstance(result.sport, str):
            raise ValueError("Response must have sport as string")
        if not isinstance(result.date, str):
            raise ValueError("Response must have date as string")

    await run_test(
        "Matching Markets: Get by sport and date (NHL)",
        lambda: dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "nhl", "date": "2025-10-20"}
        ),
        validate_matching_markets_by_sport,
    )

    def validate_matching_markets_by_sport_cbb(result):
        if not hasattr(result, "markets") or not isinstance(result.markets, dict):
            raise ValueError("Response must have markets object")
        if not isinstance(result.sport, str):
            raise ValueError("Response must have sport as string")

    await run_test(
        "Matching Markets: Get by sport and date (CBB)",
        lambda: dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "cbb", "date": "2025-12-20"}
        ),
        validate_matching_markets_by_sport_cbb,
    )

    # ===== CRYPTO PRICES ENDPOINTS =====
    print("💰 Testing Crypto Prices Endpoints...\n")

    def validate_crypto_prices(result):
        if not hasattr(result, "prices") or not isinstance(result.prices, list):
            raise ValueError("Response must have prices array")
        if len(result.prices) == 0:
            raise ValueError("Prices array should not be empty")
        price = result.prices[0]
        if not isinstance(price.symbol, str):
            raise ValueError("Price must have symbol as string")
        if not hasattr(price, "value"):
            raise ValueError("Price must have value")
        if not isinstance(price.timestamp, int):
            raise ValueError("Price must have timestamp as number")

    await run_test(
        "Crypto Prices: Get Binance Prices (latest)",
        lambda: dome.crypto_prices.binance.get_binance_prices(
            {"currency": test_binance_currency}
        ),
        validate_crypto_prices,
    )

    def validate_crypto_prices_with_total(result):
        if not hasattr(result, "prices") or not isinstance(result.prices, list):
            raise ValueError("Response must have prices array")
        if not isinstance(result.total, int):
            raise ValueError("Response must have total as number")

    await run_test(
        "Crypto Prices: Get Binance Prices (with time range)",
        lambda: dome.crypto_prices.binance.get_binance_prices(
            {
                "currency": test_binance_currency,
                "start_time": test_crypto_start_time,
                "end_time": test_crypto_end_time,
                "limit": 10,
            }
        ),
        validate_crypto_prices_with_total,
    )

    await run_test(
        "Crypto Prices: Get Chainlink Prices (latest)",
        lambda: dome.crypto_prices.chainlink.get_chainlink_prices(
            {"currency": test_chainlink_currency}
        ),
        validate_crypto_prices,
    )

    await run_test(
        "Crypto Prices: Get Chainlink Prices (with time range)",
        lambda: dome.crypto_prices.chainlink.get_chainlink_prices(
            {
                "currency": test_chainlink_currency,
                "start_time": test_crypto_start_time,
                "end_time": test_crypto_end_time,
                "limit": 10,
            }
        ),
        validate_crypto_prices_with_total,
    )

    # ===== SUMMARY =====
    print("📊 Integration Test Summary")
    print("=========================")
    print(f"✅ Passed: {test_results.passed}")
    print(f"❌ Failed: {test_results.failed}")
    total = test_results.passed + test_results.failed
    success_rate = (test_results.passed / total * 100) if total > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%\n")

    if test_results.errors:
        print("❌ Failed Tests:")
        for index, error in enumerate(test_results.errors, 1):
            print(f"   {index}. {error}")
        print("")

    if test_results.failed == 0:
        print(
            "🎉 All integration tests passed! The SDK is working correctly with the live API."
        )
    else:
        print("⚠️  Some tests failed. This might be due to:")
        print("   - Invalid test data (token IDs, wallet addresses, etc.)")
        print("   - API rate limiting")
        print("   - Network issues")
        print("   - API changes")
        print("")
        print(
            "💡 Try running the test again or check the specific error messages above."
        )

    # Exit with appropriate code
    sys.exit(1 if test_results.failed > 0 else 0)


def _validate_markets_response(response: Any) -> None:
    """Validate the markets response structure comprehensively."""
    if not hasattr(response, "markets") or not isinstance(response.markets, list):
        raise ValueError("Response must have markets array")

    if not hasattr(response, "pagination"):
        raise ValueError("Response must have pagination object")

    # Validate pagination fields
    pagination = response.pagination
    if not isinstance(pagination.limit, int):
        raise ValueError("pagination.limit must be a number")
    if not isinstance(pagination.offset, int):
        raise ValueError("pagination.offset must be a number")
    if not isinstance(pagination.total, int):
        raise ValueError("pagination.total must be a number")
    if not isinstance(pagination.has_more, bool):
        raise ValueError("pagination.has_more must be a boolean")

    # Validate each market in the response
    for market in response.markets:
        # Required string fields
        if not isinstance(market.market_slug, str) or not market.market_slug:
            raise ValueError("market.market_slug must be a non-empty string")
        if not isinstance(market.condition_id, str) or not market.condition_id:
            raise ValueError("market.condition_id must be a non-empty string")
        if not isinstance(market.title, str) or not market.title:
            raise ValueError("market.title must be a non-empty string")

        # Required number fields (timestamps)
        if not isinstance(market.start_time, int):
            raise ValueError("market.start_time must be a number")
        if not isinstance(market.end_time, int):
            raise ValueError("market.end_time must be a number")

        # Nullable timestamp fields
        if market.completed_time is not None and not isinstance(
            market.completed_time, int
        ):
            raise ValueError("market.completed_time must be a number or null")
        if market.close_time is not None and not isinstance(market.close_time, int):
            raise ValueError("market.close_time must be a number or null")
        if (
            market.market_slug == "nfl-ari-den-2025-08-16"
            and market.game_start_time is not None
            and not isinstance(market.game_start_time, str)
        ):
            raise ValueError("market.game_start_time must be a string or null")

        # Tags array
        if not isinstance(market.tags, list):
            raise ValueError("market.tags must be an array")
        for index, tag in enumerate(market.tags):
            if not isinstance(tag, str):
                raise ValueError(f"market.tags[{index}] must be a string")

        # Volume fields
        if not isinstance(market.volume_1_week, (int, float)):
            raise ValueError("market.volume_1_week must be a number")
        if not isinstance(market.volume_1_month, (int, float)):
            raise ValueError("market.volume_1_month must be a number")
        if not isinstance(market.volume_1_year, (int, float)):
            raise ValueError("market.volume_1_year must be a number")
        if not isinstance(market.volume_total, (int, float)):
            raise ValueError("market.volume_total must be a number")

        # String fields
        if not isinstance(market.resolution_source, str):
            raise ValueError("market.resolution_source must be a string")
        if not isinstance(market.image, str):
            raise ValueError("market.image must be a string")

        # Side objects
        if not hasattr(market, "side_a") or not isinstance(market.side_a, object):
            raise ValueError("market.side_a must be an object")
        if not isinstance(market.side_a.id, str) or not market.side_a.id:
            raise ValueError("market.side_a.id must be a non-empty string")
        if not isinstance(market.side_a.label, str) or not market.side_a.label:
            raise ValueError("market.side_a.label must be a non-empty string")

        if not hasattr(market, "side_b") or not isinstance(market.side_b, object):
            raise ValueError("market.side_b must be an object")
        if not isinstance(market.side_b.id, str) or not market.side_b.id:
            raise ValueError("market.side_b.id must be a non-empty string")
        if not isinstance(market.side_b.label, str) or not market.side_b.label:
            raise ValueError("market.side_b.label must be a non-empty string")

        # Winning side (nullable object)
        if (
            market.status == "closed"
            and market.winning_side is not None
            and isinstance(market.winning_side, str)
        ):
            raise ValueError("market.winning_side must be an object or null")

        # Status enum
        if market.status not in ["open", "closed"]:
            raise ValueError(
                f"market.status must be 'open' or 'closed', got: {market.status}"
            )


# Main execution
async def main() -> None:
    api_key = sys.argv[1] if len(sys.argv) > 1 else None

    if not api_key:
        print("❌ Error: API key is required")
        print("")
        print("Usage:")
        print("  python -m tests.integration_test YOUR_API_KEY")
        print("  or")
        print("  python tests/integration_test.py YOUR_API_KEY")
        print("")
        print("Example:")
        print("  python -m tests.integration_test dome_1234567890abcdef")
        sys.exit(1)

    try:
        await run_integration_test(api_key)
    except Exception as error:
        error_message = str(error) if isinstance(error, Exception) else str(error)
        print(f"💥 Fatal error during integration test: {error_message}")
        sys.exit(1)


# Run the test
if __name__ == "__main__":
    asyncio.run(main())
