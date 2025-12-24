"""
Oracle Writer Thread

Consumes buffered data from CircularBuffer and batch writes to Oracle Database.
"""

import threading
import logging
import time
import oracledb
from typing import Optional
from datetime import datetime

from .connection_pool import OracleConnectionPool
from .metrics import RollingMetrics
from .backup import CSVBackup
from ..buffer.circular_buffer import CircularBuffer
from ..buffer.exceptions import BufferEmptyError

logger = logging.getLogger(__name__)


class OracleWriter:
    """
    Background thread that consumes from CircularBuffer and writes to Oracle

    Implements batch writing with configurable triggers:
    - Time trigger: Write every N seconds
    - Size trigger: Write when batch reaches N items

    Whichever occurs first triggers the write.

    Attributes:
        circular_buffer: CircularBuffer to consume from
        connection_pool: OracleConnectionPool for database access
        metrics: RollingMetrics for performance tracking
        batch_size: Target batch size (default: 500)
        write_interval: Write trigger interval in seconds (default: 1.0)
    """

    def __init__(
        self,
        circular_buffer: CircularBuffer,
        connection_pool: OracleConnectionPool,
        metrics: RollingMetrics,
        csv_backup: CSVBackup,
        batch_size: int = 500,
        write_interval: float = 1.0
    ):
        """
        Initialize Oracle writer

        Args:
            circular_buffer: CircularBuffer instance to consume from
            connection_pool: OracleConnectionPool instance
            metrics: RollingMetrics instance for tracking
            csv_backup: CSVBackup instance for failed writes
            batch_size: Target batch size (100-1000, default: 500)
            write_interval: Write trigger interval in seconds (default: 1.0)
        """
        self.circular_buffer = circular_buffer
        self.connection_pool = connection_pool
        self.metrics = metrics
        self.csv_backup = csv_backup
        self.batch_size = batch_size
        self.write_interval = write_interval

        self.stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Validate batch size
        if batch_size < 100 or batch_size > 1000:
            logger.warning(f"Batch size {batch_size} outside recommended range 100-1000")

    def start(self):
        """
        Start the writer thread

        Raises:
            RuntimeError: If thread is already running
        """
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("Oracle writer thread is already running")

        logger.info(
            f"Starting Oracle writer thread "
            f"(batch_size={self.batch_size}, interval={self.write_interval}s)..."
        )
        self.stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="OracleWriter", daemon=False)
        self._thread.start()
        logger.info("Oracle writer thread started")

    def stop(self, timeout: float = 10.0) -> bool:
        """
        Stop the writer thread gracefully

        Flushes remaining buffered data before stopping.

        Args:
            timeout: Maximum time to wait for thread shutdown (seconds)

        Returns:
            True if stopped successfully, False if timeout occurred
        """
        if self._thread is None or not self._thread.is_alive():
            logger.warning("Oracle writer thread is not running")
            return True

        logger.info("Stopping Oracle writer thread...")
        self.stop_event.set()

        self._thread.join(timeout=timeout)

        if self._thread.is_alive():
            logger.error(f"Oracle writer thread did not stop within {timeout}s")
            return False
        else:
            logger.info("Oracle writer thread stopped successfully")
            return True

    def is_running(self) -> bool:
        """
        Check if writer thread is running

        Returns:
            True if running, False otherwise
        """
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        """
        Main writer loop (runs in background thread)

        Implements time-based and size-based write triggers.
        """
        logger.info("Oracle writer loop started")

        last_write_time = time.time()

        while not self.stop_event.is_set():
            try:
                current_time = time.time()
                time_elapsed = current_time - last_write_time
                buffer_size = self.circular_buffer.size()

                # Check write triggers
                time_trigger = time_elapsed >= self.write_interval
                size_trigger = buffer_size >= self.batch_size

                if time_trigger or size_trigger:
                    if buffer_size > 0:
                        # Determine actual batch size to write
                        actual_batch_size = min(buffer_size, self.batch_size)

                        # Write batch
                        success = self._write_batch(actual_batch_size)

                        if success:
                            last_write_time = current_time

                        # Log trigger reason
                        trigger_reason = "size" if size_trigger else "time"
                        logger.debug(
                            f"Write triggered by {trigger_reason} "
                            f"(buffer={buffer_size}, batch={actual_batch_size})"
                        )
                    else:
                        # Buffer empty, reset timer
                        last_write_time = current_time

                # Sleep briefly to avoid busy-waiting
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in Oracle writer loop: {e}", exc_info=True)
                time.sleep(1.0)  # Back off on error

        # Flush remaining data before shutdown
        self._flush_remaining_data()

        logger.info("Oracle writer loop finished")

    def _write_batch(self, count: int) -> bool:
        """
        Write a batch of items to Oracle using executemany() with retry logic

        Implements exponential backoff retry: 3 attempts with delays of 1s, 2s, 4s.

        Args:
            count: Number of items to write

        Returns:
            True if successful, False otherwise
        """
        try:
            start_time = time.time()

            # Get items from buffer
            items = self.circular_buffer.get(count)

            if not items:
                logger.warning("No items retrieved from buffer")
                return False

            # Execute batch insert with retry logic
            success = self._execute_batch_insert_with_retry(items)

            latency_ms = (time.time() - start_time) * 1000

            # Record metrics
            self.metrics.record_batch_write(
                batch_size=len(items),
                latency_ms=latency_ms,
                success=success
            )

            if success:
                logger.debug(f"Batch write completed: {len(items)} items in {latency_ms:.1f}ms")
            else:
                logger.error(f"Batch write failed after all retries: {len(items)} items")

                # Backup failed batch to CSV
                try:
                    backup_file = self.csv_backup.save_failed_batch(items)
                    logger.warning(f"Failed batch saved to: {backup_file}")
                except Exception as e:
                    logger.error(f"Failed to backup batch to CSV: {e}", exc_info=True)

            return success

        except BufferEmptyError:
            logger.warning("Buffer empty, cannot write batch")
            return False
        except Exception as e:
            logger.error(f"Batch write failed: {e}", exc_info=True)
            self.metrics.record_batch_write(batch_size=0, latency_ms=0, success=False)
            return False

    def _execute_batch_insert_with_retry(self, items: list, max_retries: int = 3) -> bool:
        """
        Execute batch insert with exponential backoff retry

        Retry delays: 1s, 2s, 4s (exponential backoff)

        Args:
            items: List of BufferedTagValue items to insert
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            True if successful, False if all retries exhausted
        """
        retry_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s

        for attempt in range(max_retries):
            try:
                success = self._execute_batch_insert(items)

                if success:
                    if attempt > 0:
                        logger.info(f"Batch insert succeeded on retry {attempt + 1}/{max_retries}")
                    return True

                # Partial success is considered success
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(
                        f"Batch insert failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay}s..."
                    )
                    time.sleep(delay)

            except oracledb.Error as e:
                logger.error(
                    f"Oracle error on attempt {attempt + 1}/{max_retries}: {e}",
                    exc_info=(attempt == max_retries - 1)  # Full trace on last attempt
                )

                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries} retry attempts exhausted")

            except Exception as e:
                logger.error(
                    f"Unexpected error on attempt {attempt + 1}/{max_retries}: {e}",
                    exc_info=True
                )
                # Don't retry on unexpected errors
                break

        return False

    def _execute_batch_insert(self, items: list) -> bool:
        """
        Execute batch insert using executemany() with batcherrors=True

        Args:
            items: List of BufferedTagValue items to insert

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare SQL INSERT statement
            insert_sql = """
                INSERT INTO tag_values (timestamp, plc_code, tag_address, tag_value, quality)
                VALUES (:timestamp, :plc_code, :tag_address, :tag_value, :quality)
            """

            # Convert BufferedTagValue items to parameter list
            parameters = [
                {
                    'timestamp': item.timestamp,
                    'plc_code': item.plc_code,
                    'tag_address': item.tag_address,
                    'tag_value': item.tag_value,
                    'quality': item.quality
                }
                for item in items
            ]

            # Execute batch insert with batcherrors=True for partial success handling
            with self.connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(insert_sql, parameters, batcherrors=True)

                # Check for batch errors
                errors = cursor.getbatcherrors()
                if errors:
                    logger.warning(f"Batch insert completed with {len(errors)} errors:")
                    for error in errors[:5]:  # Log first 5 errors only
                        logger.warning(f"  Row {error.offset}: {error.message}")

                    # If all rows failed, consider it a failure
                    if len(errors) >= len(items):
                        logger.error(f"All {len(items)} rows failed in batch insert")
                        return False

                    # Partial success
                    logger.info(
                        f"Batch insert partial success: "
                        f"{len(items) - len(errors)}/{len(items)} rows inserted"
                    )

                # Commit transaction
                conn.commit()

                logger.debug(f"Batch insert committed: {len(items)} rows")

                return True

        except oracledb.Error as e:
            logger.error(f"Oracle error during batch insert: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error during batch insert: {e}", exc_info=True)
            return False

    def _flush_remaining_data(self):
        """
        Flush remaining buffered data during shutdown

        Writes all remaining items in buffer before thread exits.
        """
        logger.info("Flushing remaining data from buffer...")

        remaining = self.circular_buffer.size()

        if remaining == 0:
            logger.info("No items to flush")
            return

        logger.info(f"Flushing {remaining} items...")

        # Write in batches until buffer is empty
        flushed_count = 0
        while self.circular_buffer.size() > 0:
            batch_size = min(self.circular_buffer.size(), self.batch_size)
            success = self._write_batch(batch_size)

            if success:
                flushed_count += batch_size
            else:
                logger.error("Failed to flush batch, stopping flush")
                break

        logger.info(f"Flushed {flushed_count}/{remaining} items during shutdown")

    def get_stats(self) -> dict:
        """
        Get writer statistics

        Returns:
            Dictionary with writer stats and metrics
        """
        return {
            'is_running': self.is_running(),
            'batch_size': self.batch_size,
            'write_interval': self.write_interval,
            'buffer_size': self.circular_buffer.size(),
            'buffer_utilization_pct': round(self.circular_buffer.utilization(), 1),
            'metrics': self.metrics.stats()
        }
