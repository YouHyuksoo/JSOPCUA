"""
Fixed Polling Thread

Implements FIXED mode polling - automatic polling at fixed intervals.
"""

import logging
import time
from .polling_thread import PollingThread
from .models import PollingGroup, PollingMode
from .data_queue import DataQueue

logger = logging.getLogger(__name__)


class FixedPollingThread(PollingThread):
    """
    FIXED mode polling thread

    Polls PLC tags automatically at fixed intervals (e.g., 1s, 5s, 10s).
    Uses high-precision timing with drift correction to maintain interval accuracy.

    Attributes:
        interval_s: Polling interval in seconds (converted from ms)
        _drift: Accumulated timing drift for correction
    """

    def __init__(self, group: PollingGroup, pool_manager, data_queue: DataQueue):
        """
        Initialize fixed polling thread

        Args:
            group: PollingGroup configuration (must be FIXED mode)
            pool_manager: PoolManager instance
            data_queue: DataQueue for storing results

        Raises:
            ValueError: If group mode is not FIXED or interval_ms is None
        """
        if group.mode != PollingMode.FIXED:
            raise ValueError(f"FixedPollingThread requires FIXED mode, got {group.mode.value}")

        if group.interval_ms is None or group.interval_ms < 100:
            raise ValueError(f"FIXED mode requires interval_ms >= 100, got {group.interval_ms}")

        super().__init__(group, pool_manager, data_queue)

        # Convert interval to seconds
        self.interval_s = group.interval_ms / 1000.0

        # Drift tracking for timing correction
        self._drift = 0.0

        logger.info(
            f"FixedPollingThread created: group={group.group_name}, "
            f"interval={group.interval_ms}ms ({self.interval_s}s)"
        )

    def run(self):
        """
        Main polling loop for FIXED mode

        Polls at fixed intervals using time.perf_counter() for high precision.
        Implements drift correction to maintain long-term interval accuracy.

        Loop continues until stop_event is set. Completes current cycle before stopping.
        """
        logger.info(f"Starting FIXED polling loop: group={self.group.group_name}, interval={self.interval_s}s")

        next_poll_time = time.perf_counter()

        while not self.stop_event.is_set():
            # Wait until next poll time
            current_time = time.perf_counter()
            sleep_time = next_poll_time - current_time

            if sleep_time > 0:
                # Sleep until next poll (check stop_event periodically)
                if self.stop_event.wait(timeout=sleep_time):
                    # Stop event was set during sleep
                    break
            else:
                # We're behind schedule - log warning if significant
                if sleep_time < -0.1:  # More than 100ms behind
                    logger.warning(
                        f"Polling cycle running behind: group={self.group.group_name}, "
                        f"behind={abs(sleep_time)*1000:.1f}ms"
                    )

            # Check stop event before polling
            if self.stop_event.is_set():
                break

            # Execute poll
            poll_start = time.perf_counter()
            success = self.execute_poll()
            poll_end = time.perf_counter()

            poll_time = poll_end - poll_start

            # Log slow polls
            if poll_time > self.interval_s:
                logger.warning(
                    f"Poll time ({poll_time*1000:.1f}ms) exceeds interval ({self.interval_s*1000:.0f}ms) "
                    f"for group {self.group.group_name}"
                )

            # Calculate next poll time with drift correction
            # This ensures long-term accuracy even if individual polls vary
            next_poll_time += self.interval_s

            # Track drift
            actual_interval = poll_end - (next_poll_time - self.interval_s)
            self._drift += (actual_interval - self.interval_s)

            # Log excessive drift
            if abs(self._drift) > self.interval_s:
                logger.debug(
                    f"Accumulated drift: group={self.group.group_name}, "
                    f"drift={self._drift*1000:.1f}ms"
                )
                # Reset drift to prevent unbounded growth
                self._drift = 0.0
                next_poll_time = time.perf_counter() + self.interval_s

        logger.info(f"FIXED polling loop stopped: group={self.group.group_name}")
