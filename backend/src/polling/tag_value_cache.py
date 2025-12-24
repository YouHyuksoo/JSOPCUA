"""
Tag Value Cache - In-memory cache for fast change detection

메모리 기반 캐시로 폴링값 변경 감지 시 SQLite 조회를 제거하여 성능 개선.

주요 기능:
- 메모리에 태그의 이전값 저장 (O(1) 조회)
- 스레드 안전 (RLock 사용)
- 시작 시 SQLite에서 일괄 로드
- 실시간 업데이트
"""

import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TagValueCache:
    """
    In-memory cache for tag values enabling fast change detection.

    Stores last_value for each tag to avoid SQLite lookups during
    change detection in oracle_writer_thread.

    메모리 기반이므로 매 폴링마다의 변경 감지가 나노초 단위로 처리됨:
    - DB 기반: ~1-5ms (파일 I/O 오버헤드)
    - 캐시 기반: ~0.001ms (메모리 해시맵)

    Thread-safe using RLock for concurrent access from:
    - PollingThread (캐시 읽음)
    - OracleWriterThread (캐시 읽고 쓰기)
    - API 요청 (캐시 업데이트)

    Attributes:
        _cache: Dictionary storing tag values
                Key: f"{plc_code}:{tag_address}" (예: "PLC01:D100")
                Value: {"last_value": 값, "last_updated": 타임스탬프}
        _lock: RLock for thread-safe access
    """

    def __init__(self):
        """Initialize empty tag value cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        logger.info("TagValueCache initialized")

    def get(self, plc_code: str, tag_address: str) -> Optional[Any]:
        """
        Get last value for a tag (메모리에서 O(1) 조회).

        Args:
            plc_code: PLC identifier (예: 'PLC01')
            tag_address: Tag address (예: 'D100')

        Returns:
            Last stored value or None if not cached
        """
        key = f"{plc_code}:{tag_address}"
        with self._lock:
            return self._cache.get(key, {}).get('last_value')

    def set(self, plc_code: str, tag_address: str, value: Any, timestamp: Optional[datetime] = None):
        """
        Update cache with new value (메모리에 O(1)로 저장).

        Args:
            plc_code: PLC identifier
            tag_address: Tag address
            value: New value (str 권장)
            timestamp: Update timestamp (기본값: now)
        """
        key = f"{plc_code}:{tag_address}"
        with self._lock:
            self._cache[key] = {
                'last_value': value,
                'last_updated': timestamp or datetime.now()
            }

    def load_from_db(self, db_manager) -> int:
        """
        Initialize cache from SQLite database (시작 시에만 1회 실행).

        모든 활성 태그의 last_value를 메모리에 로드.
        이후 변경 감지는 메모리 캐시에서만 처리.

        Args:
            db_manager: SQLiteManager instance

        Returns:
            Number of tags loaded
        """
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # 실제 스키마: tags 테이블에 plc_code 컬럼 직접 포함
                cursor.execute("""
                    SELECT t.plc_code, t.tag_address, t.last_value, t.last_updated_at
                    FROM tags t
                    WHERE t.is_active = 1
                """)

                rows = cursor.fetchall()

                with self._lock:
                    for row in rows:
                        plc_code = row[0]
                        tag_address = row[1]
                        last_value = row[2]
                        last_updated = row[3]

                        key = f"{plc_code}:{tag_address}"
                        self._cache[key] = {
                            'last_value': last_value,
                            'last_updated': last_updated or datetime.now()
                        }

                logger.info(f"Loaded {len(self._cache)} tag values into cache from SQLite")
                return len(self._cache)

        except Exception as e:
            logger.error(f"Failed to load tag values from database: {e}", exc_info=True)
            return 0

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get entire cache (스냅샷 반환, 안전함).

        Returns:
            Copy of entire cache
        """
        with self._lock:
            return dict(self._cache)

    def clear(self):
        """Clear entire cache (재시작 시에만 사용)."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {count} tag values from cache")

    def size(self) -> int:
        """Get number of cached tags."""
        with self._lock:
            return len(self._cache)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.

        Returns:
            Dictionary with cache info
        """
        with self._lock:
            return {
                'cached_tags': len(self._cache),
                'estimated_memory_mb': (len(self._cache) * 200) / 1024 / 1024,  # 대략 200바이트/태그
            }

    def remove(self, plc_code: str, tag_address: str) -> bool:
        """
        Remove tag from cache (태그 삭제 시).

        Args:
            plc_code: PLC identifier
            tag_address: Tag address

        Returns:
            True if removed, False if not found
        """
        key = f"{plc_code}:{tag_address}"
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Removed {key} from cache")
                return True
            return False
