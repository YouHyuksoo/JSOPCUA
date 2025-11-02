"""
Start Buffer and Oracle Writer

Launch BufferConsumer and OracleWriter threads to consume polling data
and persist to Oracle Database.

Usage:
    python backend/src/scripts/start_buffer_writer.py

Environment Variables Required:
    - ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME
    - ORACLE_USERNAME, ORACLE_PASSWORD
    - BUFFER_MAX_SIZE, BUFFER_BATCH_SIZE, BUFFER_WRITE_INTERVAL
    - BACKUP_FILE_PATH
"""

import sys
import os
import signal
import time
from pathlib import Path

# Add backend/src to path for imports
backend_src = Path(__file__).parent.parent
sys.path.insert(0, str(backend_src))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend/logs/buffer_writer.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Import components
from buffer.circular_buffer import CircularBuffer
from buffer.buffer_consumer import BufferConsumer
from oracle_writer.config import load_config_from_env, load_buffer_config_from_env
from oracle_writer.connection_pool import OracleConnectionPool
from oracle_writer.metrics import RollingMetrics
from oracle_writer.backup import CSVBackup
from oracle_writer.writer import OracleWriter

# Import Feature 3 DataQueue (assumes polling engine is running)
from polling.data_queue import DataQueue


# Global variables for graceful shutdown
buffer_consumer = None
oracle_writer = None
connection_pool = None


def signal_handler(signum, frame):
    """
    Handle termination signals for graceful shutdown

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")

    # Stop threads
    if buffer_consumer:
        logger.info("Stopping buffer consumer...")
        buffer_consumer.stop(timeout=10.0)

    if oracle_writer:
        logger.info("Stopping Oracle writer...")
        oracle_writer.stop(timeout=10.0)

    # Close connection pool
    if connection_pool:
        logger.info("Closing Oracle connection pool...")
        connection_pool.close()

    logger.info("Graceful shutdown complete")
    sys.exit(0)


def main():
    """
    Main function to start buffer consumer and Oracle writer

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    global buffer_consumer, oracle_writer, connection_pool

    logger.info("=" * 60)
    logger.info("Starting Buffer and Oracle Writer")
    logger.info("=" * 60)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        oracle_config = load_config_from_env()
        buffer_config = load_buffer_config_from_env()

        logger.info(f"Oracle: {oracle_config.get_connect_string()}")
        logger.info(f"Buffer max size: {buffer_config['buffer_max_size']}")
        logger.info(f"Batch size: {buffer_config['buffer_batch_size']}")
        logger.info(f"Write interval: {buffer_config['buffer_write_interval']}s")
        logger.info(f"Backup path: {buffer_config['backup_file_path']}")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1

    try:
        # Initialize components
        logger.info("")
        logger.info("Initializing components...")

        # Circular buffer
        circular_buffer = CircularBuffer(maxsize=buffer_config['buffer_max_size'])
        logger.info(f"✓ CircularBuffer initialized (maxsize={buffer_config['buffer_max_size']})")

        # Oracle connection pool
        connection_pool = OracleConnectionPool(oracle_config)
        connection_pool.create_pool()
        logger.info(f"✓ Oracle connection pool created")

        # Rolling metrics
        metrics = RollingMetrics(window_seconds=300)  # 5-minute window
        logger.info(f"✓ RollingMetrics initialized (5-minute window)")

        # CSV backup
        csv_backup = CSVBackup(backup_dir=buffer_config['backup_file_path'])
        logger.info(f"✓ CSVBackup initialized (dir={buffer_config['backup_file_path']})")

        # Data queue (from Feature 3 - assumes polling engine is running)
        # NOTE: In real deployment, DataQueue should be shared with polling engine
        # For now, create a new instance for demonstration
        data_queue = DataQueue(maxsize=10000)
        logger.info(f"✓ DataQueue initialized (maxsize=10000)")
        logger.warning("  WARNING: DataQueue is standalone. In production, share with polling engine.")

        # Buffer consumer
        buffer_consumer = BufferConsumer(
            data_queue=data_queue,
            circular_buffer=circular_buffer
        )
        logger.info(f"✓ BufferConsumer initialized")

        # Oracle writer
        oracle_writer = OracleWriter(
            circular_buffer=circular_buffer,
            connection_pool=connection_pool,
            metrics=metrics,
            csv_backup=csv_backup,
            batch_size=buffer_config['buffer_batch_size'],
            write_interval=buffer_config['buffer_write_interval']
        )
        logger.info(f"✓ OracleWriter initialized")

    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        if connection_pool:
            connection_pool.close()
        return 1

    try:
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Kill command

        # Start threads
        logger.info("")
        logger.info("Starting threads...")

        buffer_consumer.start()
        logger.info("✓ BufferConsumer thread started")

        oracle_writer.start()
        logger.info("✓ OracleWriter thread started")

        logger.info("")
        logger.info("=" * 60)
        logger.info("Buffer and Oracle Writer running")
        logger.info("Press Ctrl+C to stop gracefully")
        logger.info("=" * 60)
        logger.info("")

        # Main loop - periodically print statistics
        while True:
            time.sleep(30)  # Print stats every 30 seconds

            # Buffer consumer stats
            consumer_stats = buffer_consumer.get_stats()
            logger.info(
                f"BufferConsumer: consumed={consumer_stats['total_consumed']}, "
                f"produced={consumer_stats['total_items_produced']}, "
                f"errors={consumer_stats['error_count']}"
            )

            # Oracle writer stats
            writer_stats = oracle_writer.get_stats()
            writer_metrics = writer_stats['metrics']
            logger.info(
                f"OracleWriter: buffer={writer_stats['buffer_size']}/{buffer_config['buffer_max_size']} "
                f"({writer_stats['buffer_utilization_pct']:.1f}%), "
                f"writes={writer_metrics['total_successful_writes']}/{writer_metrics['total_successful_writes'] + writer_metrics['total_failed_writes']}, "
                f"avg_latency={writer_metrics['avg_write_latency_ms']:.1f}ms"
            )

            # CSV backup stats
            backup_stats = csv_backup.stats()
            logger.info(
                f"CSVBackup: files={backup_stats['current_backup_file_count']}, "
                f"total_backups={backup_stats['total_backups_created']}"
            )

            logger.info("")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        signal_handler(signal.SIGINT, None)

    except Exception as e:
        logger.error(f"Runtime error: {e}", exc_info=True)

        # Cleanup
        if buffer_consumer:
            buffer_consumer.stop(timeout=10.0)
        if oracle_writer:
            oracle_writer.stop(timeout=10.0)
        if connection_pool:
            connection_pool.close()

        return 1

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
