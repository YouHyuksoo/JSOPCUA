"""
SCADA System Settings

.env 파일에서 환경설정을 로드하는 모듈
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from backend directory
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"

if env_path.exists():
    load_dotenv(env_path)
    logging.info(f"[Settings] Loaded configuration from: {env_path}")
else:
    logging.warning(f"[Settings] No .env file found at {env_path}, using defaults")


class Settings:
    """SCADA 시스템 설정"""

    # =========================================================================
    # Logging Configuration
    # =========================================================================
    @property
    def LOG_LEVEL(self) -> str:
        """로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def LOG_LEVEL_INT(self) -> int:
        """로그 레벨 정수 값"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(self.LOG_LEVEL, logging.INFO)

    @property
    def LOG_COLORS(self) -> bool:
        """터미널 컬러 사용 여부"""
        value = os.getenv("LOG_COLORS", "true").lower()
        return value in ("true", "1", "yes", "on")

    @property
    def LOG_DIR(self) -> str:
        """로그 디렉토리 경로"""
        return os.getenv("LOG_DIR", "logs")

    @property
    def LOG_MAX_BYTES(self) -> int:
        """로그 파일 최대 크기 (bytes)"""
        return int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB

    @property
    def LOG_BACKUP_COUNT(self) -> int:
        """로그 파일 백업 개수"""
        return int(os.getenv("LOG_BACKUP_COUNT", "10"))

    # =========================================================================
    # Server Configuration
    # =========================================================================
    @property
    def API_HOST(self) -> str:
        """API 서버 호스트"""
        return os.getenv("API_HOST", "0.0.0.0")

    @property
    def API_PORT(self) -> int:
        """API 서버 포트"""
        return int(os.getenv("API_PORT", "8000"))

    @property
    def API_RELOAD(self) -> bool:
        """개발 모드 자동 리로드"""
        value = os.getenv("API_RELOAD", "false").lower()
        return value in ("true", "1", "yes", "on")

    @property
    def ENVIRONMENT(self) -> str:
        """환경 (development, production)"""
        return os.getenv("ENVIRONMENT", "development")

    # =========================================================================
    # Database Configuration
    # =========================================================================
    @property
    def DATABASE_PATH(self) -> str:
        """SQLite 데이터베이스 경로"""
        return os.getenv("DATABASE_PATH", "data/scada.db")

    # =========================================================================
    # Oracle Database Configuration
    # =========================================================================
    @property
    def ORACLE_HOST(self) -> str:
        """Oracle 데이터베이스 호스트"""
        return os.getenv("ORACLE_HOST", "localhost")

    @property
    def ORACLE_PORT(self) -> int:
        """Oracle 데이터베이스 포트"""
        return int(os.getenv("ORACLE_PORT", "1521"))

    @property
    def ORACLE_SERVICE_NAME(self) -> str:
        """Oracle 서비스명"""
        return os.getenv("ORACLE_SERVICE_NAME", "ORCL")

    @property
    def ORACLE_USERNAME(self) -> str:
        """Oracle 사용자명"""
        return os.getenv("ORACLE_USERNAME", "scada_user")

    @property
    def ORACLE_PASSWORD(self) -> str:
        """Oracle 비밀번호"""
        return os.getenv("ORACLE_PASSWORD", "scada_password")

    @property
    def ORACLE_POOL_MIN(self) -> int:
        """Oracle 커넥션 풀 최소 크기"""
        return int(os.getenv("ORACLE_POOL_MIN", "2"))

    @property
    def ORACLE_POOL_MAX(self) -> int:
        """Oracle 커넥션 풀 최대 크기"""
        return int(os.getenv("ORACLE_POOL_MAX", "5"))

    # =========================================================================
    # PLC Communication Configuration
    # =========================================================================
    @property
    def CONNECTION_TIMEOUT(self) -> int:
        """PLC 연결 타임아웃 (초)"""
        return int(os.getenv("CONNECTION_TIMEOUT", "5"))

    @property
    def READ_TIMEOUT(self) -> int:
        """PLC 읽기 타임아웃 (초)"""
        return int(os.getenv("READ_TIMEOUT", "3"))

    @property
    def POOL_SIZE_PER_PLC(self) -> int:
        """PLC당 커넥션 풀 크기"""
        return int(os.getenv("POOL_SIZE_PER_PLC", "5"))

    @property
    def IDLE_TIMEOUT(self) -> int:
        """커넥션 유휴 타임아웃 (초)"""
        return int(os.getenv("IDLE_TIMEOUT", "600"))

    # =========================================================================
    # Polling Configuration
    # =========================================================================
    @property
    def MAX_POLLING_GROUPS(self) -> int:
        """최대 폴링 그룹 수"""
        return int(os.getenv("MAX_POLLING_GROUPS", "10"))

    @property
    def DATA_QUEUE_SIZE(self) -> int:
        """데이터 큐 크기"""
        return int(os.getenv("DATA_QUEUE_SIZE", "10000"))

    @property
    def WEBSOCKET_BROADCAST_INTERVAL(self) -> float:
        """WebSocket 브로드캐스트 간격 (초)"""
        return float(os.getenv("WEBSOCKET_BROADCAST_INTERVAL", "1.0"))

    # =========================================================================
    # Buffer Configuration
    # =========================================================================
    @property
    def BUFFER_MAX_SIZE(self) -> int:
        """버퍼 최대 크기"""
        return int(os.getenv("BUFFER_MAX_SIZE", "100000"))

    @property
    def BUFFER_BATCH_SIZE(self) -> int:
        """배치 쓰기 크기"""
        return int(os.getenv("BUFFER_BATCH_SIZE", "500"))

    @property
    def BUFFER_BATCH_SIZE_MAX(self) -> int:
        """최대 배치 크기"""
        return int(os.getenv("BUFFER_BATCH_SIZE_MAX", "1000"))

    @property
    def BUFFER_WRITE_INTERVAL(self) -> float:
        """버퍼 쓰기 간격 (초)"""
        return float(os.getenv("BUFFER_WRITE_INTERVAL", "1.0"))

    @property
    def BUFFER_RETRY_COUNT(self) -> int:
        """버퍼 쓰기 재시도 횟수"""
        return int(os.getenv("BUFFER_RETRY_COUNT", "3"))

    @property
    def BACKUP_FILE_PATH(self) -> str:
        """백업 파일 경로"""
        return os.getenv("BACKUP_FILE_PATH", "backup")

    # =========================================================================
    # CORS Configuration
    # =========================================================================
    @property
    def CORS_ORIGINS(self) -> list:
        """CORS 허용 오리진 목록"""
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
        return [origin.strip() for origin in origins.split(",")]

    def display_config(self) -> None:
        """현재 설정을 출력"""
        logging.info("=" * 70)
        logging.info("SCADA System Configuration")
        logging.info("=" * 70)
        logging.info("[Logging]")
        logging.info(f"  LOG_LEVEL: {self.LOG_LEVEL}")
        logging.info(f"  LOG_COLORS: {self.LOG_COLORS}")
        logging.info(f"  LOG_DIR: {self.LOG_DIR}")
        logging.info(f"  LOG_MAX_BYTES: {self.LOG_MAX_BYTES:,} bytes")
        logging.info(f"  LOG_BACKUP_COUNT: {self.LOG_BACKUP_COUNT}")

        logging.info("[Server]")
        logging.info(f"  API_HOST: {self.API_HOST}")
        logging.info(f"  API_PORT: {self.API_PORT}")
        logging.info(f"  ENVIRONMENT: {self.ENVIRONMENT}")

        logging.info("[Database]")
        logging.info(f"  SQLite: {self.DATABASE_PATH}")
        logging.info(f"  Oracle: {self.ORACLE_USERNAME}@{self.ORACLE_HOST}:{self.ORACLE_PORT}/{self.ORACLE_SERVICE_NAME}")

        logging.info("[PLC Communication]")
        logging.info(f"  CONNECTION_TIMEOUT: {self.CONNECTION_TIMEOUT}s")
        logging.info(f"  READ_TIMEOUT: {self.READ_TIMEOUT}s")
        logging.info(f"  POOL_SIZE_PER_PLC: {self.POOL_SIZE_PER_PLC}")

        logging.info("[Polling]")
        logging.info(f"  MAX_POLLING_GROUPS: {self.MAX_POLLING_GROUPS}")
        logging.info(f"  DATA_QUEUE_SIZE: {self.DATA_QUEUE_SIZE:,}")

        logging.info("[Buffer]")
        logging.info(f"  BUFFER_MAX_SIZE: {self.BUFFER_MAX_SIZE:,}")
        logging.info(f"  BUFFER_BATCH_SIZE: {self.BUFFER_BATCH_SIZE}")
        logging.info(f"  BACKUP_FILE_PATH: {self.BACKUP_FILE_PATH}")

        logging.info("=" * 70)


# Singleton instance
settings = Settings()


# Export for easy import
__all__ = ["settings", "Settings"]
