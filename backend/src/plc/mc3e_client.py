"""
MC 3E ASCII Protocol Client

Mitsubishi Q Series PLC와 MC 3E ASCII 프로토콜로 통신하는 클라이언트입니다.
"""

import time
from typing import Optional, Dict, Any, List
from pymcprotocol import Type3E
from .exceptions import (
    PLCConnectionError,
    PLCTimeoutError,
    PLCProtocolError,
    PLCReadError
)
from .utils import group_continuous_addresses, format_device_address
from . import logger


class MC3EClient:
    """
    MC 3E ASCII 프로토콜 클라이언트

    Mitsubishi Q Series PLC와 TCP/IP 소켓 연결을 통해 통신합니다.
    """

    def __init__(self, ip_address: str, port: int, plc_code: str = None, timeout: int = 5):
        """
        MC3EClient 초기화

        Args:
            ip_address: PLC IP 주소
            port: PLC 포트 번호
            plc_code: PLC 식별 코드
            timeout: 연결 타임아웃 (초)
        """
        self.ip_address = ip_address
        self.port = port
        self.plc_code = plc_code or f"{ip_address}:{port}"
        self.timeout = timeout
        self._plc: Optional[Type3E] = None
        self._is_connected = False

        logger.info(f"MC3EClient initialized: {self.plc_code}")

    def connect(self) -> bool:
        """
        PLC에 연결

        Returns:
            연결 성공 여부

        Raises:
            PLCConnectionError: 연결 실패 시
            PLCTimeoutError: 연결 타임아웃 시
        """
        try:
            logger.info(f"🔌 [{self.plc_code}] Connecting to {self.ip_address}:{self.port} (timeout={self.timeout}s)...")

            self._plc = Type3E()
            # pymcprotocol의 connect() 메서드에 timeout 파라미터 전달
            # 연결 후 소켓에 timeout 설정
            self._plc.connect(self.ip_address, self.port)

            # Type3E 객체의 내부 소켓에 timeout 설정
            if hasattr(self._plc, 'sock') and self._plc.sock:
                self._plc.sock.settimeout(self.timeout)

            self._is_connected = True

            logger.info(f"✅ [{self.plc_code}] Connected successfully to {self.ip_address}:{self.port}")
            return True

        except Exception as e:
            self._is_connected = False
            error_type = type(e).__name__
            error_detail = str(e)

            # 더 자세한 오류 메시지
            if "timeout" in error_detail.lower():
                error_msg = f"Connection timeout to {self.ip_address}:{self.port} after {self.timeout}s"
                logger.error(f"⏱️  [{self.plc_code}] TIMEOUT - {error_msg} (Error: {error_type}: {error_detail})")
                raise PLCTimeoutError(error_msg, self.plc_code) from e
            elif "refused" in error_detail.lower():
                error_msg = f"Connection refused by {self.ip_address}:{self.port} (PLC may be offline or port closed)"
                logger.error(f"❌ [{self.plc_code}] CONNECTION REFUSED - {error_msg} (Error: {error_type}: {error_detail})")
                raise PLCConnectionError(error_msg, self.plc_code) from e
            elif "unreachable" in error_detail.lower():
                error_msg = f"Network unreachable to {self.ip_address}:{self.port} (Check network/firewall)"
                logger.error(f"🚫 [{self.plc_code}] UNREACHABLE - {error_msg} (Error: {error_type}: {error_detail})")
                raise PLCConnectionError(error_msg, self.plc_code) from e
            else:
                error_msg = f"Failed to connect to {self.ip_address}:{self.port}: {error_detail}"
                logger.error(f"💥 [{self.plc_code}] CONNECTION FAILED - {error_msg} (Error: {error_type})")
                raise PLCConnectionError(error_msg, self.plc_code) from e

    def disconnect(self) -> None:
        """PLC 연결 해제"""
        if self._plc and self._is_connected:
            try:
                self._plc.close()
                self._is_connected = False
                logger.info(f"PLC disconnected: {self.plc_code}")
            except Exception as e:
                logger.warning(f"[{self.plc_code}] Error during disconnect: {str(e)}")

    def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    def check_connection(self) -> bool:
        """
        실제 연결 상태 확인 (통신 테스트)

        Returns:
            연결 상태
        """
        if not self._is_connected or not self._plc:
            return False

        try:
            # 간단한 읽기 테스트로 연결 확인
            # 실패하면 연결이 끊어진 것으로 간주
            return True
        except:
            self._is_connected = False
            return False

    def reconnect(self, max_retries: int = 3, backoff_times: list = None) -> bool:
        """
        PLC 재연결 (Exponential Backoff)

        Args:
            max_retries: 최대 재시도 횟수 (기본 3)
            backoff_times: 재시도 간격 리스트 (초, 기본 [5, 10, 20])

        Returns:
            재연결 성공 여부
        """
        if backoff_times is None:
            backoff_times = [5, 10, 20]

        logger.info(f"[{self.plc_code}] Starting reconnection attempts (max: {max_retries})")

        for attempt in range(max_retries):
            try:
                # 기존 연결 정리
                self.disconnect()

                # 대기
                if attempt > 0:
                    wait_time = backoff_times[min(attempt - 1, len(backoff_times) - 1)]
                    logger.info(f"[{self.plc_code}] Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)

                # 재연결 시도
                logger.info(f"[{self.plc_code}] Reconnection attempt {attempt + 1}/{max_retries}")
                self.connect()

                logger.info(f"[{self.plc_code}] Reconnection successful on attempt {attempt + 1}")
                return True

            except Exception as e:
                logger.warning(f"[{self.plc_code}] Reconnection attempt {attempt + 1}/{max_retries} failed: {e}")

        logger.error(f"[{self.plc_code}] All reconnection attempts failed")
        return False

    def read_single(self, tag_address: str) -> Any:
        """
        단일 태그 읽기

        Args:
            tag_address: 태그 주소 (예: "D100", "X10")

        Returns:
            읽은 태그 값

        Raises:
            PLCConnectionError: 연결되지 않았을 때
            PLCTimeoutError: 읽기 타임아웃
            PLCProtocolError: 프로토콜 에러
            PLCReadError: 읽기 실패
        """
        if not self._is_connected or not self._plc:
            error_msg = "PLC is not connected"
            logger.error(f"[{self.plc_code}] {error_msg}")
            raise PLCConnectionError(error_msg, self.plc_code)

        try:
            start_time = time.time()
            logger.debug(f"[{self.plc_code}] Reading tag: {tag_address}")

            # pymcprotocol을 사용하여 태그 읽기 (batchread_wordunits 사용)
            # D100은 1개 워드 읽기
            values = self._plc.batchread_wordunits(headdevice=tag_address, readsize=1)

            # 결과가 리스트면 첫 번째 값, 아니면 그대로 반환
            value = values[0] if isinstance(values, list) and len(values) > 0 else values

            response_time = (time.time() - start_time) * 1000  # ms
            logger.info(f"[{self.plc_code}] Tag read successful: {tag_address} = {value} ({response_time:.2f}ms)")

            return value

        except TimeoutError as e:
            error_msg = f"Timeout reading tag {tag_address}"
            logger.error(f"[{self.plc_code}] {error_msg}")
            self._is_connected = False  # 연결 끊김 표시
            raise PLCTimeoutError(error_msg, self.plc_code) from e

        except (ConnectionError, OSError) as e:
            # 연결 끊김 감지
            error_msg = f"Connection lost while reading tag {tag_address}: {str(e)}"
            logger.error(f"[{self.plc_code}] {error_msg}")
            self._is_connected = False
            raise PLCConnectionError(error_msg, self.plc_code) from e

        except Exception as e:
            error_msg = f"Failed to read tag {tag_address}: {str(e)}"
            logger.error(f"[{self.plc_code}] {error_msg}")

            # 연결 관련 에러인지 확인
            if "connection" in str(e).lower() or "socket" in str(e).lower():
                self._is_connected = False

            # PLC 프로토콜 에러 파싱
            error_code = self._parse_error_code(str(e))
            if error_code:
                raise PLCProtocolError(error_msg, error_code, self.plc_code) from e

            raise PLCReadError(error_msg, self.plc_code) from e

    def read_batch(self, tag_addresses: List[str]) -> Dict[str, Any]:
        """
        배치 태그 읽기

        여러 태그를 한 번에 읽어서 통신 횟수를 줄입니다.
        연속된 주소는 자동으로 그룹화하여 최적화합니다.

        Args:
            tag_addresses: 태그 주소 리스트

        Returns:
            태그 주소 → 값 매핑 딕셔너리

        Raises:
            PLCConnectionError: 연결되지 않았을 때
            PLCTimeoutError: 읽기 타임아웃
            PLCProtocolError: 프로토콜 에러
            PLCReadError: 읽기 실패
        """
        if not self._is_connected or not self._plc:
            error_msg = "PLC is not connected"
            logger.error(f"[{self.plc_code}] {error_msg}")
            raise PLCConnectionError(error_msg, self.plc_code)

        if not tag_addresses:
            return {}

        start_time = time.time()
        results = {}
        errors = {}

        try:
            # 연속 주소 그룹화
            groups = group_continuous_addresses(tag_addresses)

            logger.debug(f"[{self.plc_code}] Batch reading {len(tag_addresses)} tags in {len(groups)} groups")

            # 각 그룹별로 배치 읽기
            for device_type, group_list in groups.items():
                for start_addr, count, tags in group_list:
                    try:
                        # 연속 태그 - batchread_wordunits 사용
                        head_device = format_device_address(device_type, start_addr)
                        values = self._plc.batchread_wordunits(headdevice=head_device, readsize=count)

                        # 결과 매핑
                        if isinstance(values, list):
                            for i, tag in enumerate(tags):
                                if i < len(values):
                                    results[tag] = values[i]
                                else:
                                    errors[tag] = "Index out of range"
                        else:
                            # 단일 값 반환된 경우
                            results[tags[0]] = values

                    except Exception as e:
                        # 개별 그룹 에러 - 개별 읽기로 폴백
                        logger.warning(f"[{self.plc_code}] Batch read failed for group {device_type}{start_addr}, falling back to individual reads: {e}")

                        for tag in tags:
                            try:
                                # 단일 태그도 batchread_wordunits 사용
                                value = self._plc.batchread_wordunits(headdevice=tag, readsize=1)
                                results[tag] = value[0] if isinstance(value, list) and len(value) > 0 else value
                            except Exception as e2:
                                errors[tag] = str(e2)
                                logger.error(f"[{self.plc_code}] Failed to read tag {tag}: {e2}")

            response_time = (time.time() - start_time) * 1000  # ms

            if errors:
                logger.warning(f"[{self.plc_code}] Batch read completed with {len(errors)} errors ({response_time:.2f}ms)")
            else:
                logger.info(f"[{self.plc_code}] Batch read successful: {len(results)} tags ({response_time:.2f}ms)")

            return results

        except TimeoutError as e:
            error_msg = f"Timeout reading batch tags"
            logger.error(f"[{self.plc_code}] {error_msg}")
            raise PLCTimeoutError(error_msg, self.plc_code) from e

        except Exception as e:
            error_msg = f"Failed to read batch tags: {str(e)}"
            logger.error(f"[{self.plc_code}] {error_msg}")

            # PLC 프로토콜 에러 파싱
            error_code = self._parse_error_code(str(e))
            if error_code:
                raise PLCProtocolError(error_msg, error_code, self.plc_code) from e

            raise PLCReadError(error_msg, self.plc_code) from e

    def _parse_error_code(self, error_message: str) -> Optional[str]:
        """
        PLC 프로토콜 에러 코드 파싱

        Args:
            error_message: 에러 메시지

        Returns:
            에러 코드 (있으면)
        """
        # pymcprotocol의 에러 메시지에서 에러 코드 추출
        # 예: "Error code: 0x1234" → "0x1234"
        if "error" in error_message.lower():
            parts = error_message.split()
            for i, part in enumerate(parts):
                if part.lower() in ["error", "code", "error_code"]:
                    if i + 1 < len(parts):
                        return parts[i + 1]

        return None

    def __enter__(self):
        """Context manager enter"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def __del__(self):
        """Destructor - 연결 정리"""
        self.disconnect()
