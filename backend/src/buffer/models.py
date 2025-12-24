"""
Buffer Data Models

Data classes for buffered tag values, write batches, and metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class BufferedTagValue:
    """
    Individual tag value extracted from PollingData for buffering
    
    Attributes:
        timestamp: Data collection time from polling engine
        plc_code: PLC identifier (e.g., 'KRCWO12ELOA101')
        tag_address: Tag address (e.g., 'D100')
        tag_value: Numeric value read from PLC
        quality: Data quality ('GOOD', 'BAD', 'UNCERTAIN')
    """
    timestamp: datetime
    plc_code: str
    tag_address: str
    tag_value: float
    quality: str = 'GOOD'
    
    def to_dict(self):
        """Convert to dictionary for CSV export"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'plc_code': self.plc_code,
            'tag_address': self.tag_address,
            'tag_value': self.tag_value,
            'quality': self.quality
        }


@dataclass
class WriteBatch:
    """
    Collection of BufferedTagValue items for bulk Oracle insert
    
    Attributes:
        items: List of BufferedTagValue objects (100-1,000 items)
        created_at: Batch creation timestamp
    """
    items: List[BufferedTagValue] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __len__(self):
        return len(self.items)
    
    def add(self, item: BufferedTagValue):
        """Add item to batch"""
        self.items.append(item)
    
    def clear(self):
        """Clear all items from batch"""
        self.items.clear()
    
    def is_empty(self):
        """Check if batch is empty"""
        return len(self.items) == 0


@dataclass
class WriterMetrics:
    """
    Performance statistics for Oracle writer
    
    Attributes:
        successful_writes: Total successful batch writes
        failed_writes: Total failed batch writes
        total_items_written: Total individual tag values written
        avg_batch_size: Rolling average batch size
        avg_write_latency_ms: Rolling average write latency in milliseconds
        buffer_utilization_pct: Current buffer utilization percentage
        overflow_count: Number of buffer overflows (FIFO evictions)
        backup_file_count: Number of CSV backup files created
        last_write_time: Timestamp of last successful write
    """
    successful_writes: int = 0
    failed_writes: int = 0
    total_items_written: int = 0
    avg_batch_size: float = 0.0
    avg_write_latency_ms: float = 0.0
    buffer_utilization_pct: float = 0.0
    overflow_count: int = 0
    backup_file_count: int = 0
    last_write_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate write success rate percentage"""
        total = self.successful_writes + self.failed_writes
        if total == 0:
            return 100.0
        return (self.successful_writes / total) * 100.0
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'successful_writes': self.successful_writes,
            'failed_writes': self.failed_writes,
            'total_items_written': self.total_items_written,
            'success_rate': round(self.success_rate, 2),
            'avg_batch_size': round(self.avg_batch_size, 1),
            'avg_write_latency_ms': round(self.avg_write_latency_ms, 1),
            'buffer_utilization_pct': round(self.buffer_utilization_pct, 1),
            'overflow_count': self.overflow_count,
            'backup_file_count': self.backup_file_count,
            'last_write_time': self.last_write_time.isoformat() if self.last_write_time else None
        }
