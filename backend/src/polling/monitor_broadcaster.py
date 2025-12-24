"""
Monitor Broadcaster Thread

Background thread that consumes polling data from DataQueue and broadcasts
to WebSocket clients for real-time monitoring.
"""

import threading
import logging
import json
import asyncio
from datetime import datetime
from typing import Optional, Set
from queue import Empty
from fastapi import WebSocket

from .data_queue import DataQueue
from .models import PollingData

logger = logging.getLogger(__name__)


class MonitorBroadcaster:
    """
    Background thread for broadcasting polling data to WebSocket clients

    Consumes PollingData from DataQueue and broadcasts to all connected
    WebSocket clients for real-time monitoring dashboards.

    Attributes:
        data_queue: DataQueue to consume from
        clients: Set of connected WebSocket clients
        thread: Threading.Thread instance
        stop_event: Event to signal thread shutdown
    """

    def __init__(self, data_queue: DataQueue):
        """
        Initialize monitor broadcaster

        Args:
            data_queue: DataQueue to consume polling results from
        """
        self.data_queue = data_queue

        # WebSocket clients
        self.clients: Set[WebSocket] = set()
        self._clients_lock = threading.Lock()

        # Thread management
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._running = False

        # Event loop for async operations
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Statistics
        self.messages_broadcast = 0
        self.clients_connected = 0
        self.last_broadcast_time: Optional[datetime] = None

        logger.info("MonitorBroadcaster initialized")

    def start(self):
        """Start the broadcaster thread"""
        if self._running:
            logger.warning("Monitor broadcaster already running")
            return

        self.stop_event.clear()
        self._running = True
        self.thread = threading.Thread(
            target=self._run,
            name="MonitorBroadcaster",
            daemon=False
        )
        self.thread.start()
        logger.info("Monitor broadcaster started")

    def stop(self, timeout: float = 5.0):
        """
        Stop the broadcaster thread gracefully

        Args:
            timeout: Maximum time to wait for thread termination (seconds)
        """
        if not self._running:
            logger.warning("Monitor broadcaster not running")
            return

        logger.info("Stopping monitor broadcaster...")
        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
            if self.thread.is_alive():
                logger.error(f"Monitor broadcaster did not stop within {timeout}s")
            else:
                self._running = False
                logger.info("Monitor broadcaster stopped")
        else:
            self._running = False

    def _run(self):
        """Main broadcaster loop"""
        logger.info("Monitor broadcaster running")

        # Create event loop for this thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            while not self.stop_event.is_set():
                try:
                    # Get data from queue with timeout
                    polling_data = self.data_queue.get(timeout=1.0)

                    # Broadcast to all clients
                    if self.clients:
                        self._broadcast_data(polling_data)

                except Empty:
                    # Queue timeout - no data to broadcast
                    continue

        except Exception as e:
            logger.error(f"Monitor broadcaster crashed: {e}", exc_info=True)

        finally:
            # Close event loop
            if self._loop:
                self._loop.close()

            self._running = False
            logger.info("Monitor broadcaster exited")

    def _broadcast_data(self, polling_data: PollingData):
        """
        Broadcast polling data to all connected WebSocket clients

        Args:
            polling_data: PollingData object to broadcast
        """
        # Convert to JSON message
        message = {
            "type": "polling_data",
            "timestamp": polling_data.timestamp.isoformat(),
            "group_id": polling_data.group_id,
            "group_name": polling_data.group_name,
            "plc_code": polling_data.plc_code,
            "mode": polling_data.mode.value,
            "poll_time_ms": polling_data.poll_time_ms,
            "tag_values": polling_data.tag_values,
            "error_tags": polling_data.error_tags
        }

        message_json = json.dumps(message)

        # Broadcast to all clients
        disconnected_clients = set()

        with self._clients_lock:
            for client in self.clients:
                try:
                    # Send message asynchronously
                    asyncio.run_coroutine_threadsafe(
                        client.send_text(message_json),
                        self._loop
                    )
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected_clients.add(client)

            # Remove disconnected clients
            if disconnected_clients:
                self.clients -= disconnected_clients
                logger.info(f"Removed {len(disconnected_clients)} disconnected clients")

        # Update statistics
        self.messages_broadcast += 1
        self.last_broadcast_time = datetime.now()

        logger.debug(
            f"Broadcast polling data: group={polling_data.group_name}, "
            f"clients={len(self.clients)}, tags={len(polling_data.tag_values)}"
        )

    def add_client(self, client: WebSocket):
        """
        Add a WebSocket client

        Args:
            client: WebSocket client to add
        """
        with self._clients_lock:
            self.clients.add(client)
            self.clients_connected += 1
            logger.info(f"Client connected (total: {len(self.clients)})")

    def remove_client(self, client: WebSocket):
        """
        Remove a WebSocket client

        Args:
            client: WebSocket client to remove
        """
        with self._clients_lock:
            if client in self.clients:
                self.clients.remove(client)
                logger.info(f"Client disconnected (total: {len(self.clients)})")

    def get_stats(self) -> dict:
        """
        Get broadcaster statistics

        Returns:
            Dictionary with statistics
        """
        with self._clients_lock:
            client_count = len(self.clients)

        return {
            "running": self._running,
            "clients_connected": client_count,
            "total_clients_connected": self.clients_connected,
            "messages_broadcast": self.messages_broadcast,
            "last_broadcast_time": self.last_broadcast_time.isoformat() if self.last_broadcast_time else None
        }

    def is_running(self) -> bool:
        """Check if broadcaster is running"""
        return self._running
