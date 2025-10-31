# Quick Start: MC 3E ASCII 프로토콜 통신 및 Connection Pool

**Feature**: MC 3E ASCII 프로토콜 통신 및 Connection Pool
**Date**: 2025-10-31

## 5-Minute Quick Start

### 전제조건

- Feature 1 완료 (SQLite DB 및 plc_connections 테이블 존재)
- Python 3.11+ 설치
- PLC가 네트워크에 연결되어 있고 MC 3E ASCII 프로토콜 활성화됨

### 1. 의존성 설치

```bash
cd backend
pip install pymcprotocol pytest
```

### 2. PLC 연결 정보 등록 (Feature 1 완료 시 생략 가능)

```bash
# SQLite에 PLC 연결 정보 추가
sqlite3 config/scada.db

INSERT INTO plc_connections (process_id, plc_code, plc_name, ip_address, port, protocol, is_active)
VALUES (1, 'PLC01', 'Test PLC', '192.168.1.10', 5010, 'MC_3E_ASCII', 1);

-- 확인
SELECT * FROM plc_connections;
.quit
```

### 3. 단일 태그 읽기 테스트

```python
# backend/src/scripts/test_plc_connection.py
from src.plc.mc3e_client import MC3EClient
from src.database.sqlite_manager import SQLiteManager

# DB에서 PLC 정보 읽기
db = SQLiteManager('config/scada.db')
plc_info = db.execute_query("SELECT * FROM plc_connections WHERE plc_code = ?", ("PLC01",))[0]

# PLC 연결 및 읽기
client = MC3EClient(plc_info['ip_address'], plc_info['port'])
client.connect()

# 단일 태그 읽기
value = client.read_single("D100")
print(f"D100 value: {value}")

client.disconnect()
```

실행:
```bash
python src/scripts/test_plc_connection.py
```

예상 출력:
```
2025-10-31 12:00:00 - INFO - PLC01 connected: 192.168.1.10:5010
D100 value: 1234
2025-10-31 12:00:01 - INFO - PLC01 disconnected
```

### 4. Connection Pool 사용

```python
from src.plc.pool_manager import PoolManager

# Pool Manager 초기화 (DB에서 PLC 목록 자동 로드)
pool_mgr = PoolManager(db_path='config/scada.db')
pool_mgr.initialize()

# PLC01에서 태그 읽기 (Connection Pool 사용)
value = pool_mgr.read_single('PLC01', 'D100')
print(f"D100: {value}")

# 배치 읽기
values = pool_mgr.read_batch('PLC01', ['D100', 'D101', 'D102'])
print(f"Batch read: {values}")

# Pool 종료
pool_mgr.shutdown()
```

예상 출력:
```
2025-10-31 12:00:00 - INFO - PoolManager initialized: 2 PLCs
2025-10-31 12:00:01 - INFO - PLC01 pool created: max_size=5
D100: 1234
Batch read: {'D100': 1234, 'D101': 5678, 'D102': 9012}
2025-10-31 12:00:02 - INFO - PoolManager shutdown complete
```

---

## Integration Scenarios

### Scenario 1: 시스템 시작 시 PLC 연결

```python
# 애플리케이션 시작 시 실행
from src.plc.pool_manager import PoolManager

pool_mgr = PoolManager(db_path='config/scada.db')
pool_mgr.initialize()  # DB에서 모든 active PLC 로드 및 Pool 생성

print(f"Initialized {pool_mgr.get_plc_count()} PLCs")
# 출력: Initialized 2 PLCs
```

### Scenario 2: 주기적 태그 읽기 (폴링 엔진 준비)

```python
import time

# 1초마다 D100 값 읽기
while True:
    try:
        value = pool_mgr.read_single('PLC01', 'D100')
        print(f"{time.strftime('%H:%M:%S')} - D100: {value}")
    except Exception as e:
        print(f"Error reading tag: {e}")
    time.sleep(1)
```

### Scenario 3: 여러 PLC에서 동시 읽기

```python
import threading

def read_from_plc(plc_code, tag_address):
    value = pool_mgr.read_single(plc_code, tag_address)
    print(f"{plc_code}/{tag_address}: {value}")

# 2개 PLC에서 동시 읽기
threads = [
    threading.Thread(target=read_from_plc, args=('PLC01', 'D100')),
    threading.Thread(target=read_from_plc, args=('PLC02', 'D200')),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

# 출력:
# PLC01/D100: 1234
# PLC02/D200: 5678
```

### Scenario 4: 연결 끊김 복구

```python
# PLC 전원 끄기 또는 네트워크 차단 후
try:
    value = pool_mgr.read_single('PLC01', 'D100')
except ConnectionError as e:
    print(f"Connection failed: {e}")
    # 자동 재연결 시도 (3회)
    # 로그:
    # 2025-10-31 12:00:05 - WARNING - PLC01 reconnect attempt 1/3
    # 2025-10-31 12:00:10 - WARNING - PLC01 reconnect attempt 2/3
    # 2025-10-31 12:00:15 - INFO - PLC01 reconnected successfully

# PLC 전원 켜기 후 자동 복구됨
value = pool_mgr.read_single('PLC01', 'D100')
print(f"Recovered! D100: {value}")
```

### Scenario 5: 배치 읽기 성능 테스트

```python
import time

# 50개 태그 개별 읽기
start = time.time()
for i in range(100, 150):
    value = pool_mgr.read_single('PLC01', f'D{i}')
duration_single = time.time() - start
print(f"Individual read (50 tags): {duration_single:.2f}s")

# 50개 태그 배치 읽기
start = time.time()
addresses = [f'D{i}' for i in range(100, 150)]
values = pool_mgr.read_batch('PLC01', addresses)
duration_batch = time.time() - start
print(f"Batch read (50 tags): {duration_batch:.2f}s")

print(f"Speedup: {duration_single / duration_batch:.1f}x")

# 예상 출력:
# Individual read (50 tags): 2.50s
# Batch read (50 tags): 0.45s
# Speedup: 5.6x
```

---

## Troubleshooting

### 문제 1: "Connection timeout" 에러

**원인**: PLC가 네트워크에 응답하지 않음

**해결**:
1. PLC IP 주소 확인: `ping 192.168.1.10`
2. 방화벽 설정 확인: 포트 5010 오픈
3. PLC MC 프로토콜 활성화 확인
4. connection_timeout 증가: DB에서 10초로 변경

### 문제 2: "Protocol error" 응답

**원인**: PLC 프로토콜 버전 불일치 또는 잘못된 태그 주소

**해결**:
1. PLC 프로토콜 설정 확인 (MC 3E ASCII)
2. 태그 주소 형식 확인 (D100, X10 등)
3. PLC 메모리 영역 확인 (D 영역이 존재하는지)

### 문제 3: "Pool exhausted" 에러

**원인**: 모든 연결이 사용 중

**해결**:
1. Connection Pool 크기 증가 (5 → 10)
2. 태그 읽기 로직 최적화 (배치 읽기 사용)
3. 연결 반환 확인 (예외 처리 시 반드시 반환)

### 문제 4: 성능 저하 (태그당 >100ms)

**원인**: 네트워크 지연 또는 개별 읽기 사용

**해결**:
1. 네트워크 latency 확인: `ping -c 10 192.168.1.10`
2. 배치 읽기로 전환
3. Connection Pool 재사용 확인 (로그에서 "new connection" 빈도 체크)

---

## Testing

### 단위 테스트 실행

```bash
cd backend
pytest tests/unit/test_mc3e_client.py -v
pytest tests/unit/test_connection_pool.py -v
```

### 통합 테스트 실행 (실제 PLC 필요)

```bash
# PLC 시뮬레이터 또는 실제 PLC 필요
pytest tests/integration/test_plc_integration.py -v
```

---

## Next Steps

- **Feature 3**: 멀티 스레드 폴링 엔진 구현 (FIXED/HANDSHAKE 모드)
- **Feature 4**: Oracle DB Writer로 태그 값 저장
- **Feature 5**: REST API/WebSocket 서버로 실시간 데이터 제공

---

## References

- [Feature 1: SQLite 데이터베이스 설정](../../001-project-structure-sqlite-setup/spec.md)
- [pymcprotocol Documentation](https://pypi.org/project/pymcprotocol/)
- [MC 3E ASCII Protocol](https://www.mitsubishielectric.com/)
