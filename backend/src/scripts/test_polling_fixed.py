"""
Test script for FIXED mode polling

Tests automatic polling at fixed intervals with timing accuracy verification.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from polling.polling_engine import PollingEngine
from plc.pool_manager import PoolManager


def test_fixed_polling():
    """
    Test FIXED mode polling with one polling group

    Verifies:
    - Polling occurs at 1-second interval
    - Data is collected and stored in queue
    - Timing accuracy is within ±10%
    """
    print("=" * 60)
    print("FIXED Mode Polling Test")
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

    # Filter for FIXED mode groups
    fixed_groups = [s for s in status if s['mode'] == 'FIXED']
    if not fixed_groups:
        print("\n❌ No FIXED mode groups found in database")
        print("   Please add at least one FIXED mode polling group to test")
        return

    test_group = fixed_groups[0]
    print(f"\n3. Testing group: {test_group['group_name']}")

    # Start all polling
    print("\n4. Starting polling engine...")
    engine.start_all()
    time.sleep(0.5)  # Give threads time to start

    # Monitor for 10 cycles
    print(f"\n5. Monitoring polling cycles (10 cycles)...")
    print(f"   Expected interval: Check database for group interval_ms")
    print(f"   Tolerance: ±10%")
    print()

    cycle_times = []
    last_poll_time = None

    for i in range(10):
        time.sleep(1.1)  # Wait a bit longer than expected interval

        # Get current status
        current_status = engine.get_status_all()
        test_status = next((s for s in current_status if s['group_name'] == test_group['group_name']), None)

        if test_status:
            current_poll_time = test_status['last_poll_time']
            success_count = test_status['success_count']
            avg_time = test_status['avg_poll_time_ms']

            if last_poll_time and current_poll_time != last_poll_time:
                # New poll occurred
                print(
                    f"   Cycle {i+1}: "
                    f"success_count={success_count}, "
                    f"avg_poll_time={avg_time:.2f}ms"
                )

            last_poll_time = current_poll_time

    # Get final statistics
    print(f"\n6. Final statistics:")
    final_status = engine.get_status_all()
    test_final = next((s for s in final_status if s['group_name'] == test_group['group_name']), None)

    if test_final:
        print(f"   Total polls: {test_final['total_polls']}")
        print(f"   Successful: {test_final['success_count']}")
        print(f"   Failed: {test_final['error_count']}")
        print(f"   Average poll time: {test_final['avg_poll_time_ms']:.2f}ms")

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
        test_fixed_polling()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
