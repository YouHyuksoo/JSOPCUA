"""
WebSocket Monitor Handler

Feature 7: Monitor Web UI - Real-time equipment status updates
Broadcasts equipment status to connected Monitor UI clients every 1 second
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect


# Connected Monitor UI clients
active_connections: Set[WebSocket] = set()

logger = logging.getLogger(__name__)

# Polling engine instance (to be set by main.py)
_polling_engine = None


def set_monitor_engine(engine):
    """Set the polling engine instance for WebSocket broadcasts"""
    global _polling_engine
    _polling_engine = engine


async def websocket_monitor_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for Monitor UI clients

    Sends real-time equipment status updates every 1 second
    Message format:
    {
        "type": "equipment_status",
        "timestamp": "2025-11-04T10:30:45.123Z",
        "equipment": [
            {
                "equipment_code": "KRCWO12ELOA101",
                "equipment_name": "Upper 로봇 용접",
                "status": "running",
                "tags": {
                    "status_tag": 1,
                    "error_tag": 0,
                    "connection": true
                },
                "last_updated": "2025-11-04T10:30:45.000Z"
            }
        ]
    }
    """
    await websocket.accept()
    active_connections.add(websocket)

    try:
        # Send connection status message
        await websocket.send_json({
            "type": "connection_status",
            "timestamp": datetime.now().isoformat(),
            "status": "connected",
            "message": "WebSocket connected successfully"
        })

        # Continuous broadcast loop
        while True:
            try:
                # Get equipment status from polling engine
                equipment_status = await get_equipment_status()

                # Broadcast to client
                message = {
                    "type": "equipment_status",
                    "timestamp": datetime.now().isoformat(),
                    "equipment": equipment_status
                }

                await websocket.send_json(message)

                # Wait 1 second before next broadcast
                await asyncio.sleep(1)

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                break

    except WebSocketDisconnect:
        pass
    finally:
        active_connections.discard(websocket)
        logger.info(f"Monitor client disconnected. Active connections: {len(active_connections)}")


async def get_equipment_status() -> List[Dict]:
    """
    Get current equipment status from polling engine

    Returns list of equipment status dictionaries
    """
    if _polling_engine is None:
        # Return mock data if polling engine is not available
        return get_mock_equipment_status()

    try:
        # TODO: Implement actual polling engine query
        # This should query the polling engine for the current tag values
        # and map them to equipment status

        # For now, return mock data
        return get_mock_equipment_status()

    except Exception as e:
        logger.error(f"Error getting equipment status: {e}")
        return get_mock_equipment_status()


def get_mock_equipment_status() -> List[Dict]:
    """
    Return mock equipment status for testing

    This is temporary until actual polling engine integration is implemented
    """
    # 17 equipment mock data
    equipment_codes = [
        "KRCWO12ELOA101", "KRCWO12ELOA102", "KRCWO12ELOA103",
        "KRCWO12ELOA104", "KRCWO12ELOA105", "KRCWO12ELOA106",
        "KRCWO12ELOA107", "KRCWO12ELOA108", "KRCWO12ELOA109",
        "KRCWO12ELOA110", "KRCWO12ELOA111", "KRCWO12ELOA112",
        "KRCWO12ELOA113", "KRCWO12ELOA114", "KRCWO12ELOA115",
        "KRCWO12ELOA116", "KRCWO12ELOA117"
    ]

    equipment_names = [
        "Upper 로봇 용접", "Lower 로봇 용접", "Front 조립",
        "Rear 조립", "Paint 도장", "Inspection 검사",
        "Welding 1", "Welding 2", "Assembly 1",
        "Assembly 2", "Coating 1", "Coating 2",
        "Quality 1", "Quality 2", "Packing 1",
        "Packing 2", "Shipping"
    ]

    equipment_status_list = []

    import random

    for i, (code, name) in enumerate(zip(equipment_codes, equipment_names)):
        # Randomly generate status for testing
        connection = random.choice([True, True, True, False])  # 75% connected
        error_tag = 0 if connection else random.choice([0, 0, 0, 1])  # 25% error when connected
        status_tag = 1 if connection and error_tag == 0 else 0

        if not connection:
            status = "disconnected"
        elif error_tag == 1:
            status = "error"
        elif status_tag == 0:
            status = "stopped"
        elif random.random() < 0.2:
            status = "idle"
        else:
            status = "running"

        equipment_status_list.append({
            "equipment_code": code,
            "equipment_name": name,
            "status": status,
            "tags": {
                "status_tag": status_tag,
                "error_tag": error_tag,
                "connection": connection
            },
            "last_updated": datetime.now().isoformat()
        })

    return equipment_status_list


async def broadcast_to_all_clients(message: Dict):
    """
    Broadcast message to all connected Monitor UI clients

    This function can be called by external modules to push updates
    """
    if not active_connections:
        return

    disconnected = set()

    for websocket in active_connections:
        try:
            await websocket.send_json(message)
        except Exception:
            disconnected.add(websocket)

    # Remove disconnected clients
    active_connections.difference_update(disconnected)
