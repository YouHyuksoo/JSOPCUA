# Quick Start: 멀티 스레드 폴링 엔진

**Feature**: 003-polling-engine
**Date**: 2025-10-31

## Prerequisites

- Feature 1 완료 (SQLite DB 설정)
- Feature 2 완료 (PoolManager 사용 가능)
- Python 3.11+ 설치
- 가상환경 활성화: `backend/.venv/Scripts/activate` (Windows) 또는 `source backend/.venv/bin/activate` (Linux)

## Quick Start Guide

### 1. 폴링 그룹 등록 (SQLite DB)

```sql
-- FIXED 모드 폴링 그룹 등록
INSERT INTO polling_groups (group_name, plc_code, mode, interval_ms, is_active)
VALUES ('LINE1_PROCESS1', 'PLC01', 'FIXED', 1000, 1);

-- HANDSHAKE 모드 폴링 그룹 등록
INSERT INTO polling_groups (group_name, plc_code, mode, interval_ms, is_active)
VALUES ('ORDER_START_TRIGGER', 'PLC01', 'HANDSHAKE', NULL, 1);

-- 태그를 폴링 그룹에 할당
UPDATE tags SET polling_group_id = 1 WHERE tag_address IN ('D100', 'D101', 'D102', 'D103', 'D104');
UPDATE tags SET polling_group_id = 2 WHERE tag_address IN ('D200', 'D201', 'D202');
```

### 2. 폴링 엔진 기본 사용

```python
from src.polling.polling_engine import PollingEngine

# 폴링 엔진 초기화
db_path = "backend/config/scada.db"
engine = PollingEngine(db_path)

try:
    # 폴링 그룹 로드
    engine.initialize()
    
    # 모든 활성 폴링 그룹 시작
    engine.start_all()
    
    print("Polling engine started successfully!")
    print(f"Running groups: {len(engine.polling_threads)}")
    
    # 상태 조회
    status = engine.get_status()
    for group_name, group_status in status.items():
        print(f"{group_name}: {group_status['status']} - Last poll: {group_status['last_poll_time']}")
    
    # 메인 루프 (Ctrl+C로 종료)
    import time
    while True:
        time.sleep(10)
        # 큐 크기 확인
        queue_size = engine.get_queue_size()
        print(f"Data queue size: {queue_size}")
        
except KeyboardInterrupt:
    print("\nShutting down polling engine...")
finally:
    engine.shutdown()
    print("Polling engine stopped.")
```

### 3. FIXED 모드 폴링 예제

```python
from src.polling.polling_engine import PollingEngine
import time

engine = PollingEngine("backend/config/scada.db")
engine.initialize()

# 특정 FIXED 모드 그룹만 시작
engine.start_group("LINE1_PROCESS1")

# 10초 동안 실행
time.sleep(10)

# 상태 확인
status = engine.get_status()
line1_status = status["LINE1_PROCESS1"]
print(f"Poll count: {line1_status['poll_count']}")  # 약 10회 (1초 주기)
print(f"Success rate: {line1_status['success_count'] / line1_status['poll_count'] * 100:.1f}%")

engine.stop_group("LINE1_PROCESS1")
engine.shutdown()
```

### 4. HANDSHAKE 모드 트리거 예제

```python
from src.polling.polling_engine import PollingEngine

engine = PollingEngine("backend/config/scada.db")
engine.initialize()

# HANDSHAKE 모드 그룹 시작 (대기 상태)
engine.start_group("ORDER_START_TRIGGER")

# 수동으로 폴링 트리거 (예: 주문 시작 시점)
print("Triggering ORDER_START_TRIGGER...")
engine.trigger_handshake("ORDER_START_TRIGGER")

# 폴링 완료까지 대기
import time
time.sleep(2)

# 큐에서 데이터 확인
if not engine.data_queue.queue.empty():
    data = engine.data_queue.queue.get()
    print(f"Polled data: {data['tag_values']}")

engine.shutdown()
```

### 5. 데이터 큐 소비 예제 (Feature 4 미리보기)

```python
from src.polling.polling_engine import PollingEngine
import threading
import time

def data_consumer(data_queue):
    """데이터 큐 소비자 (Feature 4에서 DB Writer로 구현 예정)"""
    while True:
        try:
            # 큐에서 데이터 가져오기 (block=True, 데이터 있을 때까지 대기)
            polling_data = data_queue.get(timeout=1)
            
            print(f"[{polling_data['timestamp']}] {polling_data['group_name']}: {len(polling_data['tag_values'])} tags")
            
            # TODO: Feature 4에서 Oracle DB에 저장
            # db_writer.write(polling_data)
            
        except Exception as e:
            # 타임아웃 또는 큐 빔
            pass

# 폴링 엔진 시작
engine = PollingEngine("backend/config/scada.db")
engine.initialize()
engine.start_all()

# 소비자 스레드 시작
consumer_thread = threading.Thread(target=data_consumer, args=(engine.data_queue,), daemon=True)
consumer_thread.start()

# 60초 실행
try:
    time.sleep(60)
finally:
    engine.shutdown()
```

### 6. 다중 폴링 그룹 동시 실행

```python
from src.polling.polling_engine import PollingEngine
import time

engine = PollingEngine("backend/config/scada.db")
engine.initialize()

# 모든 그룹 시작
engine.start_all()

# 30초마다 상태 출력
for i in range(10):  # 5분 실행
    time.sleep(30)
    
    status = engine.get_status()
    print(f"\n=== Status Report ({i+1}/10) ===")
    
    for group_name, group_status in status.items():
        print(f"{group_name}:")
        print(f"  Status: {group_status['status']}")
        print(f"  Poll Count: {group_status['poll_count']}")
        print(f"  Success Rate: {group_status['success_count'] / group_status['poll_count'] * 100:.1f}%")
        print(f"  Avg Poll Time: {group_status['avg_poll_time_ms']:.2f}ms")
    
    print(f"Queue Size: {engine.get_queue_size()}")

engine.shutdown()
```

## Common Scenarios

### Scenario 1: 라인별 독립 폴링

```python
# LINE1, LINE2, LINE3 각각 다른 주기로 폴링
# DB에 미리 등록:
# - LINE1_PROCESS1: 1초 주기 (실시간 모니터링)
# - LINE2_PROCESS1: 5초 주기 (정상 작동)
# - LINE3_PROCESS1: 10초 주기 (백업 라인)

engine = PollingEngine("backend/config/scada.db")
engine.initialize()
engine.start_all()

# 각 라인이 독립적으로 폴링, 서로 영향 없음
```

### Scenario 2: 이벤트 기반 데이터 수집

```python
# 주문 시작/종료 시점에만 데이터 수집
# DB에 HANDSHAKE 모드 그룹 등록:
# - ORDER_START_CAPTURE
# - ORDER_END_CAPTURE

engine = PollingEngine("backend/config/scada.db")
engine.initialize()
engine.start_all()  # HANDSHAKE 그룹은 대기 상태

# 주문 시작 시
engine.trigger_handshake("ORDER_START_CAPTURE")

# ... 작업 진행 ...

# 주문 종료 시
engine.trigger_handshake("ORDER_END_CAPTURE")
```

### Scenario 3: 동적 그룹 제어

```python
engine = PollingEngine("backend/config/scada.db")
engine.initialize()

# 일부만 시작
engine.start_group("LINE1_PROCESS1")
engine.start_group("LINE2_PROCESS1")

# 런타임에 추가 시작
time.sleep(60)
engine.start_group("LINE3_PROCESS1")

# 특정 그룹 중지 (유지보수)
engine.stop_group("LINE2_PROCESS1")

# 다시 시작
time.sleep(300)
engine.start_group("LINE2_PROCESS1")
```

## Testing

### 테스트 스크립트 실행

```bash
# 폴링 엔진 기본 테스트
python backend/src/scripts/test_polling_engine.py

# 단위 테스트
pytest backend/tests/unit/test_polling_engine.py
pytest backend/tests/unit/test_polling_thread.py
pytest backend/tests/unit/test_data_queue.py

# 통합 테스트
pytest backend/tests/integration/test_polling_integration.py
```

## Monitoring

### 로그 확인

```bash
# 폴링 엔진 로그
tail -f logs/polling.log

# 주요 로그 메시지:
# - "Polling group {name} started"
# - "Polling cycle completed: {count} tags in {time}ms"
# - "Polling error: {error_message}"
# - "Queue full warning: {queue_size}/{maxsize}"
```

### 상태 확인 API (Feature 5에서 REST API로 제공 예정)

```python
# 현재는 직접 호출
status = engine.get_status()

# 예상 출력:
{
    "LINE1_PROCESS1": {
        "status": "running",
        "poll_count": 3600,
        "success_count": 3598,
        "error_count": 2,
        "last_poll_time": "2025-10-31T12:30:45.123456",
        "avg_poll_time_ms": 45.2
    },
    ...
}
```

## Troubleshooting

### 문제 1: 폴링 주기가 정확하지 않음

**원인**: 폴링 소요 시간이 주기보다 김
**해결**: 로그에서 "Poll time exceeds interval" 경고 확인, 태그 수 줄이거나 주기 늘리기

### 문제 2: 큐가 가득 참

**원인**: Feature 4 DB Writer가 소비 속도가 느림
**해결**: 
- 큐 최대 크기 증가 (DataQueue(maxsize=20000))
- DB Writer 성능 튜닝
- 폴링 주기 조정

### 문제 3: 스레드가 종료되지 않음

**원인**: stop_event 신호가 전달되지 않음
**해결**: engine.shutdown() 호출, 3초 타임아웃 대기

### 문제 4: HANDSHAKE 트리거가 작동하지 않음

**원인**: 그룹이 시작되지 않음
**해결**: start_group() 먼저 호출 후 trigger_handshake() 호출

## Next Steps

- **Feature 4**: DB Writer로 큐 데이터를 Oracle DB에 저장
- **Feature 5**: REST API로 폴링 제어 (start/stop/trigger/status)
- **Feature 6**: 관리 웹에서 폴링 그룹 관리 UI
- **Feature 7**: 모니터링 웹에서 실시간 폴링 상태 확인
