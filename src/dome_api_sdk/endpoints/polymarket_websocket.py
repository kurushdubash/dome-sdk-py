"""Polymarket WebSocket client for real-time order data."""

import asyncio
import json
import logging
import os
from typing import Callable, Dict, List, Optional, Tuple

import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed

from ..types import (
    ActiveSubscription,
    Order,
    SubscribeMessage,
    SubscriptionAcknowledgment,
    UnsubscribeMessage,
    WebSocketOrderEvent,
)

__all__ = ["PolymarketWebSocketClient"]

logger = logging.getLogger(__name__)


class PolymarketWebSocketClient:
    """WebSocket client for real-time Polymarket order data.

    Provides real-time order information from Polymarket via WebSocket with automatic
    reconnection and subscription management.

    Example:
        ```python
        import asyncio
        from dome_api_sdk import DomeClient

        async def on_order_event(event: WebSocketOrderEvent):
            print(f"New order: {event.data}")

        async def main():
            dome = DomeClient({"api_key": "your-api-key"})
            ws_client = dome.polymarket.websocket

            # Subscribe to orders for specific users
            await ws_client.subscribe(
                users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"],
                on_event=on_order_event
            )

            # Keep running
            await asyncio.sleep(60)

            # Unsubscribe
            subscriptions = ws_client.get_active_subscriptions()
            for sub in subscriptions:
                await ws_client.unsubscribe(sub.subscription_id)

        asyncio.run(main())
        ```
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the WebSocket client.

        Args:
            api_key: API key for authentication. If not provided, will use DOME_API_KEY env var.
        """
        self._api_key = api_key or os.getenv("DOME_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "API key is required. Provide it or set DOME_API_KEY env var."
            )

        self._ws_url = f"wss://ws.domeapi.io/{self._api_key}"
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._connected = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._base_reconnect_delay = 1.0  # Start with 1 second

        # Track subscriptions: subscription_id -> ActiveSubscription
        self._active_subscriptions: Dict[str, ActiveSubscription] = {}
        # Track pending subscriptions waiting for ack: request_id -> (SubscribeMessage, Event)
        self._pending_subscriptions: Dict[
            str, Tuple[SubscribeMessage, asyncio.Event]
        ] = {}
        # Track subscription_id -> request_id mapping for ack handling
        self._subscription_id_to_request_id: Dict[str, str] = {}

        # Event handler callback
        self._on_event: Optional[Callable[[WebSocketOrderEvent], None]] = None

    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        if self._connected and self._websocket:
            return

        try:
            self._websocket = await websockets.connect(self._ws_url)
            self._connected = True
            self._reconnect_attempts = 0
            self._base_reconnect_delay = 1.0
            logger.info("Connected to WebSocket server")

            # Start receiving messages
            self._receive_task = asyncio.create_task(self._receive_messages())

            # Re-subscribe to all active subscriptions
            await self._resubscribe_all()

        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self._websocket:
            await self._websocket.close()
            self._websocket = None

        self._connected = False
        logger.info("Disconnected from WebSocket server")

    async def subscribe(
        self,
        users: List[str],
        on_event: Optional[Callable[[WebSocketOrderEvent], None]] = None,
    ) -> str:
        """Subscribe to order events for specific users.

        Args:
            users: List of wallet addresses to track
            on_event: Optional callback function to handle order events.
                     If not provided, events will be queued and can be retrieved.

        Returns:
            The subscription ID assigned by the server

        Raises:
            ValueError: If the request fails
            RuntimeError: If not connected
        """
        if not self._connected or not self._websocket:
            await self.connect()

        if on_event:
            self._on_event = on_event

        subscribe_msg: SubscribeMessage = {
            "action": "subscribe",
            "platform": "polymarket",
            "version": 1,
            "type": "orders",
            "filters": {
                "users": users,
            },
        }

        # Store as pending until we get ack
        request_id = f"pending_{len(self._pending_subscriptions)}"
        ack_event = asyncio.Event()
        self._pending_subscriptions[request_id] = (subscribe_msg, ack_event)

        try:
            await self._websocket.send(json.dumps(subscribe_msg))
            logger.info(f"Sent subscription request for users: {users}")

            # Wait for acknowledgment (with timeout)
            subscription_id = await self._wait_for_subscription_ack(
                request_id, ack_event, timeout=10.0
            )

            # Move from pending to active
            if request_id in self._pending_subscriptions:
                del self._pending_subscriptions[request_id]
            if request_id in self._subscription_id_to_request_id.values():
                # Remove reverse mapping
                self._subscription_id_to_request_id = {
                    k: v
                    for k, v in self._subscription_id_to_request_id.items()
                    if v != request_id
                }

            self._active_subscriptions[subscription_id] = ActiveSubscription(
                subscription_id=subscription_id,
                request=subscribe_msg,
            )

            logger.info(f"Subscription confirmed: {subscription_id}")
            return subscription_id

        except asyncio.TimeoutError:
            if request_id in self._pending_subscriptions:
                del self._pending_subscriptions[request_id]
            raise ValueError("Subscription timeout: No acknowledgment received")
        except Exception as e:
            if request_id in self._pending_subscriptions:
                del self._pending_subscriptions[request_id]
            raise ValueError(f"Failed to subscribe: {e}")

    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from order events.

        Args:
            subscription_id: The subscription ID to unsubscribe from

        Raises:
            ValueError: If the subscription ID is not found or request fails
            RuntimeError: If not connected
        """
        if not self._connected or not self._websocket:
            raise RuntimeError("Not connected to WebSocket server")

        if subscription_id not in self._active_subscriptions:
            raise ValueError(f"Subscription ID not found: {subscription_id}")

        unsubscribe_msg: UnsubscribeMessage = {
            "action": "unsubscribe",
            "version": 1,
            "subscription_id": subscription_id,
        }

        try:
            await self._websocket.send(json.dumps(unsubscribe_msg))
            logger.info(f"Sent unsubscribe request for: {subscription_id}")

            # Remove from active subscriptions
            del self._active_subscriptions[subscription_id]

        except Exception as e:
            raise ValueError(f"Failed to unsubscribe: {e}")

    def get_active_subscriptions(self) -> List[ActiveSubscription]:
        """Get all active subscriptions.

        Returns:
            List of active subscription information
        """
        return list(self._active_subscriptions.values())

    async def _receive_messages(self) -> None:
        """Receive and process messages from the WebSocket."""
        if not self._websocket:
            return

        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        except ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self._connected = False
            await self._handle_disconnection()
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            self._connected = False
            await self._handle_disconnection()

    async def _handle_message(self, data: Dict) -> None:
        """Handle incoming WebSocket messages."""
        msg_type = data.get("type")

        if msg_type == "ack":
            # Handle subscription acknowledgment
            subscription_id = data.get("subscription_id")
            if subscription_id:
                # Find the pending subscription - we'll match the first pending one
                # since the server doesn't send back a request identifier
                for request_id, (pending_msg, ack_event) in list(
                    self._pending_subscriptions.items()
                ):
                    # Match the first pending subscription
                    self._subscription_id_to_request_id[subscription_id] = request_id
                    # Signal the waiting coroutine
                    ack_event.set()
                    # Store the subscription_id for the waiting coroutine
                    if not hasattr(self, "_ack_subscription_ids"):
                        self._ack_subscription_ids: Dict[str, str] = {}
                    self._ack_subscription_ids[request_id] = subscription_id
                    break

        elif msg_type == "event":
            # Handle order event
            subscription_id = data.get("subscription_id")
            order_data = data.get("data", {})

            if subscription_id and order_data:
                order = Order(
                    token_id=order_data["token_id"],
                    side=order_data["side"],
                    market_slug=order_data["market_slug"],
                    condition_id=order_data["condition_id"],
                    shares=order_data["shares"],
                    shares_normalized=order_data["shares_normalized"],
                    price=order_data["price"],
                    tx_hash=order_data["tx_hash"],
                    title=order_data["title"],
                    timestamp=order_data["timestamp"],
                    order_hash=order_data["order_hash"],
                    user=order_data["user"],
                )

                event = WebSocketOrderEvent(
                    type="event",
                    subscription_id=subscription_id,
                    data=order,
                )

                if self._on_event:
                    try:
                        self._on_event(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")

    async def _wait_for_subscription_ack(
        self, request_id: str, ack_event: asyncio.Event, timeout: float
    ) -> str:
        """Wait for subscription acknowledgment."""
        # Initialize the subscription_id storage if needed
        if not hasattr(self, "_ack_subscription_ids"):
            self._ack_subscription_ids: Dict[str, str] = {}

        try:
            await asyncio.wait_for(ack_event.wait(), timeout=timeout)
            subscription_id = self._ack_subscription_ids.get(request_id)
            if subscription_id:
                # Clean up
                del self._ack_subscription_ids[request_id]
                return subscription_id
            else:
                raise ValueError("Received ack but no subscription_id")
        except asyncio.TimeoutError:
            # Clean up on timeout
            if request_id in self._ack_subscription_ids:
                del self._ack_subscription_ids[request_id]
            raise

    async def _resubscribe_all(self) -> None:
        """Re-subscribe to all active subscriptions after reconnection."""
        if not self._active_subscriptions:
            return

        logger.info(
            f"Re-subscribing to {len(self._active_subscriptions)} subscriptions"
        )

        # Create a copy of active subscriptions to re-subscribe
        subscriptions_to_resubscribe = list(self._active_subscriptions.values())
        # Clear active subscriptions - they'll be re-added as new subscriptions are confirmed
        self._active_subscriptions.clear()

        for sub in subscriptions_to_resubscribe:
            try:
                # Re-subscribe with the same request
                new_subscription_id = await self.subscribe(
                    users=sub.request["filters"]["users"],
                    on_event=self._on_event,
                )
                logger.info(
                    f"Re-subscribed: old_id={sub.subscription_id}, new_id={new_subscription_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to re-subscribe for users {sub.request['filters']['users']}: {e}"
                )

    async def _handle_disconnection(self) -> None:
        """Handle disconnection and attempt to reconnect."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self._websocket:
            try:
                await self._websocket.close()
            except Exception:
                pass
            self._websocket = None

        # Attempt to reconnect with exponential backoff
        while self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            delay = self._base_reconnect_delay * (2 ** (self._reconnect_attempts - 1))
            logger.info(
                f"Attempting to reconnect (attempt {self._reconnect_attempts}/{self._max_reconnect_attempts}) "
                f"in {delay:.2f} seconds..."
            )

            await asyncio.sleep(delay)

            try:
                await self.connect()
                logger.info("Successfully reconnected")
                return
            except Exception as e:
                logger.error(
                    f"Reconnection attempt {self._reconnect_attempts} failed: {e}"
                )
                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    logger.error(
                        "Max reconnection attempts reached. Stopping reconnection attempts."
                    )
                    self._connected = False
                    return

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
