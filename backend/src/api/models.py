"""
Pydantic Models for Database Management API

Feature 5: Database Management REST API
Provides request/response models for CRUD operations on:
- Machines, Processes, PLC Connections, Tags, Polling Groups
"""

from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field, validator, ConfigDict
import ipaddress
import re


# ==============================================================================
# Base Response Models
# ==============================================================================

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total_count: int
    total_pages: int
    current_page: int
    page_size: int


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: str
    field: Optional[str] = None


# ==============================================================================
# Machine Models
# ==============================================================================

class MachineBase(BaseModel):
    """Base Machine model"""
    machine_code: str = Field(max_length=50)
    machine_name: str = Field(max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    enabled: bool = True


class MachineCreate(MachineBase):
    """Machine creation request"""
    pass


class MachineUpdate(BaseModel):
    """Machine update request"""
    machine_name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    enabled: Optional[bool] = None


class MachineResponse(MachineBase):
    """Machine response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Process Models
# ==============================================================================

class ProcessBase(BaseModel):
    """Base Process model"""
    machine_id: int
    process_sequence: int
    process_code: str = Field(min_length=14, max_length=14)
    process_name: str = Field(max_length=200)
    equipment_type: Optional[str] = Field(None, max_length=10)
    enabled: bool = True

    @validator('process_code')
    def validate_code(cls, v):
        """Validate 14-character process code format"""
        pattern = r'^[A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}$'
        if not re.match(pattern, v):
            raise ValueError(
                'process_code must be exactly 14 characters matching pattern: '
                '[A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3}'
            )
        return v


class ProcessCreate(ProcessBase):
    """Process creation request"""
    pass


class ProcessUpdate(BaseModel):
    """Process update request"""
    process_sequence: Optional[int] = None
    process_name: Optional[str] = None
    equipment_type: Optional[str] = None
    enabled: Optional[bool] = None


class ProcessResponse(ProcessBase):
    """Process response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# PLC Connection Models
# ==============================================================================

class PLCConnectionBase(BaseModel):
    """Base PLC Connection model"""
    process_id: int
    plc_code: str = Field(max_length=50)
    ip_address: str
    port: int = 5000
    network_no: int = 0
    station_no: int = 0
    enabled: bool = True

    @validator('ip_address')
    def validate_ip(cls, v):
        """Validate IPv4 address format"""
        try:
            ipaddress.IPv4Address(v)
        except ValueError:
            raise ValueError('Invalid IPv4 address format')
        return v


class PLCConnectionCreate(PLCConnectionBase):
    """PLC Connection creation request"""
    pass


class PLCConnectionUpdate(BaseModel):
    """PLC Connection update request"""
    ip_address: Optional[str] = None
    port: Optional[int] = None
    network_no: Optional[int] = None
    station_no: Optional[int] = None
    enabled: Optional[bool] = None


class PLCConnectionResponse(PLCConnectionBase):
    """PLC Connection response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PLCTestResult(BaseModel):
    """PLC connection test result"""
    status: str  # 'success' or 'failed'
    response_time_ms: Optional[int] = None
    error: Optional[str] = None


# ==============================================================================
# Tag Models
# ==============================================================================

class TagBase(BaseModel):
    """Base Tag model"""
    plc_id: int
    process_id: int
    tag_address: str = Field(max_length=20)
    tag_name: str = Field(max_length=200)
    tag_division: Optional[str] = Field(None, max_length=50)
    data_type: str = Field(default='WORD', max_length=20)
    unit: Optional[str] = Field(None, max_length=20)
    scale: float = 1.0
    machine_code: Optional[str] = Field(None, max_length=200)
    polling_group_id: Optional[int] = None
    enabled: bool = True


class TagCreate(TagBase):
    """Tag creation request"""
    pass


class TagUpdate(BaseModel):
    """Tag update request"""
    tag_name: Optional[str] = None
    tag_division: Optional[str] = None
    data_type: Optional[str] = None
    unit: Optional[str] = None
    scale: Optional[float] = None
    polling_group_id: Optional[int] = None
    enabled: Optional[bool] = None


class TagResponse(TagBase):
    """Tag response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagImportResult(BaseModel):
    """Tag CSV import result"""
    success_count: int
    failure_count: int
    errors: List[dict]  # [{"row": int, "error": str}]


# ==============================================================================
# Polling Group Models
# ==============================================================================

class PollingGroupBase(BaseModel):
    """Base Polling Group model"""
    group_name: str = Field(max_length=200)
    machine_code: Optional[str] = Field(None, max_length=50)
    process_code: Optional[str] = Field(None, max_length=50)
    plc_id: int
    mode: str = Field(default='FIXED')
    interval_ms: int = 1000
    trigger_bit_address: Optional[str] = Field(None, max_length=20)
    trigger_bit_offset: int = 0
    auto_reset_trigger: bool = True
    priority: str = Field(default='NORMAL')
    enabled: bool = True

    @validator('mode')
    def validate_mode(cls, v):
        """Validate polling mode"""
        if v not in ['FIXED', 'HANDSHAKE']:
            raise ValueError('Mode must be FIXED or HANDSHAKE')
        return v

    @validator('trigger_bit_address')
    def validate_trigger(cls, v, values):
        """Validate trigger_bit_address required for HANDSHAKE mode"""
        if values.get('mode') == 'HANDSHAKE' and not v:
            raise ValueError('trigger_bit_address is required for HANDSHAKE mode')
        return v


class PollingGroupCreate(PollingGroupBase):
    """Polling Group creation request"""
    pass


class PollingGroupUpdate(BaseModel):
    """Polling Group update request"""
    group_name: Optional[str] = None
    mode: Optional[str] = None
    interval_ms: Optional[int] = None
    trigger_bit_address: Optional[str] = None
    enabled: Optional[bool] = None


class PollingGroupResponse(PollingGroupBase):
    """Polling Group response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==============================================================================
# Alarm Models (Feature 7: Monitor Web UI)
# ==============================================================================

class Alarm(BaseModel):
    """Alarm model from Oracle DB"""
    alarm_id: int
    equipment_code: str
    equipment_name: str
    alarm_type: str  # '알람' or '일반'
    alarm_message: str
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlarmStatistics(BaseModel):
    """Alarm statistics model aggregated by equipment"""
    equipment_code: str
    equipment_name: str
    alarm_count: int
    general_count: int

    model_config = ConfigDict(from_attributes=True)


class AlarmStatisticsResponse(BaseModel):
    """Alarm statistics response wrapper"""
    equipment: List[AlarmStatistics]
    last_updated: datetime


class RecentAlarmsResponse(BaseModel):
    """Recent alarms response wrapper"""
    alarms: List[Alarm]
