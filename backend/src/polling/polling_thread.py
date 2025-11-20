"""
Polling Thread Base Class

Abstract base class for polling threads (FIXED and HANDSHAKE modes).
"""

import threading
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from .models import PollingGroup, PollingData, ThreadState, PollingMode
from .data_queue import DataQueue
from .exceptions import PollingThreadError
from .polling_logger import get_failure_logger

logger = logging.getLogger(__name__)
failure_logger = get_failure_logger()


class PollingThread(ABC):
    """
    Abstract base class for polling threads

    Provides common functionality for both FIXED and HANDSHAKE polling modes.
    Each polling group runs in its own thread instance.

    Attributes:
        group: PollingGroup configuration
        pool_manager: PLC pool manager for reading tags
        data_queue: Shared data queue for storing results
        thread: Threading.Thread instance
        stop_event: Event to signal thread shutdown
        state: Current thread state
        last_poll_time: Timestamp of last poll
        total_polls: Total number of polls attempted
        success_count: Number of successful polls
        error_count: Number of failed polls
        avg_poll_time_ms: Running average of poll times
    """

    def __init__(self, group: PollingGroup, pool_manager, data_queue: DataQueue):
        """
        Initialize polling thread

        Args:
            group: PollingGroup configuration
            pool_manager: PoolManager instance from Feature 2
            data_queue: DataQueue for storing polling results
        """
        self.group = group
        self.pool_manager = pool_manager
        self.data_queue = data_queue

        # Thread management
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.state = ThreadState.STOPPED

        # Dedicated PLC connection (acquired on start, released on stop)
        self._plc_connection = None
        self._connection_pool = None

        # Statistics
        self.last_poll_time: Optional[datetime] = None
        self.total_polls = 0
        self.success_count = 0
        self.error_count = 0
        self.avg_poll_time_ms = 0.0
        self._poll_times = []  # Track recent poll times for averaging

        # Connection failure tracking for backoff strategy
        self.consecutive_failures = 0
        self.last_connection_check = None
        self.skip_polls_until = None  # Timestamp until which to skip polling
        self.last_error_message: Optional[str] = None  # Last error message for status reporting

        logger.info(f"PollingThread initialized: group={group.group_name}, mode={group.mode.value}")

    def reset_statistics(self):
        """
        Reset all statistics and error tracking

        Called when starting a polling group to clear previous error history.
        """
        self.total_polls = 0
        self.success_count = 0
        self.error_count = 0
        self.avg_poll_time_ms = 0.0
        self._poll_times = []
        self.consecutive_failures = 0
        self.last_error_message = None
        self.skip_polls_until = None
        logger.info(f"Statistics reset for group {self.group.group_name}")

    def start(self):
        """
        Start the polling thread

        Creates and starts a new thread that runs the polling loop.
        Acquires a dedicated PLC connection that will be held until stop().
        Resets statistics and error history before starting.
        """
        if self.state == ThreadState.RUNNING:
            logger.warning(f"Thread already running for group {self.group.group_name}")
            return

        # Reset statistics and error history
        self.reset_statistics()

        # Acquire dedicated PLC connection for this thread
        try:
            self._connection_pool = self.pool_manager._get_pool(self.group.plc_code)
            self._plc_connection = self._connection_pool.get_connection(timeout=10)
            logger.info(f"✅ [{self.group.group_name}] Acquired dedicated PLC connection")
        except Exception as e:
            logger.error(f"❌ [{self.group.group_name}] Failed to acquire PLC connection: {e}")
            self.last_error_message = f"Failed to acquire PLC connection: {e}"
            self.state = ThreadState.ERROR
            raise

        self.stop_event.clear()
        self.state = ThreadState.RUNNING
        self.thread = threading.Thread(
            target=self._run_wrapper,
            name=f"Polling-{self.group.group_name}",
            daemon=False  # Ensure clean shutdown
        )
        self.thread.start()
        logger.info(f"Started polling thread for group {self.group.group_name}")

    def stop(self, timeout: float = 5.0):
        """
        Stop the polling thread gracefully

        Sets stop event and waits for thread to terminate.
        Releases the dedicated PLC connection back to the pool.
        Thread will complete current polling cycle before stopping.

        Args:
            timeout: Maximum time to wait for thread termination (seconds)
        """
        if self.state != ThreadState.RUNNING:
            logger.warning(f"Thread not running for group {self.group.group_name}")
            # Still try to release connection if it exists
            self._release_connection()
            return

        logger.info(f"Stopping polling thread for group {self.group.group_name}")
        self.state = ThreadState.STOPPING
        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
            if self.thread.is_alive():
                logger.error(f"Thread did not stop within {timeout}s for group {self.group.group_name}")
                self.state = ThreadState.ERROR
            else:
                self.state = ThreadState.STOPPED
                logger.info(f"Polling thread stopped for group {self.group.group_name}")
        else:
            self.state = ThreadState.STOPPED

        # Release PLC connection back to pool
        self._release_connection()

    def _release_connection(self):
        """Release the dedicated PLC connection back to the pool"""
        if self._plc_connection and self._connection_pool:
            try:
                self._connection_pool.return_connection(self._plc_connection)
                logger.info(f"🔓 [{self.group.group_name}] Released PLC connection back to pool")
            except Exception as e:
                logger.error(f"❌ [{self.group.group_name}] Error releasing connection: {e}")
            finally:
                self._plc_connection = None
                self._connection_pool = None

    def _run_wrapper(self):
        """
        Wrapper around run() to catch unhandled exceptions

        Ensures thread state is properly updated even if run() crashes.
        Always releases the dedicated connection on exit.
        """
        try:
            self.run()
        except Exception as e:
            logger.error(f"Unhandled exception in polling thread {self.group.group_name}: {e}", exc_info=True)
            self.state = ThreadState.ERROR
            raise PollingThreadError(f"Thread crashed for group {self.group.group_name}: {e}")
        finally:
            # Always release connection when thread exits
            self._release_connection()
            if self.state != ThreadState.ERROR:
                self.state = ThreadState.STOPPED

    @abstractmethod
    def run(self):
        """
        Main polling loop

        Must be implemented by subclasses (FixedPollingThread, HandshakePollingThread).
        Should check stop_event periodically and complete current cycle before exiting.
        """
        pass

    def execute_poll(self) -> bool:
        """
        Execute a single polling cycle

        Reads all tags for this group using the dedicated connection.
        Uses the connection acquired in start() - no get/return overhead!

        Returns:
            True if poll succeeded, False if poll failed
        """
        current_time = time.perf_counter()

        # Check if we should skip this poll due to previous connection failures
        if self.skip_polls_until and current_time < self.skip_polls_until:
            remaining = self.skip_polls_until - current_time
            logger.debug(
                f"Skipping poll for group={self.group.group_name} "
                f"(PLC connection unavailable, retry in {remaining:.1f}s)"
            )
            return False

        # Ensure we have a dedicated connection
        if not self._plc_connection or not self._plc_connection.client:
            logger.error(f"❌ [{self.group.group_name}] No dedicated connection available")
            self._handle_connection_unavailable()
            return False

        start_time = time.perf_counter()

        try:
            # Read tags directly using dedicated connection (no pool get/return!)
            tag_values = self._plc_connection.client.read_batch(self.group.tag_addresses)

            # Calculate poll time
            end_time = time.perf_counter()
            poll_time_ms = (end_time - start_time) * 1000

            # Create polling data
            polling_data = PollingData(
                timestamp=datetime.now(),
                group_id=self.group.group_id,
                group_name=self.group.group_name,
                plc_code=self.group.plc_code,
                mode=self.group.mode,
                group_category=self.group.group_category,
                tag_values=tag_values,
                poll_time_ms=poll_time_ms,
                error_tags={}
            )

            # Store in queue
            self.data_queue.put(polling_data)

            # Update statistics
            self.last_poll_time = polling_data.timestamp
            self.total_polls += 1
            self.success_count += 1
            self._update_avg_poll_time(poll_time_ms)

            # Reset error counter on success
            if self._plc_connection:
                self._plc_connection.reset_error()

            # Reset failure counter on success
            if self.consecutive_failures > 0:
                logger.info(
                    f"PLC connection recovered for group={self.group.group_name} "
                    f"after {self.consecutive_failures} failures"
                )
                self.consecutive_failures = 0
                self.skip_polls_until = None
                self.last_error_message = None  # Clear error message on success

            logger.debug(
                f"Poll successful: group={self.group.group_name}, "
                f"tags={len(tag_values)}, time={poll_time_ms:.2f}ms"
            )
            return True

        except Exception as e:
            # Calculate poll time even on error
            end_time = time.perf_counter()
            poll_time_ms = (end_time - start_time) * 1000

            # Update statistics
            self.total_polls += 1
            self.error_count += 1

            # Increment error counter on dedicated connection
            if self._plc_connection:
                self._plc_connection.increment_error()

            # Log to console
            logger.error(
                f"Poll failed: group={self.group.group_name}, "
                f"error={str(e)}, time={poll_time_ms:.2f}ms"
            )

            # Log failure to daily folder with detailed information
            error_type = type(e).__name__
            error_message = str(e)

            # Store last error message for status reporting
            self.last_error_message = f"{error_type}: {error_message}"

            # Check if it's a connection error - apply backoff strategy
            if "connection" in error_message.lower() or "connect" in error_message.lower():
                self._handle_connection_failure()

                failure_logger.log_connection_failure(
                    plc_code=self.group.plc_code,
                    group_name=self.group.group_name,
                    ip_address="unknown",  # PoolManager should provide this
                    port=5010,  # Default port
                    error_message=error_message,
                    connection_timeout=5
                )
            elif "timeout" in error_message.lower():
                failure_logger.log_timeout_failure(
                    plc_code=self.group.plc_code,
                    group_name=self.group.group_name,
                    tag_addresses=self.group.tag_addresses,
                    timeout_ms=poll_time_ms
                )
            else:
                failure_logger.log_read_failure(
                    plc_code=self.group.plc_code,
                    group_name=self.group.group_name,
                    tag_addresses=self.group.tag_addresses,
                    error_message=error_message,
                    poll_duration_ms=poll_time_ms,
                    response_code=None
                )

            return False

    def _handle_connection_unavailable(self):
        """
        Handle PLC connection unavailable (before attempting to poll)

        Applies exponential backoff strategy to avoid wasting resources
        on repeated connection attempts.
        """
        self.consecutive_failures += 1

        # Exponential backoff: 5s, 10s, 30s, 60s, 120s, then cap at 300s (5min)
        backoff_intervals = [5, 10, 30, 60, 120, 300]
        backoff_index = min(self.consecutive_failures - 1, len(backoff_intervals) - 1)
        backoff_seconds = backoff_intervals[backoff_index]

        self.skip_polls_until = time.perf_counter() + backoff_seconds

        # Store error message for status reporting
        self.last_error_message = f"PLC {self.group.plc_code} unavailable (connection pool has no available connections)"

        logger.warning(
            f"PLC {self.group.plc_code} unavailable for group={self.group.group_name} "
            f"(failure #{self.consecutive_failures}). Skipping polls for {backoff_seconds}s"
        )

    def _handle_connection_failure(self):
        """
        Handle connection failure during polling attempt

        Similar to _handle_connection_unavailable but called after
        an actual connection error occurred.
        """
        self.consecutive_failures += 1

        # Same backoff strategy
        backoff_intervals = [5, 10, 30, 60, 120, 300]
        backoff_index = min(self.consecutive_failures - 1, len(backoff_intervals) - 1)
        backoff_seconds = backoff_intervals[backoff_index]

        self.skip_polls_until = time.perf_counter() + backoff_seconds

        logger.warning(
            f"Connection failed for PLC {self.group.plc_code}, group={self.group.group_name} "
            f"(consecutive failure #{self.consecutive_failures}). Backing off for {backoff_seconds}s"
        )

    def _update_avg_poll_time(self, poll_time_ms: float):
        """
        Update running average of poll times

        Keeps last 100 poll times for averaging.

        Args:
            poll_time_ms: Poll time in milliseconds
        """
        self._poll_times.append(poll_time_ms)
        if len(self._poll_times) > 100:
            self._poll_times.pop(0)
        self.avg_poll_time_ms = sum(self._poll_times) / len(self._poll_times)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current thread status

        Returns:
            Dictionary with status information including connection state and error messages
        """
        # Calculate success rate
        success_rate = 0.0
        if self.total_polls > 0:
            success_rate = (self.success_count / self.total_polls) * 100

        # Calculate next retry time if in backoff
        next_retry_in = None
        if self.skip_polls_until:
            remaining = self.skip_polls_until - time.perf_counter()
            if remaining > 0:
                next_retry_in = round(remaining, 1)

        return {
            "group_id": self.group.group_id,
            "group_name": self.group.group_name,
            "mode": self.group.mode.value,
            "state": self.state.value,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "total_polls": self.total_polls,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": round(success_rate, 1),
            "avg_poll_time_ms": round(self.avg_poll_time_ms, 2),
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error_message,
            "next_retry_in": next_retry_in  # Seconds until next retry (None if not in backoff)
        }

    def is_running(self) -> bool:
        """Check if thread is running"""
        return self.state == ThreadState.RUNNING
