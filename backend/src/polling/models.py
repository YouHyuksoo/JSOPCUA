"""
Polling Engine Data Models

Data classes for polling group configuration, polling data, and status.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class PollingMode(Enum):
    """Polling mode enumeration"""
    FIXED = "FIXED"
    HANDSHAKE = "HANDSHAKE"


class ThreadState(Enum):
    """Polling thread state enumeration"""
    STOPPED = "stopped"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class PollingGroup:
    """
    Polling group configuration loaded from database

    Attributes:
        group_id: Unique polling group ID (from DB)
        group_name: Polling group name
        plc_code: PLC code to connect to
        mode: Polling mode (FIXED or HANDSHAKE)
        interval_ms: Polling interval in milliseconds (FIXED mode only)
        group_category: Oracle table category (OPERATION or ALARM)
        is_active: Whether the group is active
        tag_addresses: List of tag addresses to poll
    """
    group_id: int
    group_name: str
    plc_code: str
    mode: PollingMode
    interval_ms: Optional[int] = None
    group_category: str = "OPERATION"
    is_active: bool = True
    tag_addresses: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate polling group configuration"""
        if isinstance(self.mode, str):
            self.mode = PollingMode(self.mode)

        if self.mode == PollingMode.FIXED and (self.interval_ms is None or self.interval_ms < 100):
            raise ValueError(f"FIXED mode requires interval_ms >= 100ms, got {self.interval_ms}")

        if not self.tag_addresses:
            raise ValueError(f"Polling group {self.group_name} has no tag addresses")

        # Validate group_category
        if self.group_category not in ("OPERATION", "STATE", "ALARM"):
            raise ValueError(f"Invalid group_category: {self.group_category}. Must be OPERATION, STATE, or ALARM")


@dataclass
class PollingData:
    """
    Result of a single polling cycle

    Attributes:
        timestamp: When the poll was executed
        group_id: Polling group ID
        group_name: Polling group name
        plc_code: PLC code that was polled
        mode: Polling mode used
        group_category: Oracle table category (OPERATION or ALARM)
        tag_values: Dict of tag address → value
        tag_log_modes: Dict of tag address → log_mode (ALWAYS/ON_CHANGE/NEVER)
        tag_machine_codes: Dict of tag address → machine_code (설비코드)
        poll_time_ms: Time taken to complete poll (milliseconds)
        error_tags: Dict of tag address → error message (if any)
    """
    timestamp: datetime
    group_id: int
    group_name: str
    plc_code: str
    mode: PollingMode
    group_category: str = "OPERATION"
    tag_values: Dict[str, Any] = field(default_factory=dict)
    tag_log_modes: Dict[str, str] = field(default_factory=dict)
    tag_machine_codes: Dict[str, str] = field(default_factory=dict)
    poll_time_ms: float = 0.0
    error_tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "group_id": self.group_id,
            "group_name": self.group_name,
            "plc_code": self.plc_code,
            "mode": self.mode.value,
            "group_category": self.group_category,
            "tag_values": self.tag_values,
            "poll_time_ms": self.poll_time_ms,
            "error_tags": self.error_tags
        }


@dataclass
class PollingStatus:
    """
    Status information for a polling group

    Attributes:
        group_id: Polling group ID
        group_name: Polling group name
        mode: Polling mode
        state: Current thread state
        last_poll_time: Timestamp of last poll (None if never polled)
        total_polls: Total number of polls attempted
        success_count: Number of successful polls
        error_count: Number of failed polls
        avg_poll_time_ms: Average polling time in milliseconds
    """
    group_id: int
    group_name: str
    mode: PollingMode
    state: ThreadState
    last_poll_time: Optional[datetime] = None
    total_polls: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_poll_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "mode": self.mode.value,
            "state": self.state.value,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "total_polls": self.total_polls,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "avg_poll_time_ms": self.avg_poll_time_ms
        }
