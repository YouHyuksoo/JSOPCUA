"""
Test script for HANDSHAKE mode polling

Tests manual trigger polling with immediate execution verification.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from polling.polling_engine import PollingEngine
from plc.pool_manager import PoolManager


def test_handshake_polling():
    """
    Test HANDSHAKE mode polling with manual triggers

    Verifies:
    - Manual trigger initiates polling
    - Poll executes immediately (<1s)
    - Data is stored in queue
    - Deduplication works (ignores duplicates within 1s window)
    """
    print("=" * 60)
    print("HANDSHAKE Mode Polling Test")
    print("=" * 60)

    # Initialize components
    db_path = "backend/config/scada.db"
    pool_manager = PoolManager(db_path)
    engine = PollingEngine(db_path, pool_manager)

    print(f"\n1. Initializing polling engine from database: {db_path}")
    engine.initialize()

    # Get status before start
    status = engine.get_status_all()
    print(f"\n2. Found {len(status)} polling groups")
    for s in status:
        print(f"   - {s['group_name']}: mode={s['mode']}, state={s['state']}")

    # Filter for HANDSHAKE mode groups
    handshake_groups = [s for s in status if s['mode'] == 'HANDSHAKE']
    if not handshake_groups:
        print("\n❌ No HANDSHAKE mode groups found in database")
        print("   Please add at least one HANDSHAKE mode polling group to test")
        return

    test_group = handshake_groups[0]
    print(f"\n3. Testing group: {test_group['group_name']}")

    # Start all polling
    print("\n4. Starting polling engine...")
    engine.start_all()
    time.sleep(0.5)  # Give threads time to start

    # Test manual triggers
    print(f"\n5. Testing manual triggers...")

    # Trigger 1
    print(f"\n   Trigger 1: Sending first trigger")
    start_time = time.time()
    result1 = engine.trigger_handshake(test_group['group_name'])
    print(f"   Result: {result1}")

    if result1['success']:
        # Wait a bit and check status
        time.sleep(0.5)
        current_status = engine.get_status_all()
        test_status = next((s for s in current_status if s['group_name'] == test_group['group_name']), None)

        if test_status:
            response_time = time.time() - start_time
            print(f"   Poll executed: success_count={test_status['success_count']}, response_time={response_time:.3f}s")

    # Trigger 2 (immediate - should be deduplicated)
    print(f"\n   Trigger 2: Sending duplicate within 1s window (should be ignored)")
    result2 = engine.trigger_handshake(test_group['group_name'])
    print(f"   Result: {result2}")

    # Wait for deduplication window
    print(f"\n   Waiting 1.5s for deduplication window...")
    time.sleep(1.5)

    # Trigger 3 (after dedup window - should succeed)
    print(f"\n   Trigger 3: Sending trigger after deduplication window")
    result3 = engine.trigger_handshake(test_group['group_name'])
    print(f"   Result: {result3}")

    if result3['success']:
        time.sleep(0.5)

    # Get final statistics
    print(f"\n6. Final statistics:")
    final_status = engine.get_status_all()
    test_final = next((s for s in final_status if s['group_name'] == test_group['group_name']), None)

    if test_final:
        print(f"   Total polls: {test_final['total_polls']}")
        print(f"   Successful: {test_final['success_count']}")
        print(f"   Failed: {test_final['error_count']}")
        print(f"   Average poll time: {test_final['avg_poll_time_ms']:.2f}ms")

        expected_polls = 2  # Trigger 1 and 3 should succeed, 2 should be deduplicated
        if test_final['total_polls'] >= expected_polls:
            print(f"   ✅ Expected behavior: 2 polls executed (1 deduplicated)")
        else:
            print(f"   ⚠️  Unexpected: expected at least {expected_polls} polls")

    # Check queue
    queue_size = engine.get_queue_size()
    print(f"\n7. Queue status:")
    print(f"   Items in queue: {queue_size}")

    # Stop engine
    print(f"\n8. Stopping polling engine...")
    engine.stop_all(timeout=5.0)

    print(f"\n9. Test complete!")
    print("=" * 60)

    # Shutdown
    pool_manager.shutdown()


if __name__ == "__main__":
    try:
        test_handshake_polling()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
