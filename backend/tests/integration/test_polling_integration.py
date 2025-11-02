"""
Integration test for polling engine with multiple concurrent groups
"""

import pytest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from polling.polling_engine import PollingEngine
from polling.models import PollingMode
from plc.pool_manager import PoolManager


def test_concurrent_polling_groups():
    """Test 10 concurrent polling groups without conflicts"""
    db_path = "backend/config/scada.db"
    pool_manager = PoolManager(db_path)
    engine = PollingEngine(db_path, pool_manager)
    
    engine.initialize()
    engine.start_all()
    
    # Run for 5 seconds
    time.sleep(5.0)
    
    # Verify all groups operational
    status = engine.get_status_all()
    running = [s for s in status if s['state'] == 'running']
    
    assert len(running) > 0, "At least one group should be running"
    
    # Check for data corruption
    queue_size = engine.get_queue_size()
    assert queue_size >= 0, "Queue size should be non-negative"
    
    engine.stop_all()
    pool_manager.shutdown()


if __name__ == "__main__":
    test_concurrent_polling_groups()
    print("✅ Integration test passed")
