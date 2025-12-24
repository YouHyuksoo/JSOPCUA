"""
Logging Configuration for SCADA System

폴링 로그 설정 (크기 기반 로테이션 - 멀티프로세스 안전):
- 일반 로그: logs/scada.log (INFO 레벨) - 10MB 도달 시 백업
- 에러 로그: logs/error.log (ERROR 레벨) - 10MB 도달 시 백업
- 통신 로그: logs/communication.log (PLC 통신 전용) - 10MB 도달 시 백업
- 성능 로그: logs/performance.log (폴링 성능 메트릭) - 10MB 도달 시 백업
- PLC 로그: logs/plc.log (PLC 관련) - 10MB 도달 시 백업
- 폴링 로그: logs/polling.log (폴링 엔진) - 10MB 도달 시 백업
- Oracle 로그: logs/oracle_writer.log (Oracle 연동) - 10MB 도달 시 백업
- 실패 로그: logs/polling_failures/YYYYMMDD/*.log (일자별 폴더)

로그 로테이션:
- 파일 크기(10MB) 도달 시 자동 로테이션 (ConcurrentLogHandler)
- 백업 파일명 형식: {파일명}.1, {파일명}.2 ... (예: scada.log.1)
- 최대 백업 개수: LOG_BACKUP_COUNT (기본값: 10개)

터미널 로그 레벨 설정:
- 환경변수 LOG_LEVEL로 제어 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 기본값: INFO
"""

import logging
import logging.handlers
from concurrent_log_handler import ConcurrentRotatingFileHandler
from pathlib import Path
from datetime import datetime

# Import settings from .env file
try:
    from .settings import settings
except ImportError:
    # Fallback if settings is not available
    class Settings:
        LOG_LEVEL = "INFO"
        LOG_LEVEL_INT = logging.INFO
        LOG_COLORS = True
        LOG_DIR = "logs"
        LOG_MAX_BYTES = 10485760
        LOG_BACKUP_COUNT = 10
    settings = Settings()


# ANSI Color Codes for Terminal
class ColorCodes:
    """터미널 컬러 코드"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Foreground Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright Foreground Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class ColoredFormatter(logging.Formatter):
    """
    컬러풀한 로그 포맷터

    로그 레벨별 색상:
    - DEBUG: 회색
    - INFO: 파란색
    - WARNING: 노란색
    - ERROR: 빨간색
    - CRITICAL: 굵은 빨간색
    """

    LEVEL_COLORS = {
        logging.DEBUG: ColorCodes.BRIGHT_BLACK,
        logging.INFO: ColorCodes.BRIGHT_BLUE,
        logging.WARNING: ColorCodes.BRIGHT_YELLOW,
        logging.ERROR: ColorCodes.BRIGHT_RED,
        logging.CRITICAL: ColorCodes.BOLD + ColorCodes.BRIGHT_RED,
    }

    def format(self, record):
        # 레벨별 색상 적용
        level_color = self.LEVEL_COLORS.get(record.levelno, ColorCodes.WHITE)

        # 레벨명 컬러링
        levelname_colored = f"{level_color}{record.levelname:8s}{ColorCodes.RESET}"

        # 타임스탬프 컬러 (회색)
        timestamp = self.formatTime(record, self.datefmt)
        timestamp_colored = f"{ColorCodes.BRIGHT_BLACK}{timestamp}{ColorCodes.RESET}"

        # 로거명 컬러 (청록색)
        logger_name_colored = f"{ColorCodes.CYAN}{record.name}{ColorCodes.RESET}"

        # 메시지 (레벨별 색상)
        message = record.getMessage()
        message_colored = f"{level_color}{message}{ColorCodes.RESET}"

        # 최종 포맷
        return f"{timestamp_colored} | {levelname_colored} | {logger_name_colored} | {message_colored}"


def get_log_level_from_settings() -> int:
    """
    .env 설정 파일에서 로그 레벨 가져오기

    .env 파일의 LOG_LEVEL:
    - DEBUG, INFO, WARNING, ERROR, CRITICAL
    - 기본값: INFO

    Returns:
        int: logging 모듈의 레벨 상수
    """
    return settings.LOG_LEVEL_INT


def setup_logging(log_dir: str = None, console_level: int = None, use_colors: bool = None):
    """
    SCADA 시스템 로깅 설정

    Args:
        log_dir: 로그 파일 저장 디렉토리 (None이면 .env의 LOG_DIR 사용)
        console_level: 콘솔 로그 레벨 (None이면 .env의 LOG_LEVEL 사용)
        use_colors: 터미널 컬러 사용 여부 (None이면 .env의 LOG_COLORS 사용)
    """
    # .env 파일에서 기본값 가져오기
    if log_dir is None:
        log_dir = settings.LOG_DIR
    if console_level is None:
        console_level = get_log_level_from_settings()
    if use_colors is None:
        use_colors = settings.LOG_COLORS

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Root logger 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # =========================================================================
    # 1. Console Handler (환경변수 또는 설정된 레벨)
    # =========================================================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    if use_colors:
        # 컬러풀한 포맷 사용
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # 일반 포맷 (서버 환경 등에서 사용)
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 현재 로그 레벨 출력
    level_name = logging.getLevelName(console_level)
    source = ".env file" if console_level == get_log_level_from_settings() else "parameter"
    logging.info(f"[Logging] Console log level: {level_name} (from {source})")
    logging.info(f"[Logging] Log directory: {log_path.absolute()}")
    logging.info(f"[Logging] Colors enabled: {use_colors}")

    # =========================================================================
    # 2. General Log File (scada.log) - INFO 레벨 (크기 기반 로테이션)
    # =========================================================================
    general_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "scada.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # general_handler.suffix = "%Y%m%d"  # ConcurrentRotatingFileHandler는 날짜 기반 suffix를 지원하지 않음
    general_handler.setLevel(logging.INFO)
    general_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    general_handler.setFormatter(general_formatter)
    root_logger.addHandler(general_handler)

    # =========================================================================
    # 3. Error Log File (error.log) - ERROR 레벨만 (크기 기반 로테이션)
    # =========================================================================
    error_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "error.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # error_handler.suffix = "%Y%m%d"
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d\n%(message)s\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    # =========================================================================
    # 4. Communication Log (communication.log) - PLC 통신 전용 (크기 기반 로테이션)
    # =========================================================================
    comm_logger = logging.getLogger('pymcprotocol')
    comm_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "communication.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # comm_handler.suffix = "%Y%m%d"
    comm_handler.setLevel(logging.DEBUG)
    comm_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | PLC=%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    comm_handler.setFormatter(comm_formatter)
    comm_logger.addHandler(comm_handler)
    comm_logger.setLevel(logging.DEBUG)
    comm_logger.propagate = False  # 상위 로거로 전파하지 않음

    # =========================================================================
    # 5. Performance Log (performance.log) - 폴링 성능 메트릭 (크기 기반 로테이션)
    # =========================================================================
    perf_logger = logging.getLogger('polling.performance')
    perf_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "performance.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # perf_handler.suffix = "%Y%m%d"
    perf_handler.setLevel(logging.INFO)
    perf_formatter = logging.Formatter(
        fmt='%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    perf_handler.setFormatter(perf_formatter)
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    perf_logger.propagate = False

    # =========================================================================
    # 6. PLC Log (plc.log) - PLC 관련 로그 (크기 기반 로테이션)
    # =========================================================================
    plc_logger = logging.getLogger('plc')
    plc_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "plc.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # plc_handler.suffix = "%Y%m%d"
    plc_handler.setLevel(logging.INFO)
    plc_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    plc_handler.setFormatter(plc_formatter)
    plc_logger.addHandler(plc_handler)
    plc_logger.setLevel(logging.INFO)
    plc_logger.propagate = False

    # =========================================================================
    # 7. Polling Log (polling.log) - 폴링 엔진 로그 (크기 기반 로테이션)
    # =========================================================================
    polling_logger = logging.getLogger('polling')
    polling_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "polling.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # polling_handler.suffix = "%Y%m%d"
    polling_handler.setLevel(logging.INFO)
    polling_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    polling_handler.setFormatter(polling_formatter)
    polling_logger.addHandler(polling_handler)
    polling_logger.setLevel(logging.INFO)
    polling_logger.propagate = False

    # =========================================================================
    # 8. Oracle Writer Log (oracle_writer.log) - Oracle 연동 로그 (크기 기반 로테이션)
    # =========================================================================
    oracle_logger = logging.getLogger('oracle_writer')
    oracle_handler = ConcurrentRotatingFileHandler(
        filename=log_path / "oracle_writer.log",
        mode='a',
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    # oracle_handler.suffix = "%Y%m%d"
    oracle_handler.setLevel(logging.INFO)
    oracle_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    oracle_handler.setFormatter(oracle_formatter)
    oracle_logger.addHandler(oracle_handler)
    oracle_logger.setLevel(logging.INFO)
    oracle_logger.propagate = False

    logging.info(f"Logging configured: log_dir={log_path.absolute()}")


def log_performance_metrics(
    group_name: str,
    plc_code: str,
    poll_time_ms: float,
    tag_count: int,
    success: bool
):
    """
    폴링 성능 메트릭 로깅

    Args:
        group_name: 폴링 그룹명
        plc_code: PLC 코드
        poll_time_ms: 폴링 소요 시간 (ms)
        tag_count: 폴링한 태그 개수
        success: 성공 여부
    """
    perf_logger = logging.getLogger('polling.performance')
    status = "SUCCESS" if success else "FAILED"
    perf_logger.info(
        f"Group={group_name} | PLC={plc_code} | Tags={tag_count} | "
        f"Time={poll_time_ms:.2f}ms | Status={status}"
    )


# 초기화 함수
def initialize_logging(log_dir: str = None, console_level: int = None, use_colors: bool = None):
    """
    로깅 초기화 (앱 시작 시 호출)

    Args:
        log_dir: 로그 디렉토리 경로 (None이면 .env 파일 사용)
        console_level: 콘솔 로그 레벨 (None이면 .env 파일 사용)
        use_colors: 터미널 컬러 사용 여부 (None이면 .env 파일 사용)

    Examples:
        # .env 파일 설정 사용
        initialize_logging()

        # 직접 레벨 지정 (파라미터가 .env보다 우선)
        initialize_logging(console_level=logging.DEBUG)

        # 컬러 비활성화 (서버 환경)
        initialize_logging(use_colors=False)
    """
    setup_logging(log_dir, console_level, use_colors)

    # 시작 메시지
    logging.info("=" * 70)
    logging.info("SCADA System Starting")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    logging.info("=" * 70)


def set_console_log_level(level: int):
    """
    런타임에 콘솔 로그 레벨 변경

    Args:
        level: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL

    Examples:
        # DEBUG 레벨로 변경 (모든 로그 출력)
        set_console_log_level(logging.DEBUG)

        # ERROR 레벨로 변경 (에러만 출력)
        set_console_log_level(logging.ERROR)
    """
    root_logger = logging.getLogger()

    # 콘솔 핸들러 찾기
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            old_level = logging.getLevelName(handler.level)
            new_level = logging.getLevelName(level)
            handler.setLevel(level)
            logging.info(f"Console log level changed: {old_level} → {new_level}")
            return

    logging.warning("Console handler not found, cannot change log level")


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 인스턴스 가져오기

    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)

    Returns:
        logging.Logger: 로거 인스턴스

    Examples:
        logger = get_logger(__name__)
        logger.info("Hello, World!")
    """
    return logging.getLogger(name)
