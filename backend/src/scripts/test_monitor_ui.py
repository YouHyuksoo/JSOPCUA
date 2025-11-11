"""
Test script for Monitor UI API endpoints

Feature 7: Monitor Web UI - Test alarm API and WebSocket endpoints
"""

import asyncio
import json
import time
import websockets
from datetime import datetime


# Configuration
API_BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws/monitor"


def test_alarm_statistics():
    """Test GET /api/alarms/statistics endpoint"""
    import requests

    print("\n=== Testing Alarm Statistics API ===")
    try:
        response = requests.get(f"{API_BASE_URL}/api/alarms/statistics", timeout=5)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Equipment count: {len(data.get('equipment', []))}")
            print(f"✓ Last updated: {data.get('last_updated')}")

            if data.get('equipment'):
                sample = data['equipment'][0]
                print(f"✓ Sample equipment: {sample.get('equipment_name')} - Alarm: {sample.get('alarm_count')}, General: {sample.get('general_count')}")
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_recent_alarms():
    """Test GET /api/alarms/recent endpoint"""
    import requests

    print("\n=== Testing Recent Alarms API ===")
    try:
        response = requests.get(f"{API_BASE_URL}/api/alarms/recent?limit=5", timeout=5)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            alarms = data.get('alarms', [])
            print(f"✓ Alarms count: {len(alarms)}")

            if alarms:
                sample = alarms[0]
                print(f"✓ Sample alarm: {sample.get('equipment_name')} - {sample.get('alarm_type')} - {sample.get('alarm_message')[:30]}...")
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_alarm_health():
    """Test GET /api/alarms/health endpoint"""
    import requests

    print("\n=== Testing Alarm Health Check ===")
    try:
        response = requests.get(f"{API_BASE_URL}/api/alarms/health", timeout=5)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            print(f"✓ Oracle connection: {data.get('oracle_connection')}")
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")


async def test_websocket_monitor():
    """Test WebSocket /ws/monitor endpoint"""
    print("\n=== Testing WebSocket Monitor ===")

    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✓ WebSocket connected")

            # Receive connection status message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"✓ Connection message: {data.get('type')} - {data.get('message')}")

            # Receive equipment status updates (10 seconds)
            print("Receiving equipment status updates for 10 seconds...")
            start_time = time.time()
            message_count = 0

            while time.time() - start_time < 10:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2)
                    data = json.loads(message)

                    if data.get('type') == 'equipment_status':
                        message_count += 1
                        equipment = data.get('equipment', [])
                        print(f"✓ Received equipment status: {len(equipment)} equipment, Message #{message_count}")

                        # Show sample equipment status
                        if equipment and message_count == 1:
                            sample = equipment[0]
                            print(f"  Sample: {sample.get('equipment_name')} - {sample.get('status')} - Connection: {sample.get('tags', {}).get('connection')}")

                except asyncio.TimeoutError:
                    print("⚠ No message received in 2 seconds")

            print(f"✓ Total messages received: {message_count}")
            print(f"✓ Average interval: {10 / message_count:.2f}s" if message_count > 0 else "✗ No messages received")

    except Exception as e:
        print(f"✗ WebSocket error: {str(e)}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Monitor UI API & WebSocket Test Script")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"WebSocket URL: {WEBSOCKET_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")

    # Test HTTP API endpoints
    test_alarm_statistics()
    test_recent_alarms()
    test_alarm_health()

    # Test WebSocket endpoint
    asyncio.run(test_websocket_monitor())

    print("\n" + "=" * 60)
    print("All tests completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
