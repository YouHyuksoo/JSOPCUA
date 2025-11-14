"""
Pydantic Models for Database Management API

Feature 5: Database Management REST API
Provides request/response models for CRUD operations on:
- Machines, Processes, PLC Connections, Tags, Polling Groups
"""

from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field, field_validator, ConfigDict
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
    machine_code: Optional[str] = Field(None, max_length=50)
    process_sequence: int
    process_code: str = Field(min_length=14, max_length=14)
    process_name: str = Field(max_length=200)
    equipment_type: Optional[str] = Field(None, max_length=100)
    enabled: bool = True

    @field_validator('process_code')
    @classmethod
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
    plc_code: str = Field(max_length=50)
    plc_name: str = Field(max_length=100)
    plc_spec: Optional[str] = Field(None, max_length=200)
    plc_type: Optional[str] = Field(None, max_length=20)
    ip_address: str
    port: int = 5010
    protocol: str = Field(default='MC_3E_ASCII', max_length=20)
    network_no: int = 0
    station_no: int = 0
    connection_timeout: int = 5
    is_active: bool = True
    # MELSEC 설정
    driver_version: Optional[str] = Field(None, max_length=10)
    message_format: Optional[str] = Field(None, max_length=20)
    series: Optional[str] = Field(None, max_length=50)
    # SSL/TLS 설정
    ssl_root_cert: Optional[str] = None
    ssl_version: Optional[str] = Field(None, max_length=20)
    ssl_password: Optional[str] = Field(None, max_length=200)
    ssl_private_key: Optional[str] = None
    ssl_certificate: Optional[str] = None
    # 네트워크 설정
    local_address: Optional[str] = Field(None, max_length=50)
    network_type: Optional[str] = Field(None, max_length=10)
    # 소켓 설정
    keep_alive: Optional[bool] = False
    linger_time: Optional[int] = -1
    # 일반 설정
    description: Optional[str] = None
    scan_time: Optional[int] = 1000
    # 장치 설정
    charset: Optional[str] = Field(None, max_length=20)
    text_endian: Optional[str] = Field(None, max_length=20)
    # 장치 블락 설정
    unit_size: Optional[str] = Field(None, max_length=20)
    block_size: Optional[int] = 64

    @field_validator('ip_address')
    @classmethod
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
    plc_name: Optional[str] = None
    plc_spec: Optional[str] = None
    plc_type: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    network_no: Optional[int] = None
    station_no: Optional[int] = None
    connection_timeout: Optional[int] = None
    is_active: Optional[bool] = None


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
    test_value_d100: Optional[int] = None  # D100 address test read value
    test_value_w100: Optional[int] = None  # W100+W101 combined 32-bit value
    test_value_m100: Optional[int] = None  # M100 address test read value (bit)
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
    tag_category: Optional[str] = Field(None, max_length=50)
    data_type: str = Field(default='WORD', max_length=20)
    unit: Optional[str] = Field(None, max_length=20)
    scale: float = 1.0
    machine_code: Optional[str] = Field(None, max_length=200)
    polling_group_id: Optional[int] = None
    log_mode: str = Field(default='ALWAYS', description="Log mode: ALWAYS, ON_CHANGE, NEVER")
    enabled: bool = True

    @field_validator('log_mode')
    @classmethod
    def validate_log_mode(cls, v):
        """Validate log mode"""
        if v not in ['ALWAYS', 'ON_CHANGE', 'NEVER']:
            raise ValueError('Log mode must be ALWAYS, ON_CHANGE, or NEVER')
        return v


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
    log_mode: Optional[str] = Field(None, description="Log mode: ALWAYS, ON_CHANGE, NEVER")
    enabled: Optional[bool] = None

    @field_validator('log_mode')
    @classmethod
    def validate_log_mode(cls, v):
        """Validate log mode"""
        if v is not None and v not in ['ALWAYS', 'ON_CHANGE', 'NEVER']:
            raise ValueError('Log mode must be ALWAYS, ON_CHANGE, or NEVER')
        return v


class TagResponse(TagBase):
    """Tag response"""
    id: int
    plc_code: Optional[str] = None  # PLC code from plc_connections table
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
    group_name: str = Field(max_length=200, alias='name')  # Accept 'name' from frontend
    line_code: Optional[str] = Field(None, max_length=50)  # Line code (optional, legacy field)
    machine_code: Optional[str] = Field(None, max_length=50)
    process_code: Optional[str] = Field(None, max_length=50)
    plc_id: int = Field(default=1)  # Default to PLC01
    mode: str = Field(default='FIXED')
    interval_ms: int = Field(default=1000, alias='polling_interval')  # Accept 'polling_interval' from frontend
    group_category: str = Field(default='OPERATION', description="Oracle table category: OPERATION or ALARM")
    trigger_bit_address: Optional[str] = Field(None, max_length=20)
    trigger_bit_offset: int = 0
    auto_reset_trigger: bool = True
    priority: str = Field(default='NORMAL')
    enabled: bool = Field(default=True, alias='is_active')  # Accept 'is_active' from frontend

    model_config = ConfigDict(populate_by_name=True)  # Allow both alias and field name

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        """Validate polling mode"""
        if v not in ['FIXED', 'HANDSHAKE']:
            raise ValueError('Mode must be FIXED or HANDSHAKE')
        return v

    @field_validator('group_category')
    @classmethod
    def validate_group_category(cls, v):
        """Validate group category"""
        if v not in ['OPERATION', 'STATE', 'ALARM']:
            raise ValueError('Group category must be OPERATION, STATE, or ALARM')
        return v


class PollingGroupCreate(PollingGroupBase):
    """Polling Group creation request"""
    tag_ids: List[int] = Field(default_factory=list, description="List of tag IDs to assign to this polling group")


class PollingGroupUpdate(BaseModel):
    """Polling Group update request"""
    group_name: Optional[str] = Field(None, alias='name')  # Accept 'name' from frontend
    mode: Optional[str] = None
    interval_ms: Optional[int] = Field(None, alias='polling_interval')  # Accept 'polling_interval' from frontend
    group_category: Optional[str] = Field(None, description="Oracle table category: OPERATION, STATE, or ALARM")
    trigger_bit_address: Optional[str] = None
    enabled: Optional[bool] = Field(None, alias='is_active')  # Accept 'is_active' from frontend
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs to assign to this polling group")

    model_config = ConfigDict(populate_by_name=True)  # Allow both alias and field name

    @field_validator('group_category')
    @classmethod
    def validate_group_category(cls, v):
        """Validate group category"""
        if v is not None and v not in ['OPERATION', 'STATE', 'ALARM']:
            raise ValueError('Group category must be OPERATION, STATE, or ALARM')
        return v


class PollingGroupResponse(PollingGroupBase):
    """Polling Group response"""
    id: int
    created_at: datetime
    updated_at: datetime
    tag_count: int = 0
    status: str = "stopped"  # "stopped" | "running" | "error"

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
