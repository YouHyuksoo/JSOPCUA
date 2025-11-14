# Polling Engine Integration Guide

## 개요

실시간 PLC 폴링 시스템이 REST API와 완전히 통합되었어요. 폴링 그룹을 웹 UI에서 시작/중지할 수 있고, 읽어온 데이터는 자동으로 Oracle DB에 저장되며, 모니터링 화면으로도 실시간 전송돼요.

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│              Frontend (Next.js Admin UI)                     │
│  http://localhost:3000/polling-groups                        │
│  - 폴링 그룹 생성/편집                                          │
│  - 시작/중지/재시작 버튼                                        │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          FastAPI Backend (main.py)                           │
│  POST /api/polling-groups/{id}/start                         │
│  POST /api/polling-groups/{id}/stop                          │
│  POST /api/polling-groups/{id}/restart                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│       PollingGroupManager (Singleton)                        │
│  - 폴링 엔진 생명주기 관리                                      │
│  - PoolManager 연동 (PLC 연결 풀)                             │
│  - Oracle Writer Thread 관리                                 │
│  - Monitor Broadcaster Thread 관리                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            PollingEngine (polling_engine.py)                 │
│  - 폴링 그룹별 스레드 관리                                      │
│  - FixedPollingThread / HandshakePollingThread              │
│  - DataQueue에 폴링 결과 저장                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   DataQueue                                  │
│  - 스레드 안전 큐 (max 10,000 items)                          │
│  - 폴링 결과를 임시 저장                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──────────────┬──────────────────────────────┐
                 ▼              ▼                              ▼
   ┌──────────────────┐  ┌──────────────┐    ┌─────────────────────────┐
   │ Oracle Writer    │  │ SQLite Writer│    │ Monitor Broadcaster     │
   │ Thread           │  │ (last_value) │    │ (WebSocket)             │
   │                  │  │              │    │                         │
   │ - Batch insert   │  │ - Update tags│    │ - Real-time broadcast   │
   │ - 10 records or  │  │   last_value │    │ - Multiple clients      │
   │   5 sec timeout  │  │              │    │                         │
   └────────┬─────────┘  └──────────────┘    └─────────────────────────┘
            │
            ▼
   ┌──────────────────┐
   │   Oracle DB      │
   │ ICOM_PLC_TAG_LOG │
   └──────────────────┘
```

## 주요 컴포넌트

### 1. PollingGroupManager

**위치**: `backend/src/polling/polling_group_manager.py`

**역할**:
- 폴링 엔진의 싱글톤 관리자
- REST API와 폴링 엔진을 연결
- PoolManager, PollingEngine, Oracle Writer, Monitor Broadcaster 초기화
- 폴링 그룹의 start/stop/restart 제어

**주요 메서드**:
```python
# 싱글톤 인스턴스 생성
manager = PollingGroupManager(db_path, pool_manager)
manager.initialize(enable_oracle=True)

# 폴링 그룹 제어
result = manager.start_group(group_id)
result = manager.stop_group(group_id, timeout=5.0)
result = manager.restart_group(group_id)

# 상태 조회
status = manager.get_group_status(group_id)
all_status = manager.get_all_status()

# 종료
manager.shutdown()
```

### 2. OracleWriterThread

**위치**: `backend/src/polling/oracle_writer_thread.py`

**역할**:
- DataQueue에서 폴링 결과를 소비
- Oracle DB에 배치 insert (ICOM_PLC_TAG_LOG 테이블)
- SQLite tags 테이블의 last_value 및 last_updated_at 업데이트

**설정**:
- `batch_size`: 10 (배치당 레코드 수)
- `batch_timeout`: 5.0초 (최대 대기 시간)
- `enable_oracle`: True/False (Oracle 쓰기 활성화)

**데이터 플로우**:
1. DataQueue에서 PollingData 읽기
2. Batch에 추가 (최대 10개 또는 5초 타임아웃)
3. Oracle DB INSERT:
   ```sql
   INSERT INTO ICOM_PLC_TAG_LOG (
       LOG_TIMESTAMP, PLC_CODE, TAG_ADDRESS, TAG_VALUE,
       MACHINE_CODE, POLL_TIME_MS, CREATED_AT
   ) VALUES (...)
   ```
4. SQLite tags 업데이트:
   ```sql
   UPDATE tags
   SET last_value = ?, last_updated_at = ?
   WHERE tag_address = ? AND plc_id = ...
   ```

### 3. MonitorBroadcaster

**위치**: `backend/src/polling/monitor_broadcaster.py`

**역할**:
- DataQueue에서 폴링 결과를 소비
- WebSocket 클라이언트에 실시간 브로드캐스트
- 모니터링 화면의 실시간 데이터 갱신

**메시지 포맷** (JSON):
```json
{
  "type": "polling_data",
  "timestamp": "2025-11-14T10:30:00.123456",
  "group_id": 1,
  "group_name": "Group1",
  "plc_code": "PLC01",
  "mode": "FIXED",
  "poll_time_ms": 123.45,
  "tag_values": {
    "D100": 1234,
    "D101": 5678,
    "M100": true
  },
  "error_tags": {}
}
```

## API 엔드포인트

### POST /api/polling-groups/{id}/start

폴링 그룹 시작

**Request**:
```bash
curl -X POST http://localhost:8000/api/polling-groups/1/start
```

**Response**:
```json
{
  "success": true,
  "message": "Polling group Group1 started successfully",
  "group_id": 1,
  "group_name": "Group1",
  "new_status": "running"
}
```

### POST /api/polling-groups/{id}/stop

폴링 그룹 중지

**Request**:
```bash
curl -X POST http://localhost:8000/api/polling-groups/1/stop
```

**Response**:
```json
{
  "success": true,
  "message": "Polling group Group1 stopped successfully",
  "group_id": 1,
  "group_name": "Group1",
  "new_status": "stopped"
}
```

### POST /api/polling-groups/{id}/restart

폴링 그룹 재시작

**Request**:
```bash
curl -X POST http://localhost:8000/api/polling-groups/1/restart
```

**Response**:
```json
{
  "success": true,
  "message": "Polling group Group1 restarted successfully",
  "group_id": 1,
  "group_name": "Group1",
  "new_status": "running"
}
```

## 데이터베이스 스키마

### SQLite (scada.db)

#### polling_groups 테이블
```sql
CREATE TABLE polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    polling_mode TEXT NOT NULL,           -- 'FIXED' or 'HANDSHAKE'
    polling_interval_ms INTEGER NOT NULL,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    plc_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id)
);
```

#### tags 테이블
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,
    polling_group_id INTEGER,
    tag_address TEXT NOT NULL,
    tag_name TEXT NOT NULL,
    tag_type TEXT NOT NULL,              -- 'BIT', 'INT', 'DINT', etc.
    unit TEXT,
    scale REAL DEFAULT 1.0,
    offset REAL DEFAULT 0.0,
    min_value REAL,
    max_value REAL,
    machine_code TEXT,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    last_value TEXT,                      -- 마지막 읽은 값
    last_updated_at TIMESTAMP,            -- 마지막 업데이트 시간
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id),
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id)
);
```

### Oracle DB

#### XSCADA_OPERATION 테이블 (동작 데이터)
```sql
CREATE TABLE XSCADA_OPERATION (
    TIME TIMESTAMP(6),      -- 타임스탬프
    NAME VARCHAR2(200),     -- 태그명
    VALUE VARCHAR2(100)     -- 태그값
);
```

**NAME 필드 포맷**:
```
{PLC_CODE}.Operation.{MACHINE_CODE}.{TAG_ADDRESS}
```

**예시**:
- `PLC01.Operation.KRCWO12EANN107.W0709`
- `PLC01.Operation.KRCWO12EANN107.W07C0`

**저장 조건**:
- `tags.tag_category` ≠ 'Alarm' 인 모든 태그
- 실시간으로 모든 폴링 데이터 저장

#### XSCADA_DATATAG_LOG 테이블 (알람 데이터)
```sql
CREATE TABLE XSCADA_DATATAG_LOG (
    ID NUMBER(19,0),                    -- 시퀀스 ID
    CTIME TIMESTAMP(6),                 -- 생성 시간
    OTIME TIMESTAMP(6),                 -- 발생 시간
    DATATAG_NAME NVARCHAR2(255),        -- 태그명
    DATATAG_TYPE CHAR(1),               -- 타입 (D=Digital)
    VALUE_STR NVARCHAR2(255),           -- 값(문자열)
    VALUE_NUM NUMBER,                   -- 값(숫자)
    VALUE_RAW NVARCHAR2(2000)           -- 원시값
);
```

**DATATAG_NAME 필드 포맷**:
```
{PLC_CODE}.Alarm.{MACHINE_CODE}.{TAG_ADDRESS}
```

**예시**:
- `PLC03.Alarm.KRCWO12EWEM631.M5324`
- `PLC03.Alarm.KRCWO12EWEM631.M5323`

**저장 조건**:
- `tags.tag_category = 'Alarm'` 인 태그만
- 값이 변경될 때마다 저장 (이벤트 기반)

**참고**:
- `PLC_CODE`: SQLite의 `plc_connections.plc_code` (예: PLC01, PLC02)
- `MACHINE_CODE`: SQLite의 `tags.machine_code` (예: KRCWO12EANN107)
- `TAG_ADDRESS`: SQLite의 `tags.tag_address` (예: W0709, M5324)
- machine_code가 없으면 `UNKNOWN` 사용
- `VALUE_STR`: 모든 타입을 문자열로 변환
- `VALUE_NUM`: 숫자 변환 가능하면 변환, 불가능하면 NULL
- `VALUE_RAW`: 원시 값 그대로 저장

## 설정

### 환경 변수 (.env)

```bash
# Oracle DB Connection
ORACLE_HOST=your-oracle-host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=ORCL
ORACLE_USERNAME=your-username
ORACLE_PASSWORD=your-password

# SQLite DB Path (상대 경로는 backend 기준)
DB_PATH=data/scada.db

# Polling Engine Settings
MAX_POLLING_GROUPS=10
DEFAULT_BATCH_SIZE=10
DEFAULT_BATCH_TIMEOUT=5.0

# Enable/Disable Oracle Writing
ENABLE_ORACLE=true
```

### 시작 시 초기화

**backend/src/api/main.py**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool_manager, polling_engine, polling_group_manager

    # Initialize PoolManager
    pool_manager = PoolManager(db_path)
    pool_manager.initialize()

    # Initialize PollingGroupManager (singleton)
    polling_group_manager = PollingGroupManager(db_path, pool_manager)
    polling_group_manager.initialize(enable_oracle=True)

    yield

    # Shutdown
    if polling_group_manager:
        polling_group_manager.shutdown()
    if pool_manager:
        pool_manager.shutdown()
```

## 사용 예시

### 1. 폴링 그룹 생성 (Frontend)

1. http://localhost:3000/polling-groups 접속
2. "새 폴링 그룹" 버튼 클릭
3. 그룹 정보 입력:
   - 이름: "Line1_Process1"
   - PLC: PLC01
   - 폴링 주기: 1000ms
   - 태그 선택: D100, D101, M100 등
4. "저장" 클릭

### 2. 폴링 시작

1. 폴링 그룹 리스트에서 "시작" 버튼 클릭
2. 상태가 "stopped" → "running"으로 변경
3. 태그 데이터가 실시간으로 읽히기 시작

**백그라운드 동작**:
- PollingThread가 1초마다 PLC에서 D100, D101, M100 읽기
- 읽은 데이터를 DataQueue에 저장
- OracleWriterThread가 DataQueue에서 꺼내서 Oracle DB에 저장
- SQLite tags 테이블의 last_value 업데이트
- MonitorBroadcaster가 WebSocket으로 모니터링 화면에 전송

### 3. 데이터 확인

**Oracle DB**:
```sql
-- 최근 1시간 동작 데이터 조회 (XSCADA_OPERATION)
SELECT TIME, NAME, VALUE
FROM XSCADA_OPERATION
WHERE TIME >= SYSTIMESTAMP - INTERVAL '1' HOUR
ORDER BY TIME DESC;

-- 특정 PLC의 동작 데이터 조회
SELECT TIME, NAME, VALUE
FROM XSCADA_OPERATION
WHERE NAME LIKE 'PLC01.Operation.%'
  AND TIME >= SYSTIMESTAMP - INTERVAL '1' HOUR
ORDER BY TIME DESC;

-- 특정 설비(MACHINE_CODE)의 동작 데이터 조회
SELECT TIME, NAME, VALUE
FROM XSCADA_OPERATION
WHERE NAME LIKE 'PLC01.Operation.KRCWO12EANN107.%'
  AND TIME >= SYSTIMESTAMP - INTERVAL '1' HOUR
ORDER BY TIME DESC;

-- 최근 1시간 알람 데이터 조회 (XSCADA_DATATAG_LOG)
SELECT ID, CTIME, OTIME, DATATAG_NAME, VALUE_STR, VALUE_NUM
FROM XSCADA_DATATAG_LOG
WHERE CTIME >= SYSTIMESTAMP - INTERVAL '1' HOUR
ORDER BY CTIME DESC;

-- 특정 설비의 알람 이력 조회
SELECT ID, CTIME, OTIME, DATATAG_NAME, VALUE_STR
FROM XSCADA_DATATAG_LOG
WHERE DATATAG_NAME LIKE 'PLC03.Alarm.KRCWO12EWEM631.%'
  AND CTIME >= SYSTIMESTAMP - INTERVAL '24' HOUR
ORDER BY CTIME DESC;

-- 알람 발생 횟수 집계
SELECT DATATAG_NAME, COUNT(*) as ALARM_COUNT
FROM XSCADA_DATATAG_LOG
WHERE CTIME >= SYSTIMESTAMP - INTERVAL '24' HOUR
GROUP BY DATATAG_NAME
ORDER BY ALARM_COUNT DESC;
```

**SQLite**:
```sql
SELECT tag_address, tag_name, last_value, last_updated_at
FROM tags
WHERE polling_group_id = 1
ORDER BY tag_address;
```

### 4. 폴링 중지

1. 폴링 그룹 리스트에서 "중지" 버튼 클릭
2. 상태가 "running" → "stopped"으로 변경
3. 폴링 스레드가 안전하게 종료

## 에러 처리

### 1. PLC 연결 실패

**증상**: 폴링 시작 시 "Connection refused" 에러

**해결**:
1. PLC IP 주소 및 포트 확인
2. 네트워크 연결 확인
3. PLC 전원 및 통신 모듈 상태 확인

**로그**:
```
[ERROR] Poll failed: group=Group1, error=Connection refused, time=5000ms
```

### 2. Oracle 연결 실패

**증상**: 백엔드 시작 시 "ORA-12154: TNS:could not resolve the connect identifier" 에러

**해결**:
1. Oracle 연결 정보 확인 (.env 파일)
2. Oracle 서버 접근 가능 확인
3. `enable_oracle=False`로 설정하여 Oracle 없이 테스트 가능

**로그**:
```
[ERROR] Failed to connect to Oracle: ORA-12154
[WARNING] Oracle writing disabled for this session
```

### 3. DataQueue 가득 참

**증상**: "DataQueue is full" 경고

**원인**: Oracle Writer가 데이터를 소비하는 속도보다 폴링이 더 빠름

**해결**:
1. Oracle Writer batch_size 증가 (10 → 50)
2. batch_timeout 감소 (5.0 → 2.0)
3. 폴링 주기 조정
4. DataQueue 크기 증가 (10000 → 50000)

## 성능 튜닝

### 1. Batch 설정 최적화

**시나리오**: 초당 100개의 태그 값 읽기

**권장 설정**:
```python
OracleWriterThread(
    batch_size=50,      # 배치 크기 증가
    batch_timeout=2.0   # 타임아웃 감소
)
```

**효과**:
- Oracle INSERT 빈도 감소
- 트랜잭션 오버헤드 감소
- 처리량 증가

### 2. Connection Pool 크기 조정

**시나리오**: 10개의 폴링 그룹 동시 실행

**권장 설정**:
```python
PoolManager(db_path, pool_size=10)  # 기본 5 → 10
```

**효과**:
- PLC 연결 경합 감소
- 폴링 지연 감소

### 3. 폴링 주기 최적화

**권장 사항**:
- 빠른 변화: 100-500ms (센서, 알람)
- 중간 속도: 1000-2000ms (공정 데이터)
- 느린 변화: 5000-10000ms (온도, 압력)

## 모니터링

### 시스템 상태 확인

```python
# PollingGroupManager 상태
manager = PollingGroupManager.get_instance()
all_status = manager.get_all_status()

# Oracle Writer 상태
if manager.oracle_writer:
    writer_stats = manager.oracle_writer.get_stats()
    print(f"Records written: {writer_stats['records_written']}")
    print(f"Records failed: {writer_stats['records_failed']}")
    print(f"Queue size: {writer_stats['queue_size']}")

# Monitor Broadcaster 상태
if manager.monitor_broadcaster:
    broadcaster_stats = manager.monitor_broadcaster.get_stats()
    print(f"Clients connected: {broadcaster_stats['clients_connected']}")
    print(f"Messages broadcast: {broadcaster_stats['messages_broadcast']}")
```

## 트러블슈팅

### Q: 폴링 시작 버튼을 눌러도 반응이 없어요

**A**:
1. 브라우저 개발자 도구 → 네트워크 탭 확인
2. API 응답 확인 (200 OK 또는 에러 메시지)
3. 백엔드 로그 확인:
   ```bash
   # Windows
   d:\Project\JSOPCUA\backend\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
   ```

### Q: Oracle DB에 데이터가 안 들어가요

**A**:
1. Oracle 연결 확인:
   ```python
   from src.oracle_writer.oracle_helper import OracleHelper
   with OracleHelper() as oracle:
       machines = oracle.fetch_machines()
       print(f"Connected! Found {len(machines)} machines")
   ```
2. OracleWriterThread 상태 확인
3. 로그에서 에러 메시지 확인

### Q: 모니터링 화면에 데이터가 안 나와요

**A**:
1. WebSocket 연결 확인 (개발자 도구 → 네트워크 → WS)
2. MonitorBroadcaster 실행 확인
3. 폴링 그룹이 실제로 running 상태인지 확인

## 다음 단계

### 추가 기능 개발

1. **알람 기능**: 태그 값이 임계값을 초과하면 알람 발생
2. **히스토리 조회 API**: Oracle DB에서 과거 데이터 조회
3. **대시보드**: 실시간 그래프 및 통계
4. **스케줄링**: 특정 시간에 자동 시작/중지

### 성능 개선

1. **멀티 프로세스**: PollingEngine을 별도 프로세스로 분리
2. **Redis 캐싱**: 최신 값을 Redis에 캐싱하여 빠른 조회
3. **TimescaleDB**: 시계열 데이터 최적화

## 참고 문서

- [Feature 1: Database Schema](./DATABASE_INITIALIZATION.md)
- [Feature 2: PLC Connection Pool](../backend/src/plc/README.md)
- [Feature 3: Polling Engine](../backend/src/polling/README.md)
- [Oracle DB 연동](./ENV_CONFIGURATION.md)
