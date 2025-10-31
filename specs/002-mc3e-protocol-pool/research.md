# Research: MC 3E ASCII 프로토콜 통신 및 Connection Pool

**Feature**: MC 3E ASCII 프로토콜 통신 및 Connection Pool
**Date**: 2025-10-31

## Research Areas

### 1. pymcprotocol 라이브러리

**Decision**: pymcprotocol 1.0+ 사용

**Rationale**:
- Mitsubishi MC 프로토콜 (3E, 4E) 공식 지원
- TCP/IP 및 UDP 통신 지원
- 배치 읽기/쓰기 기능 내장 (batchread_wordunits)
- Python 3.7+ 호환
- MIT 라이선스로 상업적 사용 가능
- Active maintenance (2024년 마지막 업데이트)

**Alternatives Considered**:
- **pymelsec**: 구형 라이브러리, 업데이트 중단
- **snap7** (Siemens용): Mitsubishi 미지원
- **직접 구현**: 프로토콜 복잡도 높고 개발 시간 과다

**Implementation Notes**:
```python
from pymcprotocol import Type3E

# 기본 사용법
plc = Type3E()
plc.connect(ip="192.168.1.10", port=5010)
value = plc.batchread_wordunits(headdevice="D100", readsize=10)
plc.close()
```

---

### 2. Connection Pool 설계 패턴

**Decision**: Queue 기반 Connection Pool 패턴 사용

**Rationale**:
- Python의 `queue.Queue`는 스레드 안전 (thread-safe)
- LIFO 또는 FIFO 모드 선택 가능
- 풀 크기 제한 및 블로킹/타임아웃 지원
- 표준 라이브러리로 추가 의존성 불필요
- Connection Pool에 대한 업계 표준 패턴

**Alternatives Considered**:
- **Lock 기반 리스트**: 복잡도 증가, 에러 발생 가능성 높음
- **Semaphore만 사용**: 연결 객체 관리가 어려움
- **Third-party 라이브러리** (sqlalchemy.pool): PLC 연결에 오버킬

**Implementation Pattern**:
```python
import queue
import threading

class ConnectionPool:
    def __init__(self, max_size=5):
        self._pool = queue.Queue(maxsize=max_size)
        self._lock = threading.Lock()
        self._connections = []

    def get_connection(self, timeout=5):
        try:
            conn = self._pool.get(timeout=timeout)
        except queue.Empty:
            # 새 연결 생성 (크기 제한 확인 필요)
            conn = self._create_connection()
        return conn

    def return_connection(self, conn):
        self._pool.put(conn)
```

---

### 3. 배치 읽기 최적화

**Decision**: 연속 메모리 영역을 그룹화하여 batchread 사용

**Rationale**:
- MC 프로토콜은 연속된 디바이스 주소를 한 번에 읽기 가능
- D100~D149 (50개)를 1회 통신으로 읽으면 개별 50회 대비 10배 이상 빠름
- pymcprotocol의 `batchread_wordunits`가 최적화되어 있음
- 네트워크 왕복 시간 (RTT) 절감 효과 큼

**Alternatives Considered**:
- **개별 읽기**: 단순하지만 느림 (태그당 50ms 요구사항 충족 어려움)
- **비연속 주소 멀티 읽기**: MC 프로토콜 미지원, 프로토콜 확장 필요

**Implementation Strategy**:
1. 태그 주소를 파싱하여 디바이스 타입과 번호 분리 (D100 → D, 100)
2. 동일 디바이스 타입, 연속 주소를 그룹화
3. 각 그룹에 대해 batchread_wordunits 호출
4. 비연속 주소는 개별 읽기로 폴백

```python
# 예시: D100, D101, D102, D200 → 2개 그룹
# Group 1: D100-D102 (batch)
# Group 2: D200 (single)
```

---

### 4. 연결 끊김 감지 및 재연결

**Decision**: Socket timeout + 예외 처리 기반 감지, Exponential Backoff 재연결

**Rationale**:
- pymcprotocol은 TCP 소켓 기반이므로 `socket.timeout` 예외로 감지 가능
- `OSError`, `ConnectionError` 등으로 연결 끊김 감지
- Exponential Backoff: 첫 재시도 5초 → 10초 → 20초 (최대 3회)
- PLC 부담 감소 및 네트워크 복구 시간 확보

**Alternatives Considered**:
- **Heartbeat 방식**: 추가 통신 부담, PLC 리소스 낭비
- **고정 재시도 간격**: 네트워크 복구 시간 부족 시 실패율 높음

**Implementation**:
```python
retries = 0
backoff = [5, 10, 20]  # seconds

while retries < 3:
    try:
        plc.connect(ip, port)
        break
    except (OSError, ConnectionError, TimeoutError) as e:
        logger.warning(f"Reconnect attempt {retries+1} failed: {e}")
        time.sleep(backoff[retries])
        retries += 1
```

---

### 5. 타임아웃 처리

**Decision**: Socket level timeout (5초) + Application level timeout (10초)

**Rationale**:
- **Socket timeout (5초)**: TCP 연결 및 읽기/쓰기 작업 타임아웃
- **Application timeout (10초)**: 전체 요청 처리 시간 제한 (재시도 포함)
- 2-tier timeout으로 빠른 실패 감지 + 전체 시간 제어

**Alternatives Considered**:
- **단일 timeout**: 세밀한 제어 불가
- **No timeout**: 무한 대기 가능성, 리소스 고갈

**Implementation**:
```python
# Socket level
plc.settimeout(5)  # pymcprotocol socket timeout

# Application level
import threading
timer = threading.Timer(10.0, lambda: plc.close())
timer.start()
try:
    result = plc.batchread_wordunits(...)
finally:
    timer.cancel()
```

---

### 6. 유휴 연결 정리

**Decision**: Idle timeout (10분) + 주기적 정리 (1분마다 체크)

**Rationale**:
- 장시간 사용하지 않는 연결은 PLC 측에서 끊을 수 있음
- 연결 풀에서 주기적으로 오래된 연결 제거하여 리소스 회수
- 1분마다 백그라운드 스레드가 체크

**Implementation**:
```python
class PooledConnection:
    def __init__(self, conn):
        self.conn = conn
        self.last_used = time.time()

    def is_idle(self, timeout=600):  # 10 minutes
        return (time.time() - self.last_used) > timeout

# Background cleanup thread
def cleanup_idle_connections():
    while True:
        time.sleep(60)  # Check every minute
        for conn in pool.get_all_connections():
            if conn.is_idle():
                conn.close()
                pool.remove(conn)
```

---

### 7. 로깅 전략

**Decision**: Python logging 모듈, INFO/WARNING/ERROR 레벨 분리

**Rationale**:
- 표준 라이브러리 사용
- 로그 파일 rotati on 지원 (RotatingFileHandler)
- 로그 레벨별 필터링 가능
- 구조화된 로그 메시지 (timestamp, PLC ID, 이벤트 타입)

**Log Levels**:
- **DEBUG**: 상세 프로토콜 메시지 (개발용)
- **INFO**: 연결/끊김, 읽기 성공
- **WARNING**: 재연결 시도, 타임아웃
- **ERROR**: 연결 실패, 프로토콜 에러
- **CRITICAL**: PLC 비활성화

**Implementation**:
```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('plc')
handler = RotatingFileHandler('logs/plc.log', maxBytes=10MB, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info(f"PLC01 connected: {ip}:{port}")
logger.warning(f"PLC01 reconnect attempt {retry}/3")
logger.error(f"PLC01 connection failed: {error}")
```

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| PLC Protocol | pymcprotocol | 1.0+ | MC 3E ASCII 통신 |
| Connection Pool | queue.Queue | stdlib | 스레드 안전 풀 관리 |
| Threading | threading | stdlib | 멀티스레딩 지원 |
| Database | SQLite | 3.40+ | PLC 설정 저장 (Feature 1) |
| Logging | logging | stdlib | 이벤트 로깅 |
| Testing | pytest | 7.4+ | 단위/통합 테스트 |
| Mocking | unittest.mock | stdlib | PLC 모킹 |

---

## Performance Considerations

1. **Connection Reuse**: 연결 생성 비용 100-200ms → 재사용으로 <5ms
2. **Batch Read**: 50개 태그 개별 읽기 2500ms → 배치 500ms (5배 향상)
3. **Concurrent Connections**: PLC당 5개 연결로 동시 요청 처리
4. **Async I/O 미사용**: pymcprotocol이 동기식이므로 스레드 기반 병렬성 사용

**Expected Performance**:
- 단일 태그 읽기: 평균 30-50ms (네트워크 RTT 20-30ms + 처리 10ms)
- 배치 읽기 50개: 평균 400-500ms
- Connection Pool hit rate: >90% (재사용률)

---

## Security & Error Handling

**Security**:
- PLC 연결은 내부 네트워크만 허용 (방화벽 설정)
- 인증 없음 (MC 프로토콜 특성)
- SQLite DB에 PLC IP/포트만 저장 (credential 없음)

**Error Handling**:
- 모든 PLC 통신 예외를 catch하고 로그 기록
- 재시도 로직으로 일시적 오류 복구
- 영구 실패 시 PLC 비활성 상태로 마킹
- 상위 레이어로 명확한 에러 메시지 전달

---

## References

- [pymcprotocol Documentation](https://pypi.org/project/pymcprotocol/)
- [Mitsubishi MC Protocol Reference Manual](https://www.mitsubishielectric.com/)
- [Python Queue Documentation](https://docs.python.org/3/library/queue.html)
- [Connection Pool Design Pattern](https://en.wikipedia.org/wiki/Connection_pool)
