"""
Buffer Consumer Thread

Consumes polling data from Feature 3 DataQueue, expands to BufferedTagValue items,
and pushes to CircularBuffer for Oracle writer.
"""

import threading
import logging
import queue
from typing import Optional
from datetime import datetime

from .circular_buffer import CircularBuffer
from .models import BufferedTagValue
from .exceptions import BufferConsumerError

logger = logging.getLogger(__name__)


class BufferConsumer:
    """
    Background thread that consumes polling data and feeds circular buffer

    Reads PollingData from Feature 3 DataQueue, expands tag_values dict
    into individual BufferedTagValue items, and pushes to CircularBuffer.

    Thread-safe and supports graceful shutdown.

    Attributes:
        data_queue: Feature 3 DataQueue to consume from
        circular_buffer: CircularBuffer to push data to
        stop_event: Threading event for graceful shutdown
    """

    def __init__(self, data_queue, circular_buffer: CircularBuffer):
        """
        Initialize buffer consumer

        Args:
            data_queue: DataQueue instance from Feature 3 (polling.data_queue.DataQueue)
            circular_buffer: CircularBuffer instance to push data to
        """
        self.data_queue = data_queue
        self.circular_buffer = circular_buffer
        self.stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Statistics
        self.total_consumed = 0
        self.total_items_produced = 0
        self.error_count = 0
        self.last_consume_time: Optional[datetime] = None

    def start(self):
        """
        Start the consumer thread

        Raises:
            BufferConsumerError: If thread is already running
        """
        if self._thread is not None and self._thread.is_alive():
            raise BufferConsumerError("Buffer consumer thread is already running")

        logger.info("Starting buffer consumer thread...")
        self.stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="BufferConsumer", daemon=False)
        self._thread.start()
        logger.info("Buffer consumer thread started")

    def stop(self, timeout: float = 10.0) -> bool:
        """
        Stop the consumer thread gracefully

        Args:
            timeout: Maximum time to wait for thread shutdown (seconds)

        Returns:
            True if stopped successfully, False if timeout occurred
        """
        if self._thread is None or not self._thread.is_alive():
            logger.warning("Buffer consumer thread is not running")
            return True

        logger.info("Stopping buffer consumer thread...")
        self.stop_event.set()

        self._thread.join(timeout=timeout)

        if self._thread.is_alive():
            logger.error(f"Buffer consumer thread did not stop within {timeout}s")
            return False
        else:
            logger.info("Buffer consumer thread stopped successfully")
            return True

    def is_running(self) -> bool:
        """
        Check if consumer thread is running

        Returns:
            True if running, False otherwise
        """
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        """
        Main consumer loop (runs in background thread)

        Continuously consumes PollingData from DataQueue and expands to BufferedTagValue items.
        """
        logger.info("Buffer consumer loop started")

        while not self.stop_event.is_set():
            try:
                # Get polling data with timeout (allows periodic stop_event check)
                try:
                    polling_data = self.data_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue  # No data available, check stop_event and retry

                # Process polling data
                self._process_polling_data(polling_data)

            except Exception as e:
                self.error_count += 1
                logger.error(f"Error in buffer consumer loop: {e}", exc_info=True)
                # Continue processing despite errors

        # Flush remaining items before shutdown
        self._flush_remaining_data(timeout=5.0)

        logger.info(
            f"Buffer consumer loop finished. "
            f"Total consumed: {self.total_consumed}, "
            f"Items produced: {self.total_items_produced}, "
            f"Errors: {self.error_count}"
        )

    def _process_polling_data(self, polling_data):
        """
        Process a single PollingData object

        Expands tag_values dict into BufferedTagValue items and pushes to CircularBuffer.

        Args:
            polling_data: PollingData object from Feature 3
        """
        try:
            # Extract metadata
            timestamp = polling_data.timestamp
            plc_code = polling_data.plc_code
            tag_values = polling_data.tag_values
            error_tags = polling_data.error_tags

            items_produced = 0

            # Expand tag_values dict into individual BufferedTagValue items
            for tag_address, tag_value in tag_values.items():
                # Determine quality based on error status
                quality = "BAD" if tag_address in error_tags else "GOOD"

                # Create BufferedTagValue
                buffered_item = BufferedTagValue(
                    timestamp=timestamp,
                    plc_code=plc_code,
                    tag_address=tag_address,
                    tag_value=float(tag_value) if tag_value is not None else 0.0,
                    quality=quality
                )

                # Push to circular buffer
                overflow = not self.circular_buffer.put(buffered_item)

                if overflow:
                    logger.warning(
                        f"Circular buffer overflow detected "
                        f"(plc={plc_code}, tag={tag_address})"
                    )

                items_produced += 1

            # Update statistics
            self.total_consumed += 1
            self.total_items_produced += items_produced
            self.last_consume_time = datetime.now()

            logger.debug(
                f"Processed polling data: group={polling_data.group_name}, "
                f"tags={len(tag_values)}, errors={len(error_tags)}"
            )

        except Exception as e:
            self.error_count += 1
            logger.error(
                f"Error processing polling data (group={polling_data.group_name}): {e}",
                exc_info=True
            )

    def _flush_remaining_data(self, timeout: float = 5.0):
        """
        Flush remaining data from DataQueue during shutdown

        Args:
            timeout: Maximum time to spend flushing (seconds)
        """
        logger.info("Flushing remaining data from DataQueue...")

        start_time = datetime.now()
        flushed_count = 0

        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                polling_data = self.data_queue.get_nowait()
                self._process_polling_data(polling_data)
                flushed_count += 1
            except queue.Empty:
                break  # Queue is empty
            except Exception as e:
                logger.error(f"Error flushing data: {e}")
                break

        if flushed_count > 0:
            logger.info(f"Flushed {flushed_count} items during shutdown")
        else:
            logger.info("No items to flush")

    def get_stats(self) -> dict:
        """
        Get consumer statistics

        Returns:
            Dictionary with consumer stats
        """
        return {
            'is_running': self.is_running(),
            'total_consumed': self.total_consumed,
            'total_items_produced': self.total_items_produced,
            'error_count': self.error_count,
            'last_consume_time': self.last_consume_time.isoformat() if self.last_consume_time else None,
            'buffer_size': self.circular_buffer.size(),
            'buffer_utilization_pct': round(self.circular_buffer.utilization(), 1),
            'buffer_overflow_count': self.circular_buffer.overflow_count
        }
