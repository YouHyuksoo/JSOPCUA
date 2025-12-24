"""
Data Queue Module

Thread-safe queue wrapper for storing polling data with monitoring capabilities.
"""

import queue
import logging
from typing import Optional
from .models import PollingData
from .exceptions import QueueFullError

logger = logging.getLogger(__name__)


class DataQueue:
    """
    Thread-safe wrapper around queue.Queue for polling data

    Provides monitoring capabilities and configurable queue size.
    Used by all polling threads to store collected data.

    Attributes:
        maxsize: Maximum queue size (default: 10000)
        _queue: Underlying queue.Queue instance
    """

    def __init__(self, maxsize: int = 10000):
        """
        Initialize data queue

        Args:
            maxsize: Maximum number of items in queue (default: 10000)
        """
        self.maxsize = maxsize
        self._queue = queue.Queue(maxsize=maxsize)
        logger.info(f"DataQueue initialized with maxsize={maxsize}")

    def put(self, data: PollingData, block: bool = True, timeout: Optional[float] = 30.0):
        """
        Add polling data to queue

        Args:
            data: PollingData object to add
            block: Whether to block if queue is full (default: True)
            timeout: Timeout in seconds for blocking put (default: 30s)

        Raises:
            QueueFullError: If queue is full and blocking times out
        """
        try:
            self._queue.put(data, block=block, timeout=timeout)
            logger.debug(f"Data added to queue: group={data.group_name}, size={self.size()}")
        except queue.Full:
            logger.error(f"Queue full (maxsize={self.maxsize}), cannot add data from {data.group_name}")
            raise QueueFullError(f"Data queue is full (maxsize={self.maxsize})")

    def get(self, block: bool = True, timeout: Optional[float] = None) -> PollingData:
        """
        Remove and return polling data from queue

        Args:
            block: Whether to block if queue is empty (default: True)
            timeout: Timeout in seconds for blocking get (default: None = wait forever)

        Returns:
            PollingData object

        Raises:
            queue.Empty: If queue is empty and blocking times out
        """
        try:
            data = self._queue.get(block=block, timeout=timeout)
            logger.debug(f"Data retrieved from queue: group={data.group_name}, remaining={self.size()}")
            return data
        except queue.Empty:
            logger.debug("Queue is empty, no data available")
            raise

    def get_nowait(self) -> PollingData:
        """
        Remove and return polling data without blocking

        Returns:
            PollingData object

        Raises:
            queue.Empty: If queue is empty
        """
        return self.get(block=False)

    def size(self) -> int:
        """
        Get current queue size

        Returns:
            Number of items in queue
        """
        return self._queue.qsize()

    def is_full(self) -> bool:
        """
        Check if queue is full

        Returns:
            True if queue is full, False otherwise
        """
        return self._queue.full()

    def is_empty(self) -> bool:
        """
        Check if queue is empty

        Returns:
            True if queue is empty, False otherwise
        """
        return self._queue.empty()

    def clear(self):
        """
        Clear all items from queue

        Used during shutdown to free memory.
        """
        count = 0
        try:
            while True:
                self._queue.get_nowait()
                count += 1
        except queue.Empty:
            pass

        if count > 0:
            logger.info(f"Cleared {count} items from queue")

    def __len__(self) -> int:
        """Return queue size"""
        return self.size()
