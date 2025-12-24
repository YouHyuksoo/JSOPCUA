# Data Model: Database Management REST API

**Feature**: 005-database-crud-api
**Date**: 2025-11-02

## Overview

This API uses Feature 1's existing SQLite schema. This document defines Pydantic models for request/response validation.

## Pydantic Models

### Line Models

```python
class LineBase(BaseModel):
    line_code: str = Field(max_length=50)
    line_name: str = Field(max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    enabled: bool = True

class LineCreate(LineBase):
    pass

class LineUpdate(BaseModel):
    line_name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    enabled: Optional[bool] = None

class LineResponse(LineBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

### Process Models

```python
class ProcessBase(BaseModel):
    line_id: int
    process_sequence: int
    process_code: str = Field(min_length=14, max_length=14)
    process_name: str = Field(max_length=200)
    equipment_type: Optional[str] = Field(None, max_length=10)
    enabled: bool = True
    
    @validator('process_code')
    def validate_code(cls, v):
        pattern = r'\^[A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid 14-char format')
        return v

class ProcessCreate(ProcessBase):
    pass

class ProcessUpdate(BaseModel):
    process_sequence: Optional[int] = None
    process_name: Optional[str] = None
    equipment_type: Optional[str] = None
    enabled: Optional[bool] = None

class ProcessResponse(ProcessBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

### PLC Connection Models

```python
class PLCConnectionBase(BaseModel):
    process_id: int
    plc_code: str = Field(max_length=50)
    ip_address: str
    port: int = 5000
    network_no: int = 0
    station_no: int = 0
    enabled: bool = True
    
    @validator('ip_address')
    def validate_ip(cls, v):
        try:
            ipaddress.IPv4Address(v)
        except ValueError:
            raise ValueError('Invalid IPv4 address')
        return v

class PLCConnectionCreate(PLCConnectionBase):
    pass

class PLCConnectionUpdate(BaseModel):
    ip_address: Optional[str] = None
    port: Optional[int] = None
    network_no: Optional[int] = None
    station_no: Optional[int] = None
    enabled: Optional[bool] = None

class PLCConnectionResponse(PLCConnectionBase):
    id: int
    created_at: datetime
    updated_at: datetime

class PLCTestResult(BaseModel):
    status: str  # 'success' or 'failed'
    response_time_ms: Optional[int] = None
    error: Optional[str] = None
```

### Tag Models

```python
class TagBase(BaseModel):
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
    pass

class TagUpdate(BaseModel):
    tag_name: Optional[str] = None
    tag_division: Optional[str] = None
    data_type: Optional[str] = None
    unit: Optional[str] = None
    scale: Optional[float] = None
    polling_group_id: Optional[int] = None
    enabled: Optional[bool] = None

class TagResponse(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

class TagImportResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[dict]  # [{row: int, error: str}]
```

### Polling Group Models

```python
class PollingGroupBase(BaseModel):
    group_name: str = Field(max_length=200)
    line_code: Optional[str] = Field(None, max_length=50)
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
        if v not in ['FIXED', 'HANDSHAKE']:
            raise ValueError('Mode must be FIXED or HANDSHAKE')
        return v
    
    @validator('trigger_bit_address')
    def validate_trigger(cls, v, values):
        if values.get('mode') == 'HANDSHAKE' and not v:
            raise ValueError('trigger_bit_address required for HANDSHAKE')
        return v

class PollingGroupCreate(PollingGroupBase):
    pass

class PollingGroupUpdate(BaseModel):
    group_name: Optional[str] = None
    mode: Optional[str] = None
    interval_ms: Optional[int] = None
    trigger_bit_address: Optional[str] = None
    enabled: Optional[bool] = None

class PollingGroupResponse(PollingGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

## Pagination Response

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    total_pages: int
    current_page: int
    page_size: int
```

## Error Response

```python
class ErrorResponse(BaseModel):
    error: str
    detail: str
    field: Optional[str] = None
```
