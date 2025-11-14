# 터미널 로그 시스템 (Colorful Terminal Logging)

## 개요

SCADA 시스템의 로그를 터미널에서 컬러풀하게 표시하고, 환경변수 및 런타임으로 로그 레벨을 제어할 수 있는 기능

---

## 주요 기능

### 1. 컬러풀한 로그 출력

로그 레벨별로 다른 색상을 적용하여 터미널에서 가독성 향상:

| 로그 레벨 | 색상 | 용도 |
|----------|------|------|
| DEBUG | 회색 (Gray) | 상세 디버깅 정보 |
| INFO | 파란색 (Blue) | 일반 정보 메시지 |
| WARNING | 노란색 (Yellow) | 경고 메시지 |
| ERROR | 빨간색 (Red) | 에러 메시지 |
| CRITICAL | 굵은 빨간색 (Bold Red) | 치명적 에러 |

### 2. 환경변수 제어

`LOG_LEVEL` 환경변수로 터미널 로그 레벨 제어:

```bash
# Windows
set LOG_LEVEL=DEBUG
python backend/src/api/main.py

# Linux/Mac
export LOG_LEVEL=DEBUG
python backend/src/api/main.py

# 또는 한 줄로
LOG_LEVEL=DEBUG python backend/src/api/main.py
```

**사용 가능한 레벨:**
- `DEBUG`: 모든 로그 출력 (디버깅용)
- `INFO`: INFO 이상만 출력 (기본값)
- `WARNING`: WARNING 이상만 출력
- `ERROR`: ERROR 이상만 출력
- `CRITICAL`: CRITICAL만 출력

### 3. 런타임 레벨 변경

프로그램 실행 중에 로그 레벨 변경 가능:

```python
from src.config.logging_config import set_console_log_level
import logging

# DEBUG 레벨로 변경 (모든 로그 보기)
set_console_log_level(logging.DEBUG)

# ERROR 레벨로 변경 (에러만 보기)
set_console_log_level(logging.ERROR)

# INFO 레벨로 변경 (기본)
set_console_log_level(logging.INFO)
```

---

## 로그 구조

### 터미널 로그 포맷

```
[타임스탬프] | [레벨] | [로거명] | [메시지]
```

**예시:**
```
2025-11-05 00:55:12 | INFO     | polling.engine | Starting polling group: Group1_Elevator
2025-11-05 00:55:12 | WARNING  | polling.engine | Attempting to connect to PLC02...
2025-11-05 00:55:12 | ERROR    | polling.engine | Polling failed: Connection refused
```

### 파일 로그 포맷 (더 상세)

```
[타임스탬프] | [레벨] | [로거명] | [함수명:라인] | [메시지]
```

**예시:**
```
2025-11-05 00:55:12 | INFO     | polling.engine | execute_poll:145 | Starting polling group
```

---

## 사용 방법

### 1. 앱 시작 시 초기화

```python
from src.config.logging_config import initialize_logging

# 기본 설정 (환경변수 LOG_LEVEL 사용)
initialize_logging()

# 직접 레벨 지정
initialize_logging(console_level=logging.DEBUG)

# 컬러 비활성화 (서버 환경)
initialize_logging(use_colors=False)
```

### 2. 로깅 사용

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고 메시지")
logger.error("에러 발생")
logger.critical("치명적 에러")
```

### 3. 예외 로깅 (Traceback 포함)

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    logger.error("계산 중 오류 발생", exc_info=True)
```

---

## 로그 레벨 가이드

### 개발 환경

```bash
# 모든 로그 보기 (디버깅)
set LOG_LEVEL=DEBUG
```

**용도:**
- 폴링 상세 과정 확인
- PLC 통신 패킷 확인
- 성능 메트릭 상세 분석

### 운영 환경

```bash
# 일반 정보 및 경고, 에러만 보기
set LOG_LEVEL=INFO
```

**용도:**
- 정상 운영 중 주요 이벤트 확인
- 에러 및 경고 모니터링
- 불필요한 디버그 로그 제거

### 프로덕션 환경

```bash
# 에러만 보기
set LOG_LEVEL=ERROR
```

**용도:**
- 에러 발생 시에만 알림
- 로그 노이즈 최소화
- 성능 최적화

---

## 테스트

### 테스트 스크립트 실행

```bash
cd backend
.venv\Scripts\python.exe src\scripts\test_terminal_logging.py
```

### 테스트 시나리오

1. **모든 로그 레벨 테스트**
   - DEBUG, INFO, WARNING, ERROR, CRITICAL 출력 확인
   - 각 레벨별 색상 확인

2. **환경변수 제어 테스트**
   - LOG_LEVEL=DEBUG로 실행
   - LOG_LEVEL=ERROR로 실행
   - 레벨에 따라 출력되는 로그 차이 확인

3. **런타임 레벨 변경 테스트**
   - INFO → DEBUG → ERROR → INFO 순서로 변경
   - 각 레벨에서 로그 출력 확인

4. **폴링 시뮬레이션**
   - 성공 폴링
   - 연결 실패
   - 읽기 에러
   - 성능 경고

5. **예외 로깅**
   - Traceback 포함된 에러 로그 확인

---

## 로그 구성 요소

### 1. Console Handler (터미널)
- **레벨**: 환경변수 LOG_LEVEL 또는 파라미터로 제어
- **포맷**: 컬러풀한 포맷 (ColoredFormatter)
- **출력**: 실시간 터미널 출력

### 2. File Handler (파일)
- **scada.log**: INFO 이상 모든 로그 (10MB × 10개 로테이션)
- **error.log**: ERROR 이상만 (10MB × 10개)
- **communication.log**: PLC 통신 로그 (DEBUG 레벨)
- **performance.log**: 폴링 성능 메트릭
- **polling_failures/**: 폴링 실패 상세 로그 (일자별 폴더)

---

## 실제 사용 예시

### 예시 1: 폴링 엔진 로그

```python
# polling_thread.py
logger = logging.getLogger("polling.engine")

logger.info(f"Starting polling group: {self.group_name}")
logger.debug(f"Polling {len(tag_addresses)} tags from PLC {self.plc_code}")

try:
    tag_values = self.pool_manager.read_batch(...)
    logger.info(f"Successfully read {len(tag_values)} tags")
except Exception as e:
    logger.error(f"Polling failed: {e}")
```

**터미널 출력 (LOG_LEVEL=INFO):**
```
2025-11-05 00:55:12 | INFO     | polling.engine | Starting polling group: Group1_Elevator
2025-11-05 00:55:12 | INFO     | polling.engine | Successfully read 3 tags
```

**터미널 출력 (LOG_LEVEL=DEBUG):**
```
2025-11-05 00:55:12 | INFO     | polling.engine | Starting polling group: Group1_Elevator
2025-11-05 00:55:12 | DEBUG    | polling.engine | Polling 3 tags from PLC PLC01
2025-11-05 00:55:12 | INFO     | polling.engine | Successfully read 3 tags
```

### 예시 2: PLC 통신 로그

```python
# pymcprotocol (통신 라이브러리)
comm_logger = logging.getLogger("pymcprotocol")

comm_logger.debug(f"Connecting to {ip}:{port}")
comm_logger.debug(f"Sending batch read: {tag_addresses}")
comm_logger.debug(f"Received response: {response}")
```

**터미널 출력 (LOG_LEVEL=DEBUG):**
```
2025-11-05 00:55:12 | DEBUG    | pymcprotocol | Connecting to 192.168.1.10:5010
2025-11-05 00:55:12 | DEBUG    | pymcprotocol | Sending batch read: ['D100', 'D200', 'D300']
2025-11-05 00:55:12 | DEBUG    | pymcprotocol | Received response: [100, 200, 300]
```

### 예시 3: 에러 발생 시

```python
try:
    connection = self.plc_pool.get_connection(timeout=5)
except TimeoutError as e:
    logger.error(f"Connection timeout: {e}", exc_info=True)
```

**터미널 출력 (모든 레벨):**
```
2025-11-05 00:55:12 | ERROR    | polling.engine | Connection timeout: PLC not responding
Traceback (most recent call last):
  File "polling_thread.py", line 145, in execute_poll
    connection = self.plc_pool.get_connection(timeout=5)
TimeoutError: PLC not responding
```

---

## 성능 고려사항

### 로그 레벨별 성능 영향

| 레벨 | 성능 영향 | 권장 환경 |
|------|----------|----------|
| DEBUG | 높음 (모든 로그) | 개발 환경 |
| INFO | 보통 | 운영 환경 (기본) |
| WARNING | 낮음 | 모니터링 환경 |
| ERROR | 매우 낮음 | 프로덕션 환경 |

### 컬러 출력 성능

- **터미널 환경**: ANSI 색상 코드 사용 (성능 영향 미미)
- **서버 환경 (백그라운드)**: `use_colors=False` 권장

```python
# 서버 환경 (systemd, Docker 등)
initialize_logging(use_colors=False)
```

---

## 통합 로깅 시스템

### 로그 흐름도

```
Application Code
      |
      v
[Logger] ──┬──> [Console Handler (터미널)] → 컬러풀한 실시간 출력
           |
           ├──> [File Handler (scada.log)] → 일반 로그
           |
           ├──> [Error Handler (error.log)] → 에러만
           |
           ├──> [Comm Handler (communication.log)] → PLC 통신
           |
           ├──> [Perf Handler (performance.log)] → 성능 메트릭
           |
           └──> [Failure Logger (polling_failures/)] → 실패 상세 로그
```

---

## 참고 파일

- **로깅 설정**: `backend/src/config/logging_config.py`
- **실패 로거**: `backend/src/polling/polling_logger.py`
- **테스트 스크립트**: `backend/src/scripts/test_terminal_logging.py`
- **실패 로그 문서**: `POLLING_FAILURE_LOGGING.md`

---

## FAQ

### Q: 터미널에 컬러가 안 나와요
A: Windows 10 이상에서는 자동으로 지원됩니다. 이전 버전은 `use_colors=False`로 설정하세요.

### Q: 로그가 너무 많이 출력돼요
A: `LOG_LEVEL=WARNING` 또는 `LOG_LEVEL=ERROR`로 설정하세요.

### Q: 파일에는 모든 로그를 남기고 터미널에는 에러만 보고 싶어요
A: 가능합니다. 터미널 레벨만 변경하면 됩니다:
```python
initialize_logging(console_level=logging.ERROR)
# 파일은 여전히 INFO 레벨로 모든 로그 저장
```

### Q: 실행 중에 레벨을 변경할 수 있나요?
A: 네, `set_console_log_level(logging.DEBUG)` 함수를 사용하세요.

---

**Status:** ✅ 구현 완료

**최종 업데이트:** 2025-11-05
