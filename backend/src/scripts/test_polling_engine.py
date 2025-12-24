"""
Test script for Polling Engine Control APIs

Tests engine control and monitoring features:
- start_group() / stop_group()
- get_status_all()
- Maximum capacity limits
"""

import sys
import time
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from polling.polling_engine import PollingEngine
from polling.exceptions import (
    PollingGroupNotFoundError,
    PollingGroupAlreadyRunningError,
    MaxPollingGroupsReachedError
)
from plc.pool_manager import PoolManager


def test_engine_control():
    """
    Test polling engine control and monitoring APIs

    Verifies:
    - Individual group start/stop
    - Status queries
    - Maximum capacity enforcement
    - Graceful termination
    """
    print("=" * 60)
    print("Polling Engine Control API Test")
    print("=" * 60)

    # Initialize components
    db_path = "backend/data/scada.db"
    pool_manager = PoolManager(db_path)
    engine = PollingEngine(db_path, pool_manager)

    print(f"\n1. Initializing polling engine from database: {db_path}")
    engine.initialize()

    # Get all groups
    status = engine.get_status_all()
    print(f"\n2. Available polling groups: {len(status)}")
    for s in status:
        print(f"   - {s['group_name']}: mode={s['mode']}, state={s['state']}")

    if len(status) == 0:
        print("\n❌ No polling groups found in database")
        print("   Please add polling groups to test")
        return

    # Test 1: Start individual group
    print(f"\n3. Test: Start individual group")
    test_group_name = status[0]['group_name']

    try:
        engine.start_group(test_group_name)
        print(f"   ✅ Started group: {test_group_name}")
        time.sleep(0.5)

        # Check status
        current_status = engine.get_status_all()
        test_status = next((s for s in current_status if s['group_name'] == test_group_name), None)
        if test_status and test_status['state'] == 'running':
            print(f"   ✅ Group is running: {test_group_name}")
        else:
            print(f"   ❌ Group state unexpected: {test_status['state'] if test_status else 'not found'}")

    except Exception as e:
        print(f"   ❌ Error starting group: {e}")

    # Test 2: Attempt to start already running group (should fail)
    print(f"\n4. Test: Start already running group (should fail)")
    try:
        engine.start_group(test_group_name)
        print(f"   ❌ Should have raised PollingGroupAlreadyRunningError")
    except PollingGroupAlreadyRunningError as e:
        print(f"   ✅ Correctly raised exception: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    # Test 3: Stop individual group
    print(f"\n5. Test: Stop individual group")
    try:
        engine.stop_group(test_group_name, timeout=5.0)
        print(f"   ✅ Stopped group: {test_group_name}")

        # Verify stopped
        current_status = engine.get_status_all()
        test_status = next((s for s in current_status if s['group_name'] == test_group_name), None)
        if test_status and test_status['state'] == 'stopped':
            print(f"   ✅ Group is stopped: {test_group_name}")
        else:
            print(f"   ⚠️  Group state: {test_status['state'] if test_status else 'not found'}")

    except Exception as e:
        print(f"   ❌ Error stopping group: {e}")

    # Test 4: Query status API
    print(f"\n6. Test: Status query API")
    start_time = time.time()
    status_result = engine.get_status_all()
    response_time = (time.time() - start_time) * 1000  # Convert to ms

    print(f"   Response time: {response_time:.2f}ms")
    if response_time < 200:
        print(f"   ✅ Response within 200ms requirement")
    else:
        print(f"   ⚠️  Response time exceeds 200ms")

    print(f"   Groups returned: {len(status_result)}")
    for s in status_result:
        print(f"      - {s['group_name']}: state={s['state']}, polls={s['total_polls']}")

    # Test 5: Queue monitoring
    print(f"\n7. Test: Queue monitoring")
    queue_size = engine.get_queue_size()
    print(f"   Current queue size: {queue_size}")
    print(f"   Queue max size: {engine.data_queue.maxsize}")
    print(f"   Queue full: {engine.data_queue.is_full()}")

    # Test 6: Start all groups
    print(f"\n8. Test: Start all groups")
    try:
        engine.start_all()
        print(f"   ✅ start_all() executed")

        # Check how many are running
        running_status = engine.get_status_all()
        running_count = sum(1 for s in running_status if s['state'] == 'running')
        print(f"   Running groups: {running_count}/{len(running_status)}")

        if running_count > 10:
            print(f"   ⚠️  More than 10 groups running (max capacity check may have failed)")

    except Exception as e:
        print(f"   ❌ Error in start_all(): {e}")

    # Test 7: Graceful shutdown
    print(f"\n9. Test: Graceful shutdown")
    start_time = time.time()
    engine.stop_all(timeout=5.0)
    shutdown_time = time.time() - start_time

    print(f"   Shutdown time: {shutdown_time:.2f}s")
    if shutdown_time < 5.0:
        print(f"   ✅ Shutdown within 5s requirement")
    else:
        print(f"   ⚠️  Shutdown exceeded 5s")

    # Verify all stopped
    final_status = engine.get_status_all()
    stopped_count = sum(1 for s in final_status if s['state'] == 'stopped')
    print(f"   Stopped groups: {stopped_count}/{len(final_status)}")

    print(f"\n10. Test complete!")
    print("=" * 60)

    # Shutdown
    pool_manager.shutdown()


if __name__ == "__main__":
    try:
        test_engine_control()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
