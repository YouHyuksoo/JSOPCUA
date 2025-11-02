"""
Handshake Polling Thread

Implements HANDSHAKE mode polling - manual trigger via API.
"""

import logging
import time
import threading
from .polling_thread import PollingThread
from .models import PollingGroup, PollingMode
from .data_queue import DataQueue

logger = logging.getLogger(__name__)


class HandshakePollingThread(PollingThread):
    """
    HANDSHAKE mode polling thread

    Waits for manual trigger events to execute polling.
    Does not poll automatically - requires external trigger via API.

    Attributes:
        trigger_event: Event to signal manual poll trigger
        last_trigger_time: Timestamp of last trigger (for deduplication)
        dedup_window_s: Deduplication window in seconds (default: 1.0)
    """

    def __init__(self, group: PollingGroup, pool_manager, data_queue: DataQueue):
        """
        Initialize handshake polling thread

        Args:
            group: PollingGroup configuration (must be HANDSHAKE mode)
            pool_manager: PoolManager instance
            data_queue: DataQueue for storing results

        Raises:
            ValueError: If group mode is not HANDSHAKE
        """
        if group.mode != PollingMode.HANDSHAKE:
            raise ValueError(f"HandshakePollingThread requires HANDSHAKE mode, got {group.mode.value}")

        super().__init__(group, pool_manager, data_queue)

        # Trigger mechanism
        self.trigger_event = threading.Event()
        self.last_trigger_time = 0.0
        self.dedup_window_s = 1.0  # 1-second deduplication window

        logger.info(f"HandshakePollingThread created: group={group.group_name}")

    def run(self):
        """
        Main polling loop for HANDSHAKE mode

        Waits for trigger events and executes single poll on each trigger.
        Implements deduplication to ignore multiple triggers within 1-second window.

        Loop continues until stop_event is set.
        """
        logger.info(f"Starting HANDSHAKE polling loop: group={self.group.group_name}")

        while not self.stop_event.is_set():
            # Wait for trigger event (with periodic stop_event check)
            triggered = self.trigger_event.wait(timeout=1.0)

            if not triggered:
                # Timeout - check stop_event and continue waiting
                continue

            # Clear trigger for next time
            self.trigger_event.clear()

            # Check stop event before polling
            if self.stop_event.is_set():
                break

            # Check deduplication window
            current_time = time.time()
            if current_time - self.last_trigger_time < self.dedup_window_s:
                logger.debug(
                    f"Ignoring duplicate trigger within {self.dedup_window_s}s window "
                    f"for group {self.group.group_name}"
                )
                continue

            # Update last trigger time
            self.last_trigger_time = current_time

            # Execute single poll
            logger.info(f"HANDSHAKE trigger received, executing poll: group={self.group.group_name}")
            success = self.execute_poll()

            if success:
                logger.info(f"HANDSHAKE poll completed successfully: group={self.group.group_name}")
            else:
                logger.error(f"HANDSHAKE poll failed: group={self.group.group_name}")

        logger.info(f"HANDSHAKE polling loop stopped: group={self.group.group_name}")

    def trigger(self) -> bool:
        """
        Manually trigger a polling cycle

        Sets the trigger event to execute a single poll.

        Returns:
            True if trigger was set, False if thread is not running
        """
        if not self.is_running():
            logger.warning(f"Cannot trigger non-running thread: group={self.group.group_name}")
            return False

        # Check deduplication
        current_time = time.time()
        if current_time - self.last_trigger_time < self.dedup_window_s:
            logger.debug(
                f"Trigger ignored (deduplication): group={self.group.group_name}, "
                f"last_trigger={current_time - self.last_trigger_time:.2f}s ago"
            )
            return False

        logger.info(f"Trigger set for HANDSHAKE poll: group={self.group.group_name}")
        self.trigger_event.set()
        return True
