# Data Model: 멀티 스레드 폴링 엔진

**Date**: 2025-10-31
**Feature**: 003-polling-engine

## Entities

### 1. Polling Group (폴링 그룹)

폴링 실행 단위. SQLite polling_groups 테이블에서 로드.

**Attributes**:
- `group_id` (int): 폴링 그룹 ID (PK from DB)
- `group_name` (str): 폴링 그룹 이름 (예: "LINE1_PROCESS1")
- `plc_code` (str): 연결할 PLC 코드 (Feature 2 PoolManager 사용)
- `mode` (str): 폴링 모드 ("FIXED" 또는 "HANDSHAKE")
- `interval_ms` (int): 폴링 주기 (밀리초, FIXED 모드에서만 사용)
- `is_active` (bool): 활성 상태
- `tag_addresses` (List[str]): 폴링할 태그 주소 목록 (tags 테이블에서 조회)

**Validation**:
- mode는 "FIXED" 또는 "HANDSHAKE"만 허용
- FIXED 모드일 때 interval_ms >= 100 (최소 100ms)
- tag_addresses는 최소 1개 이상

**Relationships**:
- 1 Polling Group → N Tags (tags 테이블)
- 1 Polling Group → 1 PLC (plc_connections 테이블)

### 2. Polling Thread (폴링 스레드)

폴링 그룹을 실행하는 스레드 인스턴스.

**Attributes**:
- `thread` (threading.Thread): 스레드 객체
- `group_id` (int): 연결된 폴링 그룹 ID
- `status` (str): 스레드 상태 ("running", "stopped", "error")
- `stop_event` (threading.Event): 스레드 종료 신호
- `last_poll_time` (datetime): 마지막 폴링 시간
- `poll_count` (int): 총 폴링 횟수
- `success_count` (int): 성공한 폴링 횟수
- `error_count` (int): 실패한 폴링 횟수
- `avg_poll_time_ms` (float): 평균 폴링 소요 시간 (ms)

**State Transitions**:
```
[stopped] --start()--> [running] --stop()--> [stopped]
[running] --error--> [error] --restart()--> [running]
```

### 3. Polling Data (폴링 데이터)

폴링 결과 데이터. 큐에 저장되어 Feature 4로 전달.

**Attributes**:
- `timestamp` (datetime): 폴링 시각
- `group_id` (int): 폴링 그룹 ID
- `group_name` (str): 폴링 그룹 이름
- `plc_code` (str): PLC 코드
- `mode` (str): 폴링 모드
- `tag_values` (Dict[str, Any]): 태그 주소 → 값 매핑
- `poll_time_ms` (float): 폴링 소요 시간 (ms)
- `error_tags` (Dict[str, str]): 실패한 태그 → 에러 메시지 (있으면)

**Format Example**:
```python
{
    "timestamp": datetime(2025, 10, 31, 12, 30, 45, 123456),
    "group_id": 1,
    "group_name": "LINE1_PROCESS1",
    "plc_code": "PLC01",
    "mode": "FIXED",
    "tag_values": {
        "D100": 1234,
        "D101": 5678,
        "D102": 9012
    },
    "poll_time_ms": 45.2,
    "error_tags": {}
}
```

### 4. Data Queue (데이터 큐)

스레드 안전 큐. 모든 폴링 스레드가 공유.

**Attributes**:
- `queue` (queue.Queue): Python 표준 큐
- `maxsize` (int): 최대 크기 (기본 10000)
- `current_size` (int): 현재 큐 크기 (queue.qsize())

**Operations**:
- `put(data: PollingData, block=True, timeout=None)`: 데이터 추가
- `get(block=True, timeout=None) -> PollingData`: 데이터 가져오기
- `is_full() -> bool`: 큐가 가득 찼는지 확인
- `clear()`: 큐 비우기 (shutdown 시)

### 5. Polling Engine (폴링 엔진)

전체 폴링 그룹 관리자.

**Attributes**:
- `db_path` (str): SQLite 데이터베이스 경로
- `pool_manager` (PoolManager): Feature 2의 PoolManager 인스턴스
- `data_queue` (DataQueue): 공유 데이터 큐
- `polling_threads` (Dict[int, PollingThread]): group_id → PollingThread 매핑
- `handshake_triggers` (Dict[str, Event]): group_name → Event 매핑 (HANDSHAKE 모드용)

**Operations**:
- `initialize()`: DB에서 폴링 그룹 로드 및 스레드 생성
- `start_all()`: 모든 활성 폴링 그룹 시작
- `stop_all()`: 모든 폴링 그룹 중지
- `start_group(group_name: str)`: 특정 그룹 시작
- `stop_group(group_name: str)`: 특정 그룹 중지
- `trigger_handshake(group_name: str)`: HANDSHAKE 모드 트리거
- `get_status() -> Dict`: 모든 그룹 상태 조회
- `get_queue_size() -> int`: 데이터 큐 크기 조회
- `shutdown()`: 전체 종료 (스레드 중지 + 리소스 정리)

## Database Schema (Feature 1에서 생성됨)

### polling_groups 테이블

```sql
CREATE TABLE polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL UNIQUE,
    plc_code TEXT NOT NULL,
    mode TEXT NOT NULL CHECK(mode IN ('FIXED', 'HANDSHAKE')),
    interval_ms INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_code) REFERENCES plc_connections(plc_code)
);
```

### tags 테이블 (Feature 1에서 생성, polling_group_id 컬럼 추가)

```sql
-- Feature 1 기존 스키마에 polling_group_id 추가 필요
ALTER TABLE tags ADD COLUMN polling_group_id INTEGER;
ALTER TABLE tags ADD FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id);
```

## Relationships Diagram

```
┌─────────────────┐
│ PollingEngine   │
│  ├─ db_path     │
│  ├─ pool_mgr    │──────> Feature 2 PoolManager
│  ├─ data_queue  │──────> DataQueue (shared)
│  └─ threads     │
└────────┬────────┘
         │ 1:N
         ▼
┌──────────────────┐       ┌──────────────────┐
│ PollingThread    │ 1:1   │ PollingGroup     │
│  ├─ thread       │<─────>│  ├─ group_id     │
│  ├─ group_id     │       │  ├─ group_name   │
│  ├─ status       │       │  ├─ mode         │
│  ├─ stop_event   │       │  ├─ interval_ms  │
│  └─ stats        │       │  └─ tag_addresses│
└──────────────────┘       └───────┬──────────┘
         │                         │ N:1
         │ produces                ▼
         │                  ┌─────────────────┐
         ▼                  │ PLC (Feature 2) │
┌──────────────────┐        └─────────────────┘
│ PollingData      │
│  ├─ timestamp    │
│  ├─ group_id     │
│  ├─ tag_values   │
│  └─ poll_time_ms │
└──────────┬───────┘
           │
           ▼
    ┌─────────────┐
    │ DataQueue   │──────> Feature 4 (DB Writer)
    └─────────────┘
```

## Concurrency Model

- **스레드 안전성**: queue.Queue는 내부적으로 Lock 사용하여 스레드 안전
- **스레드 격리**: 각 PollingThread는 독립적으로 실행, 서로 영향 없음
- **공유 리소스**: DataQueue, PoolManager (PoolManager는 내부적으로 스레드 안전)
- **종료 신호**: threading.Event로 안전한 스레드 종료

## Data Flow

```
1. PollingEngine.initialize()
   └─> Load polling_groups from DB
       └─> Create PollingThread for each group

2. PollingThread.run() (FIXED mode)
   └─> while not stop_event.is_set():
       ├─> pool_manager.read_batch(tag_addresses)
       ├─> Create PollingData
       ├─> data_queue.put(polling_data)
       ├─> time.sleep(interval - poll_time)
       └─> Update stats

3. PollingThread.run() (HANDSHAKE mode)
   └─> while not stop_event.is_set():
       ├─> wait for trigger_event
       ├─> pool_manager.read_batch(tag_addresses)
       ├─> Create PollingData
       ├─> data_queue.put(polling_data)
       └─> Update stats

4. Feature 4 (DB Writer)
   └─> while True:
       ├─> polling_data = data_queue.get()
       └─> Write to Oracle DB
```
