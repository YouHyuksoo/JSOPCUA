"""
WebSocket Handler

Real-time updates for polling engine status via WebSocket.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Optional
import asyncio
import json
from datetime import datetime

from polling.polling_engine import PollingEngine


class ConnectionManager:
    """
    WebSocket connection manager

    Manages active WebSocket connections and broadcasts status updates.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcast_task: Optional[asyncio.Task] = None
        self.engine: Optional[PollingEngine] = None
        self.broadcast_interval_s = 1.0  # Broadcast every 1 second

    def set_engine(self, engine: PollingEngine):
        """Set the polling engine instance"""
        self.engine = engine

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)

        # Start broadcast task if not already running
        if not self.broadcast_task or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self._broadcast_loop())

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)

        # Stop broadcast task if no connections
        if not self.active_connections and self.broadcast_task:
            self.broadcast_task.cancel()

    async def send_status(self, websocket: WebSocket):
        """Send current engine status to a single connection"""
        if not self.engine:
            return

        try:
            groups_status = self.engine.get_status_all()
            queue_size = self.engine.get_queue_size()

            status_data = {
                "type": "status_update",
                "data": {
                    "groups": groups_status,
                    "queue": {
                        "queue_size": queue_size,
                        "queue_maxsize": self.engine.data_queue.maxsize,
                        "queue_is_full": self.engine.data_queue.is_full()
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }

            await websocket.send_json(status_data)
        except Exception as e:
            print(f"Error sending status to WebSocket: {e}")

    async def broadcast_status(self):
        """Broadcast current engine status to all connections"""
        if not self.active_connections:
            return

        # Get current status
        if not self.engine:
            return

        try:
            groups_status = self.engine.get_status_all()
            queue_size = self.engine.get_queue_size()

            status_data = {
                "type": "status_update",
                "data": {
                    "groups": groups_status,
                    "queue": {
                        "queue_size": queue_size,
                        "queue_maxsize": self.engine.data_queue.maxsize,
                        "queue_is_full": self.engine.data_queue.is_full()
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }

            # Send to all connections
            dead_connections = set()
            for connection in self.active_connections:
                try:
                    await connection.send_json(status_data)
                except Exception as e:
                    print(f"Error broadcasting to WebSocket: {e}")
                    dead_connections.add(connection)

            # Remove dead connections
            self.active_connections -= dead_connections

        except Exception as e:
            print(f"Error broadcasting status: {e}")

    async def _broadcast_loop(self):
        """Background task to periodically broadcast status"""
        try:
            while self.active_connections:
                await self.broadcast_status()
                await asyncio.sleep(self.broadcast_interval_s)
        except asyncio.CancelledError:
            pass


# Global connection manager
manager = ConnectionManager()


def set_websocket_engine(engine: PollingEngine):
    """Set the polling engine for WebSocket manager"""
    manager.set_engine(engine)


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time status updates

    Clients receive automatic status updates every second.
    """
    await manager.connect(websocket)

    try:
        # Send initial status
        await manager.send_status(websocket)

        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client (heartbeat, commands, etc.)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # 60 second timeout
                )

                # Handle client messages
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif message.get("type") == "get_status":
                        await manager.send_status(websocket)
                except json.JSONDecodeError:
                    pass

            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
