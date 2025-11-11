# Data Model: 통합 테스트 및 배포 준비

**Feature**: 008-integration-test-deployment  
**Date**: 2025-11-04

## Overview

Feature 8은 새로운 데이터베이스 테이블을 생성하지 않습니다. 대신, 테스트 결과 및 성능 메트릭을 파일 시스템에 저장합니다 (JSON, CSV 형식).

## Entities

### 1. IntegrationTestResult (JSON)

**Purpose**: E2E 통합 테스트 실행 결과를 저장

**Fields**:
- `execution_id`: string (UUID) - 테스트 실행 고유 ID
- `timestamp`: string (ISO 8601) - 테스트 시작 시간
- `total_tests`: integer - 총 테스트 수
- `passed`: integer - 성공한 테스트 수
- `failed`: integer - 실패한 테스트 수
- `skipped`: integer - 건너뛴 테스트 수
- `duration`: float - 전체 실행 시간 (초)
- `tests`: array of TestDetail

**TestDetail** (nested):
- `test_name`: string - 테스트 함수명
- `status`: enum ("passed", "failed", "skipped")
- `duration`: float - 테스트 실행 시간 (초)
- `error_message`: string | null - 에러 메시지 (실패 시)
- `error_traceback`: string | null - 스택 트레이스 (실패 시)

**File Location**: `backend/test-results-{timestamp}.json`

**Validation Rules**:
- execution_id must be valid UUID
- timestamp must be ISO 8601 format
- total_tests = passed + failed + skipped
- duration >= 0
- status must be one of: passed, failed, skipped

### 2. PerformanceMetric (CSV)

**Purpose**: 성능 벤치마크 측정 데이터를 저장

**Fields**:
- `timestamp`: string (ISO 8601) - 측정 시간
- `metric_name`: string - 메트릭 이름 (예: polling_latency_avg)
- `value`: float - 측정 값
- `unit`: string - 단위 (ms, values/sec, MB)
- `percentile`: integer | null - 백분위수 (50, 95, 99 또는 null)

**File Location**: `backend/metrics-{test_name}-{timestamp}.csv`

**Validation Rules**:
- timestamp must be ISO 8601 format
- metric_name must be non-empty
- value >= 0
- unit must be one of: ms, sec, values/sec, MB, GB
- percentile must be null or in [50, 90, 95, 99]

**Example Metrics**:
- `polling_latency_avg`: 평균 폴링 지연 (ms)
- `polling_latency_p99`: 99th percentile 폴링 지연 (ms)
- `oracle_throughput`: Oracle Writer 처리량 (values/sec)
- `oracle_batch_success_rate`: 배치 쓰기 성공률 (%)
- `websocket_update_latency`: WebSocket 업데이트 지연 (ms)
- `memory_usage`: 메모리 사용량 (MB)

### 3. DockerService (docker-compose.yml)

**Purpose**: Docker Compose 서비스 정의

**Fields**:
- `service_name`: string - 서비스 이름 (backend, admin, monitor)
- `image`: string - Docker 이미지 (Dockerfile 경로)
- `build`: object - 빌드 설정 (context, dockerfile)
- `ports`: array of string - 포트 매핑 (host:container)
- `volumes`: array of string - 볼륨 매핑 (host:container)
- `environment`: object - 환경 변수 (key-value)
- `depends_on`: array of string - 의존 서비스
- `healthcheck`: object - 헬스 체크 설정

**File Location**: `docker-compose.yml` (루트)

**Example**:
```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
  ports:
    - "8000:8000"
  volumes:
    - ./backend/config:/app/config
    - ./backend/logs:/app/logs
  environment:
    ORACLE_DSN: ${ORACLE_DSN}
    ORACLE_USER: ${ORACLE_USER}
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### 4. DeploymentEnvironment (.env.production)

**Purpose**: 환경별 설정 변수

**Fields**:
- `ORACLE_DSN`: string - Oracle DB 연결 문자열
- `ORACLE_USER`: string - Oracle 사용자명
- `ORACLE_PASSWORD`: string - Oracle 비밀번호
- `PLC_IP_LIST`: string - PLC IP 주소 목록 (쉼표 구분)
- `ADMIN_PORT`: integer - Admin UI 포트 (기본값 3000)
- `MONITOR_PORT`: integer - Monitor UI 포트 (기본값 3001)
- `BACKEND_PORT`: integer - Backend API 포트 (기본값 8000)
- `LOG_LEVEL`: string - 로그 레벨 (DEBUG, INFO, WARNING, ERROR)

**File Location**: `.env.production` (루트)

**Validation Rules**:
- ORACLE_DSN must be valid Oracle connection string
- Ports must be in range 1024-65535
- LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR

## Relationships

```text
IntegrationTestResult (1) --contains--> (N) TestDetail
PerformanceMetric (N) --measured_during--> (1) IntegrationTestResult

DockerService (3) --uses--> (1) DeploymentEnvironment
```

## File System Structure

```text
backend/
├── test-results-2025-11-04T10-30-00.json
├── metrics-polling-2025-11-04T10-30-00.csv
├── metrics-oracle-2025-11-04T10-30-00.csv
├── metrics-websocket-2025-11-04T10-30-00.csv
└── metrics-memory-2025-11-04T10-30-00.csv

# Root
.env.production
docker-compose.yml
```

## No Database Changes

Feature 8 does NOT modify SQLite or Oracle DB schemas. All test data is stored in files.
