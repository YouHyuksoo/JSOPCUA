"""
PLC Communication Data Models

이 모듈은 PLC 통신에 사용되는 데이터 모델을 정의합니다.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class PLCConnectionInfo:
    """PLC 연결 정보"""
    plc_id: int
    plc_code: str
    plc_name: str
    ip_address: str
    port: int
    protocol: str
    connection_timeout: int = 5
    is_active: bool = True

    def __str__(self) -> str:
        return f"{self.plc_code} ({self.ip_address}:{self.port})"


@dataclass
class TagInfo:
    """태그 정보"""
    tag_id: int
    plc_id: int
    tag_address: str
    tag_name: str
    tag_type: str
    unit: Optional[str] = None
    scale: float = 1.0
    machine_code: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.tag_name} ({self.tag_address})"


@dataclass
class ReadRequest:
    """태그 읽기 요청"""
    request_id: str
    plc_id: int
    tag_addresses: list[str]
    timeout: int = 5
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ReadResponse:
    """태그 읽기 응답"""
    request_id: str
    success: bool
    values: Dict[str, Any]
    errors: Dict[str, str]
    response_time_ms: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
