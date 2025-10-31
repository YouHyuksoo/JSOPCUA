# Data Model: MC 3E ASCII 프로토콜 통신 및 Connection Pool

**Feature**: MC 3E ASCII 프로토콜 통신 및 Connection Pool
**Date**: 2025-10-31

## Overview

이 기능은 Feature 1의 SQLite 데이터 모델을 활용하고, 런타임 Connection Pool 관리를 위한 메모리 기반 데이터 구조를 추가합니다.

## Entities

### 1. PLCConnection (Feature 1에서 상속)

기존 SQLite `plc_connections` 테이블 활용.

**Attributes**:
- `id`: 고유 식별자
- `plc_code`: PLC 코드 (예: "PLC01")
- `ip_address`: IP 주소
- `port`: 포트 번호 (기본 5010)
- `protocol`: 프로토콜 타입 ("MC_3E_ASCII")
- `connection_timeout`: 연결 타임아웃 (초)
- `is_active`: 활성 상태

**Relationships**:
- `Process` (N:1): 하나의 공정에 속함
- `Tag` (1:N): 여러 태그를 소유함

---

### 2. Tag (Feature 1에서 상속)

기존 SQLite `tags` 테이블 활용.

**Attributes**:
- `id`: 고유 식별자
- `plc_id`: 연관된 PLC ID
- `tag_address`: 태그 주소 (예: "D100")
- `tag_name`: 태그 이름
- `tag_type`: 데이터 타입 (INT, REAL 등)
- `unit`: 단위 (°C, bar 등)
- `scale`: 스케일 인자
- `machine_code`: 14자리 설비 코드

**Relationships**:
- `PLCConnection` (N:1): 하나의 PLC에 속함

---

### 3. ConnectionPool (Runtime, 메모리 전용)

PLC당 관리되는 연결 풀 (메모리에만 존재, DB 저장 안 함).

**Attributes**:
- `plc_id`: 연관된 PLC ID
- `plc_code`: PLC 코드 (식별용)
- `ip_address`: IP 주소
- `port`: 포트
- `max_size`: 최대 연결 수 (5)
- `available_connections`: 사용 가능한 연결 큐
- `active_connections`: 사용 중인 연결 세트
- `total_connections`: 현재 총 연결 수
- `lock`: 스레드 안전을 위한 Lock

**Methods**:
- `get_connection(timeout)`: 사용 가능한 연결 가져오기 (없으면 생성)
- `return_connection(conn)`: 연결 반환
- `close_all()`: 모든 연결 종료

**State Transitions**:
```
[Empty] → [Create first conn] → [Available (1)]
[Available (N)] → [Borrow conn] → [Available (N-1), Active (1)]
[Active (1)] → [Return conn] → [Available (N), Active (0)]
[Available (N)] → [Idle timeout] → [Cleanup] → [Available (N-1)]
```

---

### 4. PooledConnection (Runtime, 메모리 전용)

개별 PLC 연결 wrapper (메모리에만 존재).

**Attributes**:
- `connection`: pymcprotocol Type3E 객체
- `plc_id`: 연관된 PLC ID
- `created_at`: 생성 시간
- `last_used`: 마지막 사용 시간
- `is_connected`: 연결 상태
- `error_count`: 연속 에러 횟수

**Methods**:
- `connect()`: PLC 연결
- `disconnect()`: PLC 연결 해제
- `read_single(address)`: 단일 태그 읽기
- `read_batch(addresses)`: 배치 태그 읽기
- `is_idle(timeout)`: 유휴 상태 확인

---

### 5. ReadRequest (Runtime, 메모리 전용)

태그 읽기 요청 (일시적 데이터 구조).

**Attributes**:
- `request_id`: 고유 요청 ID (UUID)
- `plc_id`: 대상 PLC ID
- `tag_addresses`: 읽을 태그 주소 목록
- `timeout`: 타임아웃 (초)
- `timestamp`: 요청 시간

---

### 6. ReadResponse (Runtime, 메모리 전용)

태그 읽기 응답 (일시적 데이터 구조).

**Attributes**:
- `request_id`: 요청 ID
- `success`: 성공 여부
- `values`: 태그 주소 → 값 매핑 (dict)
- `errors`: 에러 정보 (실패한 태그)
- `response_time_ms`: 응답 시간 (밀리초)
- `timestamp`: 응답 시간

---

## Relationships Diagram

```
┌─────────────────────────────────────────┐
│         SQLite Database (Feature 1)      │
├─────────────────────────────────────────┤
│  lines → processes → plc_connections    │
│                      ↓                   │
│                    tags                  │
└─────────────────────────────────────────┘
              ↓ (읽기 전용)
┌─────────────────────────────────────────┐
│      Runtime Memory (Feature 2)          │
├─────────────────────────────────────────┤
│  PoolManager                             │
│    ├─ ConnectionPool (PLC01)            │
│    │    ├─ PooledConnection (conn1)     │
│    │    ├─ PooledConnection (conn2)     │
│    │    └─ PooledConnection (conn3)     │
│    └─ ConnectionPool (PLC02)            │
│         └─ ...                           │
└─────────────────────────────────────────┘
```

**Data Flow**:
1. 애플리케이션 시작 → SQLite에서 plc_connections 읽기
2. 각 PLC에 대해 ConnectionPool 생성
3. 태그 읽기 요청 → PoolManager → ConnectionPool → PooledConnection
4. PLC 통신 → 결과 반환

---

## Data Validation Rules

### PLCConnection
- `ip_address`: 유효한 IPv4 주소 형식
- `port`: 1-65535 범위
- `connection_timeout`: 1-30초 범위
- `protocol`: "MC_3E_ASCII"만 허용 (이 기능에서)

### Tag
- `tag_address`: 정규식 `^[DXYWMB]\d+$` (예: D100, X10, Y20)
- `plc_id`: plc_connections 테이블에 존재하는 ID

### ConnectionPool
- `max_size`: 1-10 범위
- `total_connections`: `max_size` 이하

### ReadRequest
- `tag_addresses`: 최소 1개, 최대 50개
- `timeout`: 1-30초 범위

---

## Performance Considerations

**Connection Pool Sizing**:
- PLC당 5개 연결 = 동시 5개 요청 처리 가능
- 10개 PLC × 5개 연결 = 최대 50개 동시 연결

**Memory Usage**:
- PooledConnection: ~10KB (pymcprotocol 객체 + 메타데이터)
- ConnectionPool (5 conns): ~50KB
- 10 PLCs: ~500KB 총 메모리 사용

**Scalability**:
- 현재 설계: 10 PLCs, 500 tags/PLC = 5,000 tags
- 배치 읽기: 50 tags/batch = 100 batches
- 총 처리 시간: 100 batches × 500ms = 50초 (전체 스캔)

---

## Future Enhancements

- **ConnectionPoolStats**: 풀 통계 (hit rate, miss rate, 평균 대기 시간)
- **TagCache**: 최근 읽은 태그 값 캐시 (짧은 TTL)
- **Batch Optimization**: 태그 주소 자동 최적화 알고리즘
- **Health Monitoring**: PLC 연결 상태 모니터링 및 알람
