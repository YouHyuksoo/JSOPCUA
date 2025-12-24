"""
Polling Failure Logger

일자별 폴더에 폴링 실패 로그를 저장하는 모듈
명령 실행 및 회신 과정의 상세 정보를 기록
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json


class PollingFailureLogger:
    """
    폴링 실패 로그 관리 클래스

    일자별 폴더 구조:
    logs/
    └─ polling_failures/
       ├─ 20250104/
       │  ├─ PLC01_failure_093015.log
       │  ├─ PLC01_failure_093045.log
       │  └─ PLC02_failure_100120.log
       └─ 20250105/
          └─ PLC01_failure_080512.log
    """

    def __init__(self, base_log_dir: str = "logs/polling_failures"):
        """
        Initialize polling failure logger

        Args:
            base_log_dir: 기본 로그 디렉토리 경로 (프로젝트 루트 기준)
        """
        self.base_log_dir = Path(base_log_dir)
        self.logger = logging.getLogger(__name__)

    def _get_daily_folder(self) -> Path:
        """
        현재 날짜의 폴더 경로 반환 (YYYYMMDD 형식)
        폴더가 없으면 자동 생성

        Returns:
            Path: 일자별 폴더 경로
        """
        today = datetime.now().strftime("%Y%m%d")
        daily_folder = self.base_log_dir / today
        daily_folder.mkdir(parents=True, exist_ok=True)
        return daily_folder

    def log_failure(
        self,
        plc_code: str,
        group_name: str,
        error_type: str,
        error_message: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        tag_addresses: Optional[list] = None,
        poll_duration_ms: Optional[float] = None,
        retry_count: int = 0
    ):
        """
        폴링 실패 로그를 일자별 폴더에 저장

        Args:
            plc_code: PLC 코드 (예: "PLC01")
            group_name: 폴링 그룹명
            error_type: 에러 타입 (CONNECTION_FAILED, TIMEOUT, READ_ERROR 등)
            error_message: 에러 메시지
            request_data: PLC에 전송한 요청 데이터 (옵션)
            response_data: PLC에서 받은 응답 데이터 (옵션)
            tag_addresses: 읽으려던 태그 주소 목록 (옵션)
            poll_duration_ms: 폴링 소요 시간 (ms)
            retry_count: 재시도 횟수
        """
        try:
            # 일자별 폴더 생성
            daily_folder = self._get_daily_folder()

            # 로그 파일명: {PLC코드}_failure_{시각}.log
            timestamp = datetime.now().strftime("%H%M%S_%f")[:9]  # HHMMSS_fff
            log_filename = f"{plc_code}_failure_{timestamp}.log"
            log_filepath = daily_folder / log_filename

            # 로그 내용 구성
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "plc_code": plc_code,
                "group_name": group_name,
                "error_type": error_type,
                "error_message": error_message,
                "tag_addresses": tag_addresses or [],
                "tag_count": len(tag_addresses) if tag_addresses else 0,
                "poll_duration_ms": poll_duration_ms,
                "retry_count": retry_count,
                "request": request_data,
                "response": response_data
            }

            # JSON 형식으로 저장 (가독성 좋게 indent 적용)
            with open(log_filepath, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)

            self.logger.warning(
                f"Polling failure logged: {log_filepath.name} | "
                f"PLC={plc_code}, Group={group_name}, Error={error_type}"
            )

        except Exception as e:
            self.logger.error(f"Failed to write polling failure log: {e}")

    def log_connection_failure(
        self,
        plc_code: str,
        group_name: str,
        ip_address: str,
        port: int,
        error_message: str,
        connection_timeout: int
    ):
        """
        PLC 연결 실패 로그 (간편 메서드)

        Args:
            plc_code: PLC 코드
            group_name: 폴링 그룹명
            ip_address: PLC IP 주소
            port: PLC 포트
            error_message: 에러 메시지
            connection_timeout: 연결 타임아웃 (초)
        """
        self.log_failure(
            plc_code=plc_code,
            group_name=group_name,
            error_type="CONNECTION_FAILED",
            error_message=error_message,
            request_data={
                "ip_address": ip_address,
                "port": port,
                "timeout": connection_timeout
            }
        )

    def log_read_failure(
        self,
        plc_code: str,
        group_name: str,
        tag_addresses: list,
        error_message: str,
        poll_duration_ms: float,
        response_code: Optional[str] = None
    ):
        """
        태그 읽기 실패 로그 (간편 메서드)

        Args:
            plc_code: PLC 코드
            group_name: 폴링 그룹명
            tag_addresses: 읽으려던 태그 주소 목록
            error_message: 에러 메시지
            poll_duration_ms: 폴링 소요 시간 (ms)
            response_code: PLC 응답 코드 (있는 경우)
        """
        self.log_failure(
            plc_code=plc_code,
            group_name=group_name,
            error_type="READ_ERROR",
            error_message=error_message,
            tag_addresses=tag_addresses,
            poll_duration_ms=poll_duration_ms,
            response_data={
                "response_code": response_code
            } if response_code else None
        )

    def log_timeout_failure(
        self,
        plc_code: str,
        group_name: str,
        tag_addresses: list,
        timeout_ms: float
    ):
        """
        타임아웃 실패 로그 (간편 메서드)

        Args:
            plc_code: PLC 코드
            group_name: 폴링 그룹명
            tag_addresses: 읽으려던 태그 주소 목록
            timeout_ms: 타임아웃 시간 (ms)
        """
        self.log_failure(
            plc_code=plc_code,
            group_name=group_name,
            error_type="TIMEOUT",
            error_message=f"Polling timeout after {timeout_ms}ms",
            tag_addresses=tag_addresses,
            poll_duration_ms=timeout_ms
        )

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        오래된 로그 폴더 정리 (옵션)

        Args:
            days_to_keep: 보관할 일수 (기본 30일)
        """
        try:
            if not self.base_log_dir.exists():
                return

            cutoff_date = datetime.now().timestamp() - (days_to_keep * 86400)
            deleted_count = 0

            for folder in self.base_log_dir.iterdir():
                if folder.is_dir():
                    folder_time = folder.stat().st_mtime
                    if folder_time < cutoff_date:
                        # 폴더 내 모든 파일 삭제
                        for log_file in folder.iterdir():
                            log_file.unlink()
                        # 빈 폴더 삭제
                        folder.rmdir()
                        deleted_count += 1

            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old log folders (older than {days_to_keep} days)")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")


# 싱글톤 인스턴스 생성
_failure_logger_instance = None


def get_failure_logger(base_log_dir: str = "logs/polling_failures") -> PollingFailureLogger:
    """
    싱글톤 PollingFailureLogger 인스턴스 반환

    Args:
        base_log_dir: 기본 로그 디렉토리 (최초 호출 시만 적용)

    Returns:
        PollingFailureLogger: 싱글톤 인스턴스
    """
    global _failure_logger_instance

    if _failure_logger_instance is None:
        _failure_logger_instance = PollingFailureLogger(base_log_dir)

    return _failure_logger_instance
