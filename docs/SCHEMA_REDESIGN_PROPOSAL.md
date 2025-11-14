# SCADA 데이터베이스 스키마 재설계 제안서

## 문제점 요약

### 현재 구조의 문제
1. **PLC가 공정에 종속** (`plc_connections.process_id` FK) ❌
2. **공정이 설비에 종속** (`processes.machine_id` FK) ❌
3. **알람 마스터 누락** (M 주소 알람 정보 미관리) ❌
4. **Tags가 process_id를 직접 참조하지 않음** ❌

### 실제 요구사항
1. PLC 3대는 독립적 물리 장치 (공정과 무관)
2. 공정 30개는 독립적 논리 단위 (설비와 무관)
3. Tags가 PLC + 공정을 연결하는 중심 테이블
4. 알람 마스터 별도 관리 (M 주소 알람 정의)
5. SQLite 독립 운영 (Oracle DB 참조 없음)

---

## 수정된 ERD

```
┌─────────────────────┐
│  plc_connections    │ (PLC 마스터)
│  ──────────────────│
│  id (PK)            │
│  plc_code (UNIQUE)  │ ← "PLC01", "PLC02", "PLC03"
│  plc_name           │
│  ip_address         │
│  port               │
│  protocol           │
└─────────────────────┘
         ↑
         │ FK
         │
┌────────┴────────────┐         ┌─────────────────────┐
│  tags               │◄────────┤  processes          │ (공정 마스터)
│  ──────────────────│  FK     │  ──────────────────│
│  id (PK)            │         │  id (PK)            │
│  plc_id (FK)        │         │  process_code (UK)  │ ← "KRCWO12ELOA101"
│  process_id (FK)    │─────────│  process_name       │
│  tag_address        │         │  location           │
│  tag_name           │         │  sequence_order     │
│  tag_type           │         └─────────────────────┘
│  polling_group_id   │
│  UNIQUE(plc_id,     │
│         tag_address)│
└─────────────────────┘
         ↑
         │ FK (optional)
         │
┌────────┴────────────┐
│  polling_groups     │ (폴링 그룹)
│  ──────────────────│
│  id (PK)            │
│  group_name (UK)    │
│  plc_id (FK)        │
│  polling_mode       │
│  polling_interval_ms│
└─────────────────────┘

┌─────────────────────┐
│  alarm_masters      │ (알람 마스터) ← 신규 추가
│  ──────────────────│
│  id (PK)            │
│  plc_id (FK)        │
│  process_id (FK)    │
│  alarm_address      │ ← "M100", "M101", "M102"
│  alarm_code         │ ← "ALM_OVERHEAT_01"
│  alarm_message      │ ← "과열 알람 발생"
│  severity           │ ← "WARNING", "ERROR", "CRITICAL"
│  UNIQUE(plc_id,     │
│         alarm_addr) │
└─────────────────────┘
```

---

## 테이블별 상세 정의

### 1. `plc_connections` (PLC 마스터) ✅ 독립 테이블

```sql
CREATE TABLE plc_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_code VARCHAR(20) NOT NULL UNIQUE,           -- "PLC01", "PLC02", "PLC03"
    plc_name VARCHAR(100) NOT NULL,                 -- "메인 CPU PLC"
    ip_address VARCHAR(45) NOT NULL,                -- "192.168.1.10"
    port INTEGER NOT NULL DEFAULT 5010,
    protocol VARCHAR(20) NOT NULL DEFAULT 'MC_3E_ASCII',
    network_no INTEGER DEFAULT 0,                   -- MC 프로토콜 네트워크 번호
    station_no INTEGER DEFAULT 0,                   -- MC 프로토콜 국번
    connection_timeout INTEGER DEFAULT 5,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**데이터 예시:**
| id | plc_code | plc_name | ip_address | port |
|----|----------|----------|------------|------|
| 1 | PLC01 | 메인 CPU | 192.168.1.10 | 5010 |
| 2 | PLC02 | 서브 CPU1 | 192.168.1.11 | 5010 |
| 3 | PLC03 | 서브 CPU2 | 192.168.1.12 | 5010 |

---

### 2. `processes` (공정/설비 마스터) ✅ 독립 테이블

```sql
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_code VARCHAR(14) NOT NULL UNIQUE,       -- "KRCWO12ELOA101" (14자리)
    process_name VARCHAR(100) NOT NULL,             -- "엘레베이터 A 공정"
    location VARCHAR(100),                          -- "1동 2층"
    sequence_order INTEGER DEFAULT 0,               -- 공정 순서
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**데이터 예시:**
| id | process_code | process_name | location |
|----|--------------|--------------|----------|
| 1 | KRCWO12ELOA101 | 엘레베이터 A | 1동 2층 |
| 2 | KRCWO12WLDA201 | 용접기 A | 1동 3층 |
| 3 | KRCWO12PRSA301 | 프레스 A | 2동 1층 |

---

### 3. `tags` (태그 마스터) ✅ PLC + 공정 연결

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,                        -- FK to plc_connections
    process_id INTEGER NOT NULL,                    -- FK to processes
    tag_address VARCHAR(50) NOT NULL,               -- "D100", "W200", "M100"
    tag_name VARCHAR(100) NOT NULL,                 -- "엘레베이터 A 온도"
    tag_type VARCHAR(20) NOT NULL DEFAULT 'INT',    -- "INT", "FLOAT", "BIT"
    unit VARCHAR(20),                               -- "℃", "bar", "rpm"
    scale REAL DEFAULT 1.0,                         -- 스케일 배율
    offset REAL DEFAULT 0.0,                        -- 오프셋
    min_value REAL,                                 -- 최소값
    max_value REAL,                                 -- 최대값
    polling_group_id INTEGER,                       -- FK to polling_groups (NULL 허용)
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_value TEXT,                                -- 마지막 폴링값
    last_updated_at TIMESTAMP,                      -- 마지막 업데이트 시각
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL,

    UNIQUE(plc_id, tag_address)  -- PLC + 주소 = 유일키
);

CREATE INDEX idx_tags_plc_id ON tags(plc_id);
CREATE INDEX idx_tags_process_id ON tags(process_id);
CREATE INDEX idx_tags_polling_group ON tags(polling_group_id);
CREATE INDEX idx_tags_active ON tags(is_active);
```

**데이터 예시:**
| plc_id | plc_code | process_id | process_code | tag_address | tag_name |
|--------|----------|------------|--------------|-------------|----------|
| 1 | PLC01 | 1 | KRCWO12ELOA101 | D100 | 엘레베이터 A 온도 |
| 1 | PLC01 | 1 | KRCWO12ELOA101 | D200 | 엘레베이터 A 압력 |
| 1 | PLC01 | 2 | KRCWO12WLDA201 | D100 | 용접기 온도 (같은 D100, 다른 공정) |
| 2 | PLC02 | 1 | KRCWO12ELOA101 | D100 | 엘레베이터 상태 (같은 D100, 다른 PLC) |

---

### 4. `alarm_masters` (알람 마스터) ✨ 신규 추가

```sql
CREATE TABLE alarm_masters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,                        -- FK to plc_connections
    process_id INTEGER NOT NULL,                    -- FK to processes
    alarm_address VARCHAR(50) NOT NULL,             -- "M100", "M101", "M102"
    alarm_code VARCHAR(50) NOT NULL UNIQUE,         -- "ALM_OVERHEAT_01"
    alarm_message VARCHAR(200) NOT NULL,            -- "과열 알람 발생"
    alarm_description TEXT,                         -- 상세 설명
    severity VARCHAR(20) NOT NULL DEFAULT 'WARNING',-- "INFO", "WARNING", "ERROR", "CRITICAL"
    action_guide TEXT,                              -- 조치 가이드
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,

    UNIQUE(plc_id, alarm_address)  -- PLC + 알람주소 = 유일키
);

CREATE INDEX idx_alarm_plc_id ON alarm_masters(plc_id);
CREATE INDEX idx_alarm_process_id ON alarm_masters(process_id);
CREATE INDEX idx_alarm_severity ON alarm_masters(severity);
CREATE INDEX idx_alarm_active ON alarm_masters(is_active);
```

**데이터 예시:**
| plc_id | process_id | alarm_address | alarm_code | alarm_message | severity |
|--------|------------|---------------|------------|---------------|----------|
| 1 | 1 | M100 | ALM_OVERHEAT_01 | 엘레베이터 과열 알람 | ERROR |
| 1 | 1 | M101 | ALM_PRESSURE_01 | 압력 이상 알람 | WARNING |
| 1 | 2 | M100 | ALM_WELD_TEMP_01 | 용접 온도 이상 | CRITICAL |

---

### 5. `polling_groups` (폴링 그룹)

```sql
CREATE TABLE polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(50) NOT NULL UNIQUE,         -- "그룹1_엘레베이터"
    plc_id INTEGER NOT NULL,                        -- FK to plc_connections
    polling_mode VARCHAR(20) NOT NULL CHECK(polling_mode IN ('FIXED', 'HANDSHAKE')),
    polling_interval_ms INTEGER NOT NULL DEFAULT 1000,
    trigger_bit_address VARCHAR(20),                -- HANDSHAKE 모드 트리거 주소
    trigger_bit_offset INTEGER DEFAULT 0,
    auto_reset_trigger BOOLEAN DEFAULT 1,
    priority VARCHAR(20) DEFAULT 'NORMAL',          -- "HIGH", "NORMAL", "LOW"
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE
);

CREATE INDEX idx_polling_plc_id ON polling_groups(plc_id);
CREATE INDEX idx_polling_active ON polling_groups(is_active);
```

---

## 주요 변경 사항

### ❌ 삭제된 테이블
- `machines` (설비 테이블) → 불필요한 계층 구조

### ✅ 수정된 테이블
- `processes`: `machine_id` FK 제거 (독립 테이블)
- `plc_connections`: `process_id` FK 제거 (독립 테이블)
- `tags`: `process_id` FK 추가 (PLC + 공정 연결)

### ✨ 추가된 테이블
- `alarm_masters`: 알람 정의 마스터 (M 주소 관리)

---

## 데이터 흐름 예시

### 사용자 등록 순서

```
1. PLC 등록
   └─ INSERT INTO plc_connections (plc_code, ip_address, ...)

2. 공정 등록
   └─ INSERT INTO processes (process_code, process_name, ...)

3. 태그 등록 (PLC + 공정 연결)
   └─ INSERT INTO tags (plc_id, process_id, tag_address, ...)

4. 알람 등록 (PLC + 공정 연결)
   └─ INSERT INTO alarm_masters (plc_id, process_id, alarm_address, ...)

5. 폴링 그룹 생성
   └─ INSERT INTO polling_groups (group_name, plc_id, ...)

6. 태그를 폴링 그룹에 할당
   └─ UPDATE tags SET polling_group_id = ? WHERE id IN (...)
```

---

## 폴링 동작 흐름

```
1. 폴링 그룹 로딩
   SELECT pg.*, pc.plc_code, pc.ip_address
   FROM polling_groups pg
   JOIN plc_connections pc ON pg.plc_id = pc.id
   WHERE pg.is_active = 1

2. 폴링 그룹별 태그 로딩
   SELECT t.tag_address, t.tag_type, p.process_code
   FROM tags t
   JOIN processes p ON t.process_id = p.id
   WHERE t.polling_group_id = ?
     AND t.is_active = 1

3. 알람 비트 로딩 (M 주소)
   SELECT a.alarm_address, a.alarm_code, a.alarm_message
   FROM alarm_masters a
   WHERE a.plc_id = ?
     AND a.is_active = 1

4. PLC 통신 (pymcprotocol)
   - 태그 배치 읽기: batchread_wordunits([D100, D200, W100, ...])
   - 알람 비트 읽기: batchread_bitunits([M100, M101, M102, ...])

5. Oracle DB 저장
   - 태그 데이터: INSERT INTO scada_data_table (plc_code, process_code, tag_address, value, ...)
   - 알람 이벤트: INSERT INTO alarm_history (plc_code, process_code, alarm_code, ...)
```

---

## 마이그레이션 전략

### 옵션 1: 전체 재생성 (권장)
1. 기존 데이터 백업
2. 새 스키마로 데이터베이스 재생성
3. 기존 데이터 변환 스크립트 실행

### 옵션 2: 단계별 마이그레이션
1. `alarm_masters` 테이블 추가
2. `tags`에 `process_id` 컬럼 추가
3. `plc_connections`에서 `process_id` 제거
4. `processes`에서 `machine_id` 제거
5. `machines` 테이블 삭제

---

## 다음 단계

이 설계안으로 진행할까요?

1. ✅ 승인 → 마이그레이션 스크립트 작성
2. ❌ 수정 필요 → 추가 요구사항 확인
