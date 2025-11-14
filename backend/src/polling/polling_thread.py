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

        # Statistics
        self.last_poll_time: Optional[datetime] = None
        self.total_polls = 0
        self.success_count = 0
        self.error_count = 0
        self.avg_poll_time_ms = 0.0
        self._poll_times = []  # Track recent poll times for averaging

        logger.info(f"PollingThread initialized: group={group.group_name}, mode={group.mode.value}")

    def start(self):
        """
        Start the polling thread

        Creates and starts a new thread that runs the polling loop.
        """
        if self.state == ThreadState.RUNNING:
            logger.warning(f"Thread already running for group {self.group.group_name}")
            return

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
        Thread will complete current polling cycle before stopping.

        Args:
            timeout: Maximum time to wait for thread termination (seconds)
        """
        if self.state != ThreadState.RUNNING:
            logger.warning(f"Thread not running for group {self.group.group_name}")
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

    def _run_wrapper(self):
        """
        Wrapper around run() to catch unhandled exceptions

        Ensures thread state is properly updated even if run() crashes.
        """
        try:
            self.run()
        except Exception as e:
            logger.error(f"Unhandled exception in polling thread {self.group.group_name}: {e}", exc_info=True)
            self.state = ThreadState.ERROR
            raise PollingThreadError(f"Thread crashed for group {self.group.group_name}: {e}")
        finally:
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

        Reads all tags for this group and stores result in data queue.

        Returns:
            True if poll succeeded, False if poll failed
        """
        start_time = time.perf_counter()

        try:
            # Read tags using PoolManager
            tag_values = self.pool_manager.read_batch(
                self.group.plc_code,
                self.group.tag_addresses
            )

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

            # Log to console
            logger.error(
                f"Poll failed: group={self.group.group_name}, "
                f"error={str(e)}, time={poll_time_ms:.2f}ms"
            )

            # Log failure to daily folder with detailed information
            error_type = type(e).__name__
            error_message = str(e)

            # Determine specific error type
            if "connection" in error_message.lower() or "connect" in error_message.lower():
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
            Dictionary with status information
        """
        return {
            "group_id": self.group.group_id,
            "group_name": self.group.group_name,
            "mode": self.group.mode.value,
            "state": self.state.value,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "total_polls": self.total_polls,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "avg_poll_time_ms": round(self.avg_poll_time_ms, 2)
        }

    def is_running(self) -> bool:
        """Check if thread is running"""
        return self.state == ThreadState.RUNNING
