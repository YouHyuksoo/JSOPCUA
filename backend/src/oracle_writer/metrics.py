"""
Rolling Metrics Tracker

Time-windowed metrics collection using collections.deque for 5-minute rolling averages.
"""

import threading
from collections import deque
from typing import Optional
from datetime import datetime, timedelta


class RollingMetrics:
    """
    Thread-safe rolling metrics tracker for time-windowed averages

    Tracks metrics over a configurable time window (default: 5 minutes).
    Automatically removes expired data points for accurate rolling averages.

    Attributes:
        window_seconds: Time window in seconds (default: 300 = 5 minutes)
    """

    def __init__(self, window_seconds: int = 300):
        """
        Initialize rolling metrics tracker

        Args:
            window_seconds: Time window for rolling averages (default: 300 = 5 minutes)
        """
        self.window_seconds = window_seconds
        self._window_duration = timedelta(seconds=window_seconds)

        # Deques store (timestamp, value) tuples
        self._batch_sizes = deque()
        self._write_latencies = deque()
        self._overflow_events = deque()

        self._lock = threading.Lock()

        # Cumulative counters (not time-windowed)
        self.total_successful_writes = 0
        self.total_failed_writes = 0
        self.total_items_written = 0
        self.last_write_time: Optional[datetime] = None

    def _prune_old_data(self, data_deque: deque):
        """
        Remove data points older than the time window

        Args:
            data_deque: Deque containing (timestamp, value) tuples
        """
        now = datetime.now()
        cutoff_time = now - self._window_duration

        # Remove expired items from the left (oldest)
        while data_deque and data_deque[0][0] < cutoff_time:
            data_deque.popleft()

    def record_batch_write(self, batch_size: int, latency_ms: float, success: bool):
        """
        Record a batch write operation

        Args:
            batch_size: Number of items in the batch
            latency_ms: Write latency in milliseconds
            success: Whether the write succeeded
        """
        with self._lock:
            now = datetime.now()

            # Record metrics
            self._batch_sizes.append((now, batch_size))
            self._write_latencies.append((now, latency_ms))

            # Update cumulative counters
            if success:
                self.total_successful_writes += 1
                self.total_items_written += batch_size
            else:
                self.total_failed_writes += 1

            self.last_write_time = now

            # Prune old data
            self._prune_old_data(self._batch_sizes)
            self._prune_old_data(self._write_latencies)

    def record_overflow(self, count: int = 1):
        """
        Record buffer overflow event(s)

        Args:
            count: Number of overflow events (default: 1)
        """
        with self._lock:
            now = datetime.now()
            self._overflow_events.append((now, count))

            # Prune old data
            self._prune_old_data(self._overflow_events)

    def get_avg_batch_size(self) -> float:
        """
        Get average batch size over the time window

        Returns:
            Average batch size (0.0 if no data)
        """
        with self._lock:
            self._prune_old_data(self._batch_sizes)

            if not self._batch_sizes:
                return 0.0

            total = sum(size for _, size in self._batch_sizes)
            return total / len(self._batch_sizes)

    def get_avg_write_latency(self) -> float:
        """
        Get average write latency over the time window

        Returns:
            Average latency in milliseconds (0.0 if no data)
        """
        with self._lock:
            self._prune_old_data(self._write_latencies)

            if not self._write_latencies:
                return 0.0

            total = sum(latency for _, latency in self._write_latencies)
            return total / len(self._write_latencies)

    def get_overflow_count(self) -> int:
        """
        Get total overflow events in the time window

        Returns:
            Number of overflow events
        """
        with self._lock:
            self._prune_old_data(self._overflow_events)
            return sum(count for _, count in self._overflow_events)

    def get_overflow_rate(self) -> float:
        """
        Get overflow rate as percentage of total items

        Returns:
            Overflow rate percentage (0.0-100.0)
        """
        with self._lock:
            overflow_count = self.get_overflow_count()

            if self.total_items_written == 0:
                return 0.0

            # Calculate rate over the time window
            return (overflow_count / (self.total_items_written + overflow_count)) * 100.0

    def get_write_success_rate(self) -> float:
        """
        Get write success rate percentage (cumulative, not time-windowed)

        Returns:
            Success rate percentage (0.0-100.0)
        """
        with self._lock:
            total_writes = self.total_successful_writes + self.total_failed_writes

            if total_writes == 0:
                return 0.0

            return (self.total_successful_writes / total_writes) * 100.0

    def get_write_count_in_window(self) -> int:
        """
        Get number of write operations in the time window

        Returns:
            Number of writes
        """
        with self._lock:
            self._prune_old_data(self._batch_sizes)
            return len(self._batch_sizes)

    def get_items_written_in_window(self) -> int:
        """
        Get total items written in the time window

        Returns:
            Total items written
        """
        with self._lock:
            self._prune_old_data(self._batch_sizes)
            return sum(size for _, size in self._batch_sizes)

    def get_throughput(self) -> float:
        """
        Get average throughput in items per second over the time window

        Returns:
            Items per second (0.0 if no data)
        """
        with self._lock:
            self._prune_old_data(self._batch_sizes)

            if not self._batch_sizes:
                return 0.0

            # Calculate actual time span of data
            oldest_time = self._batch_sizes[0][0]
            newest_time = self._batch_sizes[-1][0]
            time_span_seconds = (newest_time - oldest_time).total_seconds()

            if time_span_seconds == 0:
                return 0.0

            total_items = sum(size for _, size in self._batch_sizes)
            return total_items / time_span_seconds

    def stats(self) -> dict:
        """
        Get comprehensive statistics (thread-safe)

        Returns:
            Dictionary with all metrics (rolling and cumulative)
        """
        with self._lock:
            # Prune all data structures
            self._prune_old_data(self._batch_sizes)
            self._prune_old_data(self._write_latencies)
            self._prune_old_data(self._overflow_events)

            # Calculate rolling metrics
            avg_batch_size = self.get_avg_batch_size()
            avg_latency = self.get_avg_write_latency()
            overflow_count = self.get_overflow_count()
            write_count = len(self._batch_sizes)
            items_in_window = sum(size for _, size in self._batch_sizes)

            # Calculate throughput
            throughput = 0.0
            if len(self._batch_sizes) > 1:
                oldest_time = self._batch_sizes[0][0]
                newest_time = self._batch_sizes[-1][0]
                time_span_seconds = (newest_time - oldest_time).total_seconds()
                if time_span_seconds > 0:
                    throughput = items_in_window / time_span_seconds

            return {
                # Rolling metrics (time-windowed)
                'window_seconds': self.window_seconds,
                'avg_batch_size': round(avg_batch_size, 1),
                'avg_write_latency_ms': round(avg_latency, 1),
                'write_count_in_window': write_count,
                'items_written_in_window': items_in_window,
                'overflow_count_in_window': overflow_count,
                'throughput_items_per_sec': round(throughput, 1),

                # Cumulative metrics (all-time)
                'total_successful_writes': self.total_successful_writes,
                'total_failed_writes': self.total_failed_writes,
                'total_items_written': self.total_items_written,
                'success_rate_pct': round(self.get_write_success_rate(), 1),
                'last_write_time': self.last_write_time.isoformat() if self.last_write_time else None
            }

    def reset(self):
        """
        Reset all metrics (thread-safe)

        Clears all time-windowed data and cumulative counters.
        Use with caution in production.
        """
        with self._lock:
            self._batch_sizes.clear()
            self._write_latencies.clear()
            self._overflow_events.clear()

            self.total_successful_writes = 0
            self.total_failed_writes = 0
            self.total_items_written = 0
            self.last_write_time = None
