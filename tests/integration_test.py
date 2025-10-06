#!/usr/bin/env python3
"""Integration test script for the Dome SDK.

This script makes live calls to the real Dome API endpoints to verify
that the SDK works correctly with actual data.

Usage:
    python -m dome_api_sdk.tests.integration_test YOUR_API_KEY
    or
    python tests/integration_test.py YOUR_API_KEY
"""

import asyncio
import sys
from typing import Dict, List

from dome_api_sdk import DomeClient


class TestResults:
    """Test results container."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []


async def run_integration_test(api_key: str) -> None:
    """Run the integration test suite."""
    print("🚀 Starting Dome SDK Integration Test...\n")

    async with DomeClient({"api_key": api_key}) as dome:
        test_results = TestResults()

        # Helper function to run a test
        async def run_test(test_name: str, test_fn) -> None:
            try:
                print(f"📋 Testing: {test_name}")
                result = await test_fn()
                print(f"✅ PASSED: {test_name}")
                print(f"   Response: {str(result)[:200]}...\n")
                test_results.passed += 1
            except Exception as error:
                print(f"❌ FAILED: {test_name}")
                error_message = str(error)
                print(f"   Error: {error_message}\n")
                test_results.failed += 1
                test_results.errors.append(f"{test_name}: {error_message}")

        # Test data - using real-looking IDs that might exist
        test_token_id = "58519484510520807142687824915233722607092670035910114837910294451210534222702"
        test_condition_id = "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57"
        test_wallet_address = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
        test_market_slug = "bitcoin-up-or-down-july-25-8pm-et"

        # ===== POLYMARKET MARKET ENDPOINTS =====
        print("📊 Testing Polymarket Market Endpoints...\n")

        await run_test("Polymarket: Get Market Price (current)", lambda: 
            dome.polymarket.markets.get_market_price({
                "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850",
            })
        )

        await run_test("Polymarket: Get Market Price (historical)", lambda:
            dome.polymarket.markets.get_market_price({
                "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850",
                "at_time": 1757334400
            })
        )

        await run_test("Polymarket: Get Candlesticks (1 hour intervals)", lambda:
            dome.polymarket.markets.get_candlesticks({
                "condition_id": test_condition_id,
                "start_time": int(asyncio.get_event_loop().time()) - 86400 * 7,  # 7 days ago
                "end_time": int(asyncio.get_event_loop().time()),  # now
                "interval": 60  # 1 hour
            })
        )

        await run_test("Polymarket: Get Candlesticks (1 day intervals)", lambda:
            dome.polymarket.markets.get_candlesticks({
                "condition_id": test_condition_id,
                "start_time": int(asyncio.get_event_loop().time()) - 86400 * 30,  # 30 days ago
                "end_time": int(asyncio.get_event_loop().time()),  # now
                "interval": 1440  # 1 day
            })
        )

        # ===== POLYMARKET ORDERS ENDPOINTS =====
        print("📋 Testing Polymarket Orders Endpoints...\n")

        await run_test("Polymarket: Get Orders (by market slug)", lambda:
            dome.polymarket.orders.get_orders({
                "market_slug": test_market_slug,
                "limit": 10
            })
        )

        await run_test("Polymarket: Get Orders (by token ID)", lambda:
            dome.polymarket.orders.get_orders({
                "token_id": test_token_id,
                "limit": 5
            })
        )

        await run_test("Polymarket: Get Orders (with time range)", lambda:
            dome.polymarket.orders.get_orders({
                "market_slug": test_market_slug,
                "start_time": int(asyncio.get_event_loop().time()) - 86400 * 7,  # 7 days ago
                "end_time": int(asyncio.get_event_loop().time()),  # now
                "limit": 20,
                "offset": 0
            })
        )

        await run_test("Polymarket: Get Orders (by user)", lambda:
            dome.polymarket.orders.get_orders({
                "user": test_wallet_address,
                "limit": 10
            })
        )

        # ===== MATCHING MARKETS ENDPOINTS =====
        print("🔗 Testing Matching Markets Endpoints...\n")

        await run_test("Matching Markets: Get by Polymarket slug", lambda:
            dome.matching_markets.get_matching_markets({
                "polymarket_market_slug": ["nfl-ari-den-2025-08-16"]
            })
        )

        await run_test("Matching Markets: Get by Kalshi ticker", lambda:
            dome.matching_markets.get_matching_markets({
                "kalshi_event_ticker": ["KXNFLGAME-25AUG16ARIDEN"]
            })
        )

        await run_test("Matching Markets: Get by sport and date (NFL)", lambda:
            dome.matching_markets.get_matching_markets_by_sport({
                "sport": "nfl",
                "date": "2025-08-16"
            })
        )

        await run_test("Matching Markets: Get by sport and date (MLB)", lambda:
            dome.matching_markets.get_matching_markets_by_sport({
                "sport": "mlb",
                "date": "2025-08-16"
            })
        )

        # ===== SUMMARY =====
        print("📊 Integration Test Summary")
        print("=========================")
        print(f"✅ Passed: {test_results.passed}")
        print(f"❌ Failed: {test_results.failed}")
        print(f"📈 Success Rate: {((test_results.passed / (test_results.passed + test_results.failed)) * 100):.1f}%\n")

        if test_results.errors:
            print("❌ Failed Tests:")
            for i, error in enumerate(test_results.errors, 1):
                print(f"   {i}. {error}")
            print("")

        if test_results.failed == 0:
            print("🎉 All integration tests passed! The SDK is working correctly with the live API.")
        else:
            print("⚠️  Some tests failed. This might be due to:")
            print("   - Invalid test data (token IDs, wallet addresses, etc.)")
            print("   - API rate limiting")
            print("   - Network issues")
            print("   - API changes")
            print("")
            print("💡 Try running the test again or check the specific error messages above.")

        # Exit with appropriate code
        sys.exit(1 if test_results.failed > 0 else 0)


async def main() -> None:
    """Main execution function."""
    if len(sys.argv) < 2:
        print("❌ Error: API key is required")
        print("")
        print("Usage:")
        print("  python -m dome_api_sdk.tests.integration_test YOUR_API_KEY")
        print("  or")
        print("  python tests/integration_test.py YOUR_API_KEY")
        print("")
        print("Example:")
        print("  python -m dome_api_sdk.tests.integration_test dome_1234567890abcdef")
        sys.exit(1)

    api_key = sys.argv[1]

    try:
        await run_integration_test(api_key)
    except Exception as error:
        print(f"💥 Fatal error during integration test: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
