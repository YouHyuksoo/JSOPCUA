"""
Integrated Startup Script

Starts all Feature 3 and Feature 4 components:
- Feature 3: Polling Engine (PollingEngine with PoolManager)
- Feature 4: BufferConsumer + OracleWriter

Usage:
    python backend/src/scripts/start_all.py

Press Ctrl+C to gracefully shutdown all components.
"""

import sys
import os
import time
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plc.pool_manager import PoolManager
from polling.polling_engine import PollingEngine
from polling.data_queue import DataQueue
from buffer.circular_buffer import CircularBuffer
from buffer.buffer_consumer import BufferConsumer
from oracle_writer.writer import OracleWriter
from oracle_writer.connection_pool import OracleConnectionPool
from oracle_writer.metrics import RollingMetrics
from oracle_writer.backup import CSVBackup
from oracle_writer.config import OracleConfig

# Global shutdown flag
shutdown_requested = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_requested
    print("\n[SIGNAL] Shutdown signal received (Ctrl+C)")
    shutdown_requested = True


def main():
    """Main entry point"""
    global shutdown_requested

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 80)
    print("INTEGRATED STARTUP: Feature 3 + Feature 4")
    print("=" * 80)
    print()

    # Configuration
    db_path = "backend/config/scada.db"

    # Feature 3: Polling Engine
    print("[FEATURE 3] Initializing Polling Engine...")
    try:
        pool_manager = PoolManager(db_path)
        data_queue = DataQueue(maxsize=10000)
        polling_engine = PollingEngine(db_path, pool_manager, data_queue=data_queue)
        polling_engine.initialize()
        print(f"  ✓ Polling Engine initialized")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return 1

    # Feature 4: Buffer
    print("[FEATURE 4] Initializing Circular Buffer...")
    try:
        circular_buffer = CircularBuffer(maxsize=10000, overflow_alert_threshold=80.0)
        print(f"  ✓ Circular Buffer initialized (max size: 10,000)")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        polling_engine.shutdown()
        pool_manager.shutdown()
        return 1

    # Feature 4: Oracle Connection Pool
    print("[FEATURE 4] Initializing Oracle Connection Pool...")
    try:
        oracle_config = OracleConfig.from_env()
        connection_pool = OracleConnectionPool(
            host=oracle_config.host,
            port=oracle_config.port,
            service_name=oracle_config.service_name,
            username=oracle_config.username,
            password=oracle_config.password,
            min_pool_size=oracle_config.pool_min,
            max_pool_size=oracle_config.pool_max
        )
        print(f"  ✓ Oracle Connection Pool initialized (min={oracle_config.pool_min}, max={oracle_config.pool_max})")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        print("  NOTE: Oracle connection is optional. Buffer and consumer will still run.")
        connection_pool = None

    # Feature 4: Metrics and Backup
    print("[FEATURE 4] Initializing Metrics and CSV Backup...")
    try:
        metrics = RollingMetrics(window_seconds=300)  # 5-minute window
        csv_backup = CSVBackup(backup_dir="backend/backup")
        print(f"  ✓ Metrics and CSV Backup initialized")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        if connection_pool:
            connection_pool.close()
        polling_engine.shutdown()
        pool_manager.shutdown()
        return 1

    # Feature 4: Buffer Consumer Thread
    print("[FEATURE 4] Starting Buffer Consumer...")
    try:
        buffer_consumer = BufferConsumer(data_queue, circular_buffer)
        buffer_consumer.start()
        print(f"  ✓ Buffer Consumer thread started")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        if connection_pool:
            connection_pool.close()
        polling_engine.shutdown()
        pool_manager.shutdown()
        return 1

    # Feature 4: Oracle Writer Thread
    oracle_writer = None
    if connection_pool:
        print("[FEATURE 4] Starting Oracle Writer...")
        try:
            oracle_writer = OracleWriter(
                circular_buffer=circular_buffer,
                connection_pool=connection_pool,
                metrics=metrics,
                csv_backup=csv_backup,
                batch_size=500,
                write_interval=0.5,
                retry_max=3
            )
            oracle_writer.start()
            print(f"  ✓ Oracle Writer thread started")
        except Exception as e:
            print(f"  ✗ FAIL: {e}")
            buffer_consumer.stop()
            buffer_consumer.join(timeout=5)
            connection_pool.close()
            polling_engine.shutdown()
            pool_manager.shutdown()
            return 1
    else:
        print("[FEATURE 4] Oracle Writer skipped (no connection pool)")

    # Feature 3: Start all polling groups
    print("[FEATURE 3] Starting all polling groups...")
    try:
        polling_engine.start_all_groups()
        print(f"  ✓ All polling groups started")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")

    print()
    print("=" * 80)
    print("ALL COMPONENTS RUNNING")
    print("=" * 80)
    print()
    print("Components:")
    print(f"  - Polling Engine: RUNNING")
    print(f"  - Buffer Consumer: RUNNING")
    if oracle_writer:
        print(f"  - Oracle Writer: RUNNING")
    else:
        print(f"  - Oracle Writer: SKIPPED (no Oracle connection)")
    print()
    print("Press Ctrl+C to gracefully shutdown all components...")
    print()

    # Main loop - wait for shutdown signal
    try:
        while not shutdown_requested:
            time.sleep(1)

            # Check thread health
            if not buffer_consumer.is_alive():
                print("\n[WARNING] Buffer Consumer thread died unexpectedly")
                shutdown_requested = True

            if oracle_writer and not oracle_writer.is_alive():
                print("\n[WARNING] Oracle Writer thread died unexpectedly")
                shutdown_requested = True

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Keyboard interrupt received")
        shutdown_requested = True

    # Graceful shutdown
    print()
    print("=" * 80)
    print("GRACEFUL SHUTDOWN")
    print("=" * 80)
    print()

    # Stop polling engine
    print("[FEATURE 3] Stopping polling engine...")
    try:
        polling_engine.stop_all_groups()
        time.sleep(2)  # Allow final polling data to be queued
        print(f"  ✓ Polling engine stopped")
    except Exception as e:
        print(f"  ✗ WARNING: {e}")

    # Stop buffer consumer
    print("[FEATURE 4] Stopping buffer consumer...")
    try:
        buffer_consumer.stop()
        buffer_consumer.join(timeout=10)
        if buffer_consumer.is_alive():
            print(f"  ✗ WARNING: Buffer consumer did not stop within 10 seconds")
        else:
            print(f"  ✓ Buffer consumer stopped")
    except Exception as e:
        print(f"  ✗ WARNING: {e}")

    # Stop Oracle writer
    if oracle_writer:
        print("[FEATURE 4] Stopping Oracle writer...")
        try:
            oracle_writer.stop()
            oracle_writer.join(timeout=10)
            if oracle_writer.is_alive():
                print(f"  ✗ WARNING: Oracle writer did not stop within 10 seconds")
            else:
                print(f"  ✓ Oracle writer stopped")
        except Exception as e:
            print(f"  ✗ WARNING: {e}")

    # Close Oracle connection pool
    if connection_pool:
        print("[FEATURE 4] Closing Oracle connection pool...")
        try:
            connection_pool.close()
            print(f"  ✓ Oracle connection pool closed")
        except Exception as e:
            print(f"  ✗ WARNING: {e}")

    # Shutdown polling engine and pool manager
    print("[FEATURE 3] Shutting down polling engine...")
    try:
        polling_engine.shutdown()
        print(f"  ✓ Polling engine shutdown")
    except Exception as e:
        print(f"  ✗ WARNING: {e}")

    print("[FEATURE 3] Shutting down pool manager...")
    try:
        pool_manager.shutdown()
        print(f"  ✓ Pool manager shutdown")
    except Exception as e:
        print(f"  ✗ WARNING: {e}")

    print()
    print("=" * 80)
    print("SHUTDOWN COMPLETE")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
