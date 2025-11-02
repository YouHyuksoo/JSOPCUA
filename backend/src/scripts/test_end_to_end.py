"""
End-to-End Test: Polling → Buffer → Oracle

Test the complete data flow from polling engine through buffer to Oracle Database.

Usage:
    python backend/src/scripts/test_end_to_end.py
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add backend/src to path for imports
backend_src = Path(__file__).parent.parent
sys.path.insert(0, str(backend_src))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import components
from buffer.circular_buffer import CircularBuffer
from buffer.buffer_consumer import BufferConsumer
from buffer.models import BufferedTagValue
from oracle_writer.config import load_config_from_env, load_buffer_config_from_env
from oracle_writer.connection_pool import OracleConnectionPool
from oracle_writer.metrics import RollingMetrics
from oracle_writer.backup import CSVBackup
from oracle_writer.writer import OracleWriter
from polling.data_queue import DataQueue
from polling.models import PollingData, PollingMode


def create_test_polling_data(group_id: int, tag_count: int = 10) -> PollingData:
    """
    Create test polling data

    Args:
        group_id: Polling group ID
        tag_count: Number of tags to generate

    Returns:
        PollingData object with test data
    """
    tag_values = {
        f"D{100 + i}": float(1000 + i) for i in range(tag_count)
    }

    return PollingData(
        timestamp=datetime.now(),
        group_id=group_id,
        group_name=f"TestGroup{group_id}",
        plc_code="KRCWO12ELOA101",
        mode=PollingMode.FIXED,
        tag_values=tag_values,
        poll_time_ms=50.0,
        error_tags={}
    )


def test_buffer_consumer(data_queue: DataQueue, circular_buffer: CircularBuffer):
    """
    Test 1: Buffer Consumer

    Verify that BufferConsumer correctly expands PollingData to BufferedTagValue items.

    Args:
        data_queue: DataQueue instance
        circular_buffer: CircularBuffer instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Test 1: Buffer Consumer")
    logger.info("=" * 60)

    try:
        # Create and start buffer consumer
        buffer_consumer = BufferConsumer(data_queue, circular_buffer)
        buffer_consumer.start()

        # Add test polling data
        test_data = create_test_polling_data(group_id=1, tag_count=5)
        data_queue.put(test_data)

        logger.info(f"✓ Added PollingData with {len(test_data.tag_values)} tags to DataQueue")

        # Wait for consumer to process
        time.sleep(2)

        # Check buffer size
        buffer_size = circular_buffer.size()
        expected_size = len(test_data.tag_values)

        if buffer_size >= expected_size:
            logger.info(f"✓ CircularBuffer size: {buffer_size} (expected: {expected_size})")

            # Peek at items
            items = circular_buffer.peek(count=2)
            logger.info(f"✓ Sample items in buffer:")
            for item in items:
                logger.info(f"  - {item.plc_code} / {item.tag_address} = {item.tag_value}")

            # Stop consumer
            buffer_consumer.stop(timeout=5.0)
            logger.info("✓ Buffer consumer stopped")

            return True
        else:
            logger.error(f"✗ Buffer size mismatch: {buffer_size} != {expected_size}")
            buffer_consumer.stop(timeout=5.0)
            return False

    except Exception as e:
        logger.error(f"✗ Buffer consumer test failed: {e}", exc_info=True)
        return False


def test_oracle_writer(
    circular_buffer: CircularBuffer,
    connection_pool: OracleConnectionPool,
    metrics: RollingMetrics,
    csv_backup: CSVBackup
):
    """
    Test 2: Oracle Writer

    Verify that OracleWriter correctly writes buffered data to Oracle.

    Args:
        circular_buffer: CircularBuffer instance
        connection_pool: OracleConnectionPool instance
        metrics: RollingMetrics instance
        csv_backup: CSVBackup instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test 2: Oracle Writer")
    logger.info("=" * 60)

    try:
        # Add test items to buffer
        test_items = [
            BufferedTagValue(
                timestamp=datetime.now(),
                plc_code="KRCWO12ELOA101",
                tag_address=f"D{200 + i}",
                tag_value=float(2000 + i),
                quality="GOOD"
            )
            for i in range(10)
        ]

        for item in test_items:
            circular_buffer.put(item)

        logger.info(f"✓ Added {len(test_items)} test items to CircularBuffer")

        # Create and start Oracle writer
        oracle_writer = OracleWriter(
            circular_buffer=circular_buffer,
            connection_pool=connection_pool,
            metrics=metrics,
            csv_backup=csv_backup,
            batch_size=500,
            write_interval=1.0
        )
        oracle_writer.start()
        logger.info("✓ Oracle writer started")

        # Wait for write to complete
        time.sleep(3)

        # Check buffer is empty
        buffer_size = circular_buffer.size()
        if buffer_size == 0:
            logger.info(f"✓ Buffer emptied (size: {buffer_size})")
        else:
            logger.warning(f"⚠ Buffer not fully emptied (size: {buffer_size})")

        # Check metrics
        stats = metrics.stats()
        logger.info(f"✓ Metrics:")
        logger.info(f"  - Successful writes: {stats['total_successful_writes']}")
        logger.info(f"  - Failed writes: {stats['total_failed_writes']}")
        logger.info(f"  - Items written: {stats['total_items_written']}")
        logger.info(f"  - Avg batch size: {stats['avg_batch_size']}")
        logger.info(f"  - Avg latency: {stats['avg_write_latency_ms']:.1f}ms")

        # Stop writer
        oracle_writer.stop(timeout=5.0)
        logger.info("✓ Oracle writer stopped")

        # Verify data in Oracle
        success = verify_data_in_oracle(connection_pool, test_items)

        return success

    except Exception as e:
        logger.error(f"✗ Oracle writer test failed: {e}", exc_info=True)
        return False


def verify_data_in_oracle(connection_pool: OracleConnectionPool, expected_items: list) -> bool:
    """
    Verify that data was written to Oracle tag_values table

    Args:
        connection_pool: OracleConnectionPool instance
        expected_items: List of expected BufferedTagValue items

    Returns:
        True if data found, False otherwise
    """
    logger.info("")
    logger.info("Verifying data in Oracle...")

    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()

            # Count rows for test PLC code
            cursor.execute("""
                SELECT COUNT(*)
                FROM tag_values
                WHERE plc_code = 'KRCWO12ELOA101'
                AND tag_address LIKE 'D2%'
            """)
            count = cursor.fetchone()[0]

            if count > 0:
                logger.info(f"✓ Found {count} rows in tag_values table")

                # Sample a few rows
                cursor.execute("""
                    SELECT timestamp, plc_code, tag_address, tag_value, quality
                    FROM tag_values
                    WHERE plc_code = 'KRCWO12ELOA101'
                    AND tag_address LIKE 'D2%'
                    ORDER BY timestamp DESC
                    FETCH FIRST 3 ROWS ONLY
                """)
                rows = cursor.fetchall()

                logger.info(f"✓ Sample rows:")
                for row in rows:
                    logger.info(f"  - {row[0]} | {row[1]} | {row[2]} = {row[3]} ({row[4]})")

                return True
            else:
                logger.warning("⚠ No rows found in tag_values table")
                logger.warning("  Note: Check if tag_values table exists and is accessible")
                return False

    except Exception as e:
        logger.error(f"✗ Failed to verify data in Oracle: {e}", exc_info=True)
        return False


def test_csv_backup(csv_backup: CSVBackup):
    """
    Test 3: CSV Backup

    Verify that CSV backup works for failed writes.

    Args:
        csv_backup: CSVBackup instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test 3: CSV Backup")
    logger.info("=" * 60)

    try:
        # Create test items
        test_items = [
            BufferedTagValue(
                timestamp=datetime.now(),
                plc_code="KRCWO12ELOA101",
                tag_address=f"D{300 + i}",
                tag_value=float(3000 + i),
                quality="GOOD"
            )
            for i in range(5)
        ]

        # Save to CSV
        backup_file = csv_backup.save_failed_batch(test_items)
        logger.info(f"✓ CSV backup created: {backup_file}")

        # Verify file exists
        if os.path.exists(backup_file):
            file_size = os.path.getsize(backup_file)
            logger.info(f"✓ Backup file size: {file_size} bytes")

            # Get backup stats
            stats = csv_backup.stats()
            logger.info(f"✓ Backup stats:")
            logger.info(f"  - Total backups: {stats['total_backups_created']}")
            logger.info(f"  - Total items: {stats['total_items_backed_up']}")
            logger.info(f"  - File count: {stats['current_backup_file_count']}")

            return True
        else:
            logger.error(f"✗ Backup file not found: {backup_file}")
            return False

    except Exception as e:
        logger.error(f"✗ CSV backup test failed: {e}", exc_info=True)
        return False


def main():
    """
    Main test function

    Runs all end-to-end tests and reports results.
    """
    logger.info("")
    logger.info("*" * 60)
    logger.info("End-to-End Test Suite: Polling → Buffer → Oracle")
    logger.info("*" * 60)
    logger.info("")

    # Load configuration
    try:
        oracle_config = load_config_from_env()
        buffer_config = load_buffer_config_from_env()
        logger.info(f"Configuration loaded: {oracle_config.get_connect_string()}")
        logger.info("")

    except ValueError as e:
        logger.error(f"✗ Configuration error: {e}")
        return 1

    # Initialize components
    connection_pool = None
    try:
        logger.info("Initializing components...")

        circular_buffer = CircularBuffer(maxsize=buffer_config['buffer_max_size'])
        data_queue = DataQueue(maxsize=10000)
        metrics = RollingMetrics(window_seconds=300)
        csv_backup = CSVBackup(backup_dir=buffer_config['backup_file_path'])

        connection_pool = OracleConnectionPool(oracle_config)
        connection_pool.create_pool()

        logger.info("✓ All components initialized")
        logger.info("")

    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}", exc_info=True)
        if connection_pool:
            connection_pool.close()
        return 1

    # Run tests
    results = []
    try:
        results.append(("Buffer Consumer", test_buffer_consumer(data_queue, circular_buffer)))
        results.append(("Oracle Writer", test_oracle_writer(circular_buffer, connection_pool, metrics, csv_backup)))
        results.append(("CSV Backup", test_csv_backup(csv_backup)))

    finally:
        # Clean up
        if connection_pool:
            connection_pool.close()
            logger.info("")
            logger.info("✓ Connection pool closed")

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("")
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 60)

    if passed == total:
        logger.info("")
        logger.info("✓ All tests passed! End-to-end flow verified.")
        logger.info("  MVP complete: Polling → Buffer → Oracle → CSV Backup")
        return 0
    else:
        logger.error("")
        logger.error(f"✗ {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
