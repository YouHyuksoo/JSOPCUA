"""
Data Distributor Thread

Consumes polling data from DataQueue and distributes to multiple consumers:
1. Oracle Writer (for database persistence)
2. Monitor Broadcaster (for real-time WebSocket clients)
3. SQLite updater (for last_value tracking)
"""

import threading
import logging
from typing import Optional
from queue import Empty, Queue

from .data_queue import DataQueue
from .models import PollingData

logger = logging.getLogger(__name__)


class DataDistributor:
    """
    Distributes polling data to multiple output queues

    Consumes from single input DataQueue and distributes to:
    - Oracle writer queue
    - Monitor broadcast queue
    - Any other custom queues

    This allows different consumers to process data at their own pace
    without blocking each other.

    Attributes:
        input_queue: DataQueue to consume from
        output_queues: List of output queues
        thread: Threading.Thread instance
        stop_event: Event to signal thread shutdown
    """

    def __init__(self, input_queue: DataQueue):
        """
        Initialize data distributor

        Args:
            input_queue: DataQueue to consume polling results from
        """
        self.input_queue = input_queue
        self.output_queues = []
        self._output_locks = []

        # Thread management
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._running = False

        # Statistics
        self.records_distributed = 0
        self.records_dropped = 0

        logger.info("DataDistributor initialized")

    def add_output_queue(self, queue: Queue, name: str = "unnamed"):
        """
        Add an output queue for distribution

        Args:
            queue: Queue to add
            name: Name for logging purposes
        """
        self.output_queues.append({
            "queue": queue,
            "name": name,
            "lock": threading.Lock()
        })
        logger.info(f"Added output queue: {name}")

    def start(self):
        """Start the distributor thread"""
        if self._running:
            logger.warning("Data distributor already running")
            return

        self.stop_event.clear()
        self._running = True
        self.thread = threading.Thread(
            target=self._run,
            name="DataDistributor",
            daemon=False
        )
        self.thread.start()
        logger.info("Data distributor started")

    def stop(self, timeout: float = 5.0):
        """
        Stop the distributor thread gracefully

        Args:
            timeout: Maximum time to wait for thread termination (seconds)
        """
        if not self._running:
            logger.warning("Data distributor not running")
            return

        logger.info("Stopping data distributor...")
        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
            if self.thread.is_alive():
                logger.error(f"Data distributor did not stop within {timeout}s")
            else:
                self._running = False
                logger.info("Data distributor stopped")
        else:
            self._running = False

    def _run(self):
        """Main distributor loop"""
        logger.info("Data distributor running")

        try:
            while not self.stop_event.is_set():
                try:
                    # Get data from input queue with timeout
                    polling_data = self.input_queue.get(timeout=1.0)

                    # Distribute to all output queues
                    self._distribute(polling_data)

                    # Update statistics
                    self.records_distributed += 1

                except Empty:
                    # Queue timeout - no data to distribute
                    continue

        except Exception as e:
            logger.error(f"Data distributor crashed: {e}", exc_info=True)

        finally:
            self._running = False
            logger.info("Data distributor exited")

    def _distribute(self, polling_data: PollingData):
        """
        Distribute polling data to all output queues

        Args:
            polling_data: PollingData object to distribute
        """
        for output in self.output_queues:
            queue = output["queue"]
            name = output["name"]

            try:
                # Try to put without blocking
                # If queue is full, log warning and drop
                if queue.full():
                    logger.warning(f"Output queue '{name}' is full, dropping data")
                    self.records_dropped += 1
                else:
                    queue.put_nowait(polling_data)

            except Exception as e:
                logger.error(f"Failed to put data to queue '{name}': {e}")
                self.records_dropped += 1

    def get_stats(self) -> dict:
        """
        Get distributor statistics

        Returns:
            Dictionary with statistics
        """
        output_stats = []
        for output in self.output_queues:
            queue = output["queue"]
            output_stats.append({
                "name": output["name"],
                "size": queue.qsize(),
                "full": queue.full()
            })

        return {
            "running": self._running,
            "records_distributed": self.records_distributed,
            "records_dropped": self.records_dropped,
            "output_queues": output_stats,
            "input_queue_size": self.input_queue.size()
        }

    def is_running(self) -> bool:
        """Check if distributor is running"""
        return self._running
