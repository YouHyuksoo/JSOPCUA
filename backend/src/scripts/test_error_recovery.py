"""
Test script for error recovery and resilience

Tests polling engine error handling and recovery capabilities.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from polling.polling_engine import PollingEngine
from plc.pool_manager import PoolManager


def test_error_recovery():
    """
    Test error recovery and resilience features
    """
    print("=" * 60)
    print("Error Recovery and Resilience Test")
    print("=" * 60)

    # Initialize components
    db_path = "backend/config/scada.db"
    pool_manager = PoolManager(db_path)
    engine = PollingEngine(db_path, pool_manager)

    print(f"\n1. Initializing polling engine...")
    engine.initialize()

    print(f"\n2. Starting all polling groups...")
    engine.start_all()
    time.sleep(2.0)

    print(f"\n3. Monitoring for 10 seconds...")
    for i in range(10):
        time.sleep(1)
        status = engine.get_status_all()
        total_polls = sum(s['total_polls'] for s in status)
        total_errors = sum(s['error_count'] for s in status)
        print(f"   Second {i+1}: polls={total_polls}, errors={total_errors}")

    print(f"\n4. Stopping all groups...")
    engine.stop_all(timeout=5.0)

    print("\n5. Test complete!")
    pool_manager.shutdown()


if __name__ == "__main__":
    test_error_recovery()
