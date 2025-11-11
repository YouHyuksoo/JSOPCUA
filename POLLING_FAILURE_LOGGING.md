# 폴링 실패 로그 시스템

## 개요

PLC 폴링 실패 시 명령 실행 및 회신 과정을 **일자별 폴더 구조**로 상세 기록하는 로깅 시스템

---

## 폴더 구조

```
logs/
├─ scada.log                    # 일반 시스템 로그 (INFO)
├─ error.log                    # 에러 로그 (ERROR만)
├─ communication.log            # PLC 통신 로그
├─ performance.log              # 폴링 성능 메트릭
└─ polling_failures/            # 폴링 실패 로그 (일자별)
   ├─ 20250104/
   │  ├─ PLC01_failure_093015_123.log
   │  ├─ PLC01_failure_093045_456.log
   │  └─ PLC02_failure_100120_789.log
   ├─ 20250105/
   │  └─ PLC01_failure_080512_001.log
   └─ 20250106/
      └─ PLC03_failure_153022_555.log
```

**로그 파일명 규칙:**
- `{PLC코드}_failure_{HHMMSS}_{밀리초}.log`
- 예: `PLC01_failure_093015_123.log` → PLC01에서 09:30:15.123에 발생한 실패

---

## 로그 내용 (JSON 형식)

### 예시 1: 연결 실패 (CONNECTION_FAILED)

```json
{
  "timestamp": "2025-01-04T09:30:15.123456",
  "plc_code": "PLC01",
  "group_name": "Group1_Elevator",
  "error_type": "CONNECTION_FAILED",
  "error_message": "Connection refused: PLC not responding",
  "tag_addresses": [],
  "tag_count": 0,
  "poll_duration_ms": null,
  "retry_count": 0,
  "request": {
    "ip_address": "192.168.1.10",
    "port": 5010,
    "timeout": 5
  },
  "response": null
}
```

### 예시 2: 읽기 실패 (READ_ERROR)

```json
{
  "timestamp": "2025-01-04T09:30:45.678901",
  "plc_code": "PLC02",
  "group_name": "Group2_Welding",
  "error_type": "READ_ERROR",
  "error_message": "Read error: Invalid response code 0x4001",
  "tag_addresses": ["D100", "D200", "D300", "W100"],
  "tag_count": 4,
  "poll_duration_ms": 1250.5,
  "retry_count": 0,
  "request": null,
  "response": {
    "response_code": "0x4001"
  }
}
```

### 예시 3: 타임아웃 (TIMEOUT)

```json
{
  "timestamp": "2025-01-04T10:01:20.345678",
  "plc_code": "PLC03",
  "group_name": "Group3_Press",
  "error_type": "TIMEOUT",
  "error_message": "Polling timeout after 5000.0ms",
  "tag_addresses": ["M100", "M101", "M102"],
  "tag_count": 3,
  "poll_duration_ms": 5000.0,
  "retry_count": 0,
  "request": null,
  "response": null
}
```

---

## 사용 방법

### 1. 로깅 초기화 (main.py에서)

```python
from src.config.logging_config import initialize_logging

# 앱 시작 시 호출
initialize_logging(log_dir="logs")
```

### 2. 폴링 스레드에서 자동 로깅

폴링 실패 시 자동으로 `logs/polling_failures/YYYYMMDD/` 폴더에 로그 생성:

```python
# polling_thread.py의 execute_poll() 메서드에서 자동 처리됨
try:
    tag_values = self.pool_manager.read_batch(...)
except Exception as e:
    # 자동으로 failure_logger에 기록
    failure_logger.log_read_failure(...)
```

### 3. 수동 로깅 (필요 시)

```python
from src.polling.polling_logger import get_failure_logger

logger = get_failure_logger()

# 연결 실패 로깅
logger.log_connection_failure(
    plc_code="PLC01",
    group_name="Group1",
    ip_address="192.168.1.10",
    port=5010,
    error_message="Connection timeout",
    connection_timeout=5
)

# 읽기 실패 로깅
logger.log_read_failure(
    plc_code="PLC01",
    group_name="Group1",
    tag_addresses=["D100", "D200"],
    error_message="Invalid response",
    poll_duration_ms=1200.5,
    response_code="0x4001"
)

# 커스텀 실패 로깅 (모든 파라미터)
logger.log_failure(
    plc_code="PLC01",
    group_name="Group1",
    error_type="CUSTOM_ERROR",
    error_message="Custom error message",
    request_data={"key": "value"},
    response_data={"status": "error"},
    tag_addresses=["D100"],
    poll_duration_ms=500.0,
    retry_count=2
)
```

---

## 에러 타입

| Error Type | 설명 | 발생 조건 |
|------------|------|----------|
| `CONNECTION_FAILED` | PLC 연결 실패 | IP 연결 불가, 타임아웃 |
| `READ_ERROR` | 태그 읽기 실패 | 잘못된 응답 코드, 데이터 오류 |
| `TIMEOUT` | 폴링 타임아웃 | 설정된 시간 내 응답 없음 |
| `DATA_CORRUPTION` | 데이터 손상 | 체크섬 오류, 비정상 데이터 |
| `CUSTOM_ERROR` | 사용자 정의 에러 | 기타 에러 |

---

## 로그 정리 (자동)

30일 이상 지난 로그 폴더 자동 삭제:

```python
from src.polling.polling_logger import get_failure_logger

logger = get_failure_logger()
logger.cleanup_old_logs(days_to_keep=30)  # 30일 이상 지난 폴더 삭제
```

---

## 테스트

테스트 스크립트 실행:

```bash
cd backend
.venv\Scripts\python.exe src\scripts\test_polling_failure_log.py
```

**결과:**
- `logs/polling_failures/20250104/` 폴더에 4개 테스트 로그 파일 생성
- 각 로그 파일은 JSON 형식으로 상세 정보 포함

---

## 로그 활용 예시

### 1. 특정 PLC의 실패 로그 검색

```bash
# Windows
dir /s /b logs\polling_failures\*PLC01*.log

# Linux/Mac
find logs/polling_failures -name "*PLC01*.log"
```

### 2. 특정 날짜의 모든 실패 로그

```bash
cd logs/polling_failures/20250104
dir *.log
```

### 3. JSON 파싱 (Python)

```python
import json

with open('logs/polling_failures/20250104/PLC01_failure_093015_123.log', 'r') as f:
    log_data = json.load(f)
    print(f"Error: {log_data['error_message']}")
    print(f"Tags: {log_data['tag_addresses']}")
    print(f"Duration: {log_data['poll_duration_ms']}ms")
```

---

## 성능 영향

- **파일 I/O**: 비동기 처리 (메인 스레드 차단 없음)
- **디스크 사용량**: 실패 로그만 저장 (성공 로그 X)
- **예상 크기**: 로그 1건당 약 1KB, 하루 1000건 실패 시 약 1MB

---

## 설정

### 로그 디렉토리 변경

```python
from src.polling.polling_logger import get_failure_logger

# 커스텀 디렉토리
logger = get_failure_logger(base_log_dir="custom_logs/failures")
```

### 로그 보관 기간 변경

```python
# 7일만 보관
logger.cleanup_old_logs(days_to_keep=7)

# 90일 보관
logger.cleanup_old_logs(days_to_keep=90)
```

---

## 통합 로깅 시스템

| 로그 파일 | 용도 | 레벨 | 보관 정책 |
|----------|------|------|-----------|
| `scada.log` | 일반 시스템 로그 | INFO | 10MB × 10개 (Rotation) |
| `error.log` | 에러 로그만 | ERROR | 10MB × 10개 |
| `communication.log` | PLC 통신 | DEBUG | 10MB × 10개 |
| `performance.log` | 폴링 성능 메트릭 | INFO | 10MB × 10개 |
| `polling_failures/*` | 폴링 실패 상세 | - | 30일 보관 |

---

## 참고 파일

- **Logger 구현**: `backend/src/polling/polling_logger.py`
- **통합 설정**: `backend/src/config/logging_config.py`
- **Polling Thread**: `backend/src/polling/polling_thread.py`
- **테스트 스크립트**: `backend/src/scripts/test_polling_failure_log.py`

---

**Status:** ✅ 구현 완료
