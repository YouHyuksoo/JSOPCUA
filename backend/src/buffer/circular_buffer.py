"""
Circular Buffer

Thread-safe circular buffer using collections.deque with automatic FIFO overflow.
"""

import threading
import logging
from collections import deque
from typing import Optional
from datetime import datetime

from .models import BufferedTagValue
from .exceptions import BufferEmptyError

logger = logging.getLogger(__name__)


class CircularBuffer:
    """
    Thread-safe circular buffer with automatic FIFO overflow
    
    Uses collections.deque with maxlen for automatic oldest-item eviction.
    Tracks overflow events for monitoring and alerting.
    
    Attributes:
        maxsize: Maximum buffer capacity
        overflow_count: Number of items evicted due to buffer full
        overflow_alert_threshold: Utilization % to trigger warning (default: 80%)
    """
    
    def __init__(self, maxsize: int = 100000, overflow_alert_threshold: float = 80.0):
        """
        Initialize circular buffer
        
        Args:
            maxsize: Maximum number of items (default: 100,000)
            overflow_alert_threshold: Utilization % to trigger warning (default: 80%)
        """
        self.maxsize = maxsize
        self.overflow_alert_threshold = overflow_alert_threshold
        self._buffer = deque(maxlen=maxsize)
        self._lock = threading.Lock()
        self.overflow_count = 0
        self._total_added = 0
        self._last_alert_count = 0  # Track last alert to avoid spam
    
    def put(self, item: BufferedTagValue) -> bool:
        """
        Add item to buffer (thread-safe)
        
        If buffer is full, oldest item is automatically evicted (FIFO).
        Tracks overflow events and logs warnings.
        
        Args:
            item: BufferedTagValue to add
            
        Returns:
            True if added without overflow, False if overflow occurred
        """
        with self._lock:
            current_size = len(self._buffer)
            utilization_pct = (current_size / self.maxsize) * 100.0
            
            # Alert if approaching capacity (before overflow)
            if utilization_pct >= self.overflow_alert_threshold and self.overflow_count == self._last_alert_count:
                logger.warning(
                    f"Buffer utilization high: {utilization_pct:.1f}% "
                    f"({current_size}/{self.maxsize} items). "
                    f"Approaching capacity!"
                )
                self._last_alert_count = self.overflow_count
            
            self._buffer.append(item)
            self._total_added += 1
            
            # Check if overflow occurred (deque evicted oldest item)
            if current_size == self.maxsize:
                self.overflow_count += 1
                
                # Log overflow event with statistics
                overflow_rate = (self.overflow_count / self._total_added) * 100.0
                logger.warning(
                    f"Buffer overflow #{self.overflow_count}: Discarded oldest item (FIFO). "
                    f"Total added: {self._total_added}, "
                    f"Overflow rate: {overflow_rate:.3f}%"
                )
                
                self._last_alert_count = self.overflow_count
                return False  # Overflow occurred
            
            return True  # No overflow
    
    def get(self, count: int = 1) -> list[BufferedTagValue]:
        """
        Get and remove items from buffer (thread-safe, FIFO order)
        
        Args:
            count: Number of items to retrieve (default: 1)
            
        Returns:
            List of BufferedTagValue items (may be fewer than requested)
            
        Raises:
            BufferEmptyError: If buffer is empty
        """
        with self._lock:
            if not self._buffer:
                raise BufferEmptyError("Cannot get from empty buffer")
            
            items = []
            for _ in range(min(count, len(self._buffer))):
                items.append(self._buffer.popleft())
            
            return items
    
    def peek(self, count: int = 1) -> list[BufferedTagValue]:
        """
        View items without removing (thread-safe)
        
        Args:
            count: Number of items to peek (default: 1)
            
        Returns:
            List of BufferedTagValue items (read-only)
        """
        with self._lock:
            return list(self._buffer)[:count]
    
    def size(self) -> int:
        """Get current buffer size (thread-safe)"""
        with self._lock:
            return len(self._buffer)
    
    def is_empty(self) -> bool:
        """Check if buffer is empty (thread-safe)"""
        with self._lock:
            return len(self._buffer) == 0
    
    def is_full(self) -> bool:
        """Check if buffer is at capacity (thread-safe)"""
        with self._lock:
            return len(self._buffer) >= self.maxsize
    
    def utilization(self) -> float:
        """
        Get buffer utilization percentage (thread-safe)
        
        Returns:
            Utilization percentage (0.0 - 100.0)
        """
        with self._lock:
            return (len(self._buffer) / self.maxsize) * 100.0
    
    def get_overflow_rate(self) -> float:
        """
        Get overflow rate as percentage of total items added
        
        Returns:
            Overflow rate percentage (0.0 - 100.0)
        """
        with self._lock:
            if self._total_added == 0:
                return 0.0
            return (self.overflow_count / self._total_added) * 100.0
    
    def clear(self):
        """Clear all items from buffer (thread-safe)"""
        with self._lock:
            self._buffer.clear()
    
    def stats(self) -> dict:
        """
        Get buffer statistics (thread-safe)
        
        Returns:
            Dictionary with current_size, max_size, utilization_pct, overflow_count, total_added, overflow_rate_pct
        """
        with self._lock:
            utilization_pct = (len(self._buffer) / self.maxsize) * 100.0
            overflow_rate_pct = (self.overflow_count / self._total_added * 100.0) if self._total_added > 0 else 0.0
            
            return {
                'current_size': len(self._buffer),
                'max_size': self.maxsize,
                'utilization_pct': round(utilization_pct, 1),
                'overflow_count': self.overflow_count,
                'total_added': self._total_added,
                'overflow_rate_pct': round(overflow_rate_pct, 3)
            }
