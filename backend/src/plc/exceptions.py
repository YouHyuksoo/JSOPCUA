"""
PLC Communication Exceptions

PLC 통신 관련 예외 클래스를 정의합니다.
"""


class PLCException(Exception):
    """PLC 통신 기본 예외"""
    def __init__(self, message: str, plc_code: str = None):
        self.message = message
        self.plc_code = plc_code
        super().__init__(self.format_message())

    def format_message(self) -> str:
        if self.plc_code:
            return f"[{self.plc_code}] {self.message}"
        return self.message


class PLCConnectionError(PLCException):
    """PLC 연결 실패 예외"""
    pass


class PLCTimeoutError(PLCException):
    """PLC 통신 타임아웃 예외"""
    pass


class PLCProtocolError(PLCException):
    """PLC 프로토콜 에러 예외"""
    def __init__(self, message: str, error_code: str = None, plc_code: str = None):
        self.error_code = error_code
        super().__init__(message, plc_code)

    def format_message(self) -> str:
        base_msg = super().format_message()
        if self.error_code:
            return f"{base_msg} (Error Code: {self.error_code})"
        return base_msg


class PLCReadError(PLCException):
    """PLC 읽기 실패 예외"""
    pass


class PLCPoolExhaustedError(PLCException):
    """Connection Pool 고갈 예외"""
    pass


class PLCInactiveError(PLCException):
    """PLC 비활성 상태 예외"""
    pass
