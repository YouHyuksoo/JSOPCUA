# 03. 데이터베이스 설계

## 3.1 데이터베이스 개요

JSScada 시스템은 2개의 데이터베이스를 사용합니다:

1. **SQLite (로컬)**: SCADA 설정 정보 저장
   - 라인, 공정, PLC, 태그, 폴링 그룹 마스터 데이터
   - 파일 위치: `backend/config/scada.db`

2. **Oracle (원격)**: 폴링 결과 저장
   - 기존 시스템과 연동
   - 알람/상태 데이터, 비트 폴링 결과

---

## 3.2 SQLite 데이터베이스 (SCADA 로컬 설정)

### 3.2.1 ERD (Entity Relationship Diagram)

```
┌────────────────┐
│     lines      │
│                │
│ PK id          │
│    line_code   │◄──┐
│    line_name   │   │
│    location    │   │
│    enabled     │   │
└────────────────┘   │
                     │
                     │ FK line_id
                     │
┌────────────────────┴──────┐
│      processes            │
│                           │
│ PK id                     │
│ FK line_id                │
│    process_sequence       │
│    process_code           │◄──┐
│    process_name           │   │
│    equipment_type         │   │
│    enabled                │   │
└───────────────────────────┘   │
                                │
                                │ FK process_id
                                │
┌───────────────────────────────┴───┐
│       plc_connections             │
│                                   │
│ PK id                             │
│ FK process_id                     │
│    plc_code                       │◄──┐
│    ip_address                     │   │
│    port                           │   │
│    network_no                     │   │
│    station_no                     │   │
│    enabled                        │   │
└───────────────────────────────────┘   │
                                        │
                                        │ FK plc_id
                                        │
┌───────────────────────────────────────┴──────┐
│                 tags                         │
│                                              │
│ PK id                                        │
│ FK plc_id                                    │
│ FK process_id                                │
│    tag_address                               │
│    tag_name                                  │
│    tag_division                              │
│    data_type                                 │
│    unit                                      │
│    scale                                     │
│    machine_code                              │
│ FK polling_group_id                          │◄──┐
│    enabled                                   │   │
└──────────────────────────────────────────────┘   │
                                                   │
                                                   │
┌──────────────────────────────────────────────────┴─────┐
│              polling_groups                            │
│                                                        │
│ PK id                                                  │
│    group_name                                          │
│    line_code                                           │
│    process_code                                        │
│ FK plc_id                                              │
│    mode                (FIXED / HANDSHAKE)             │
│    interval_ms                                         │
│    trigger_bit_address                                 │
│    trigger_bit_offset                                  │
│    auto_reset_trigger                                  │
│    priority                                            │
│    enabled                                             │
└────────────────────────────────────────────────────────┘
```

---

### 3.2.2 테이블 정의

#### 테이블: `lines` (라인)

생산 라인 정보를 저장합니다.

```sql
CREATE TABLE lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_code VARCHAR(50) UNIQUE NOT NULL,        -- 라인 코드 (예: 'LINE01')
    line_name VARCHAR(200) NOT NULL,              -- 라인 명 (예: 'TUB 가공 라인')
    location VARCHAR(100),                        -- 위치 (예: '창원 공장')
    enabled BOOLEAN DEFAULT 1,                    -- 활성화 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_lines_code ON lines(line_code);
```

**예시 데이터**:
```sql
INSERT INTO lines (line_code, line_name, location, enabled) VALUES
('LINE01', 'TUB 가공 라인', '창원 공장', 1);
```

---

#### 테이블: `processes` (공정)

생산 공정 정보를 저장합니다.

```sql
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id INTEGER NOT NULL,                     -- 라인 ID (FK)
    process_sequence INTEGER NOT NULL,            -- 공정 순서 (1, 2, 3, ...)
    process_code VARCHAR(50) UNIQUE NOT NULL,     -- 14자리 설비 코드 (예: 'KRCWO12ELOA101')
    process_name VARCHAR(200) NOT NULL,           -- 공정 명 (예: 'Upper Loading')
    equipment_type VARCHAR(10),                   -- 설비 타입 (예: 'LOA', 'WEM', 'DRY')
    enabled BOOLEAN DEFAULT 1,                    -- 활성화 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_id) REFERENCES lines(id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_processes_line ON processes(line_id);
CREATE INDEX idx_processes_code ON processes(process_code);
```

**예시 데이터**:
```sql
INSERT INTO processes (line_id, process_sequence, process_code, process_name, equipment_type, enabled) VALUES
(1, 1, 'KRCWO12ELOA101', 'Upper Loading', 'LOA', 1),
(1, 2, 'KRCWO12EWEM102', 'Welding Machine 1', 'WEM', 1);
```

---

#### 테이블: `plc_connections` (PLC 연결)

PLC 연결 정보를 저장합니다.

```sql
CREATE TABLE plc_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,                  -- 공정 ID (FK)
    plc_code VARCHAR(50) UNIQUE NOT NULL,         -- PLC 코드 (예: 'PLC01')
    ip_address VARCHAR(50) NOT NULL,              -- PLC IP 주소 (예: '192.168.1.10')
    port INTEGER DEFAULT 5000,                    -- PLC 포트 (기본: 5000)
    network_no INTEGER DEFAULT 0,                 -- MC 프로토콜 네트워크 번호
    station_no INTEGER DEFAULT 0,                 -- MC 프로토콜 스테이션 번호
    enabled BOOLEAN DEFAULT 1,                    -- 활성화 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_plc_process ON plc_connections(process_id);
CREATE INDEX idx_plc_code ON plc_connections(plc_code);
```

**예시 데이터**:
```sql
INSERT INTO plc_connections (process_id, plc_code, ip_address, port, network_no, station_no, enabled) VALUES
(1, 'PLC01', '192.168.1.10', 5000, 0, 0, 1),
(2, 'PLC02', '192.168.1.11', 5000, 0, 0, 1);
```

---

#### 테이블: `tags` (태그)

PLC 태그 정보를 저장합니다.

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,                      -- PLC ID (FK)
    process_id INTEGER NOT NULL,                  -- 공정 ID (FK)
    tag_address VARCHAR(20) NOT NULL,             -- TAG 주소 (예: 'W150', 'M100')
    tag_name VARCHAR(200) NOT NULL,               -- TAG 명 (예: 'Upper셔틀#1 유효부하')
    tag_division VARCHAR(50),                     -- TAG 구분 (예: '부하율', '전류치')
    data_type VARCHAR(20) DEFAULT 'WORD',         -- 데이터 타입 (WORD, DWORD, BIT 등)
    unit VARCHAR(20),                             -- 단위 (예: '%', 'A', '℃')
    scale DECIMAL(10, 4) DEFAULT 1.0,             -- 스케일 팩터 (예: 0.1, 1.0)
    machine_code VARCHAR(200),                    -- 설비 코드 (KRCWO12ELOA101)
    polling_group_id INTEGER,                     -- 폴링 그룹 ID (FK)
    enabled BOOLEAN DEFAULT 1,                    -- 활성화 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL
);

-- 인덱스
CREATE INDEX idx_tags_plc ON tags(plc_id);
CREATE INDEX idx_tags_process ON tags(process_id);
CREATE INDEX idx_tags_polling_group ON tags(polling_group_id);
CREATE INDEX idx_tags_address ON tags(tag_address);
```

**예시 데이터**:
```sql
INSERT INTO tags (plc_id, process_id, tag_address, tag_name, tag_division, data_type, unit, scale, machine_code, polling_group_id, enabled) VALUES
(1, 1, 'W150', 'Upper셔틀#1 유효부하', '부하율', 'WORD', '%', 1.0, 'KRCWO12ELOA101', 1, 1),
(1, 1, 'W151', 'Upper셔틀#2 유효부하', '부하율', 'WORD', '%', 1.0, 'KRCWO12ELOA101', 1, 1),
(1, 1, 'W152', 'Upper샤프트모터 전류치', '전류치', 'WORD', 'A', 0.1, 'KRCWO12ELOA101', 1, 1);
```

---

#### 테이블: `polling_groups` (폴링 그룹)

폴링 그룹 설정을 저장합니다.

```sql
CREATE TABLE polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(200) NOT NULL,             -- 그룹 명 (예: 'Upper Loading - 부하율')
    line_code VARCHAR(50),                        -- 라인 코드
    process_code VARCHAR(50),                     -- 공정 코드
    plc_id INTEGER NOT NULL,                      -- PLC ID (FK)
    mode VARCHAR(20) DEFAULT 'FIXED',             -- 폴링 모드 (FIXED, HANDSHAKE)
    interval_ms INTEGER DEFAULT 1000,             -- 폴링 간격 (밀리초)
    trigger_bit_address VARCHAR(20),              -- 트리거 비트 주소 (예: 'B0110')
    trigger_bit_offset INTEGER DEFAULT 0,         -- 트리거 비트 오프셋 (0~15)
    auto_reset_trigger BOOLEAN DEFAULT 1,         -- 자동 트리거 리셋 여부
    priority VARCHAR(20) DEFAULT 'NORMAL',        -- 우선순위 (HIGH, NORMAL, LOW)
    enabled BOOLEAN DEFAULT 1,                    -- 활성화 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_polling_groups_plc ON polling_groups(plc_id);
CREATE INDEX idx_polling_groups_enabled ON polling_groups(enabled);
```

**예시 데이터**:
```sql
-- 고정 간격 폴링 그룹
INSERT INTO polling_groups (group_name, line_code, process_code, plc_id, mode, interval_ms, enabled) VALUES
('Upper Loading - 고정 폴링', 'LINE01', 'KRCWO12ELOA101', 1, 'FIXED', 1000, 1);

-- 핸드셰이크 폴링 그룹
INSERT INTO polling_groups (group_name, line_code, process_code, plc_id, mode, interval_ms, trigger_bit_address, trigger_bit_offset, auto_reset_trigger, enabled) VALUES
('Upper Loading - 작업 완료', 'LINE01', 'KRCWO12ELOA101', 1, 'HANDSHAKE', 500, 'B0110', 0, 1, 1);
```

---

### 3.2.3 SQLite 뷰 (View)

#### 뷰: `v_tags_with_plc`

태그 정보와 PLC 정보를 조인한 뷰입니다.

```sql
CREATE VIEW v_tags_with_plc AS
SELECT
    t.id AS tag_id,
    t.tag_address,
    t.tag_name,
    t.tag_division,
    t.data_type,
    t.unit,
    t.scale,
    t.machine_code,
    t.polling_group_id,
    t.enabled AS tag_enabled,
    p.plc_code,
    p.ip_address,
    p.port,
    p.enabled AS plc_enabled,
    pr.process_code,
    pr.process_name,
    l.line_code,
    l.line_name
FROM tags t
JOIN plc_connections p ON t.plc_id = p.id
JOIN processes pr ON t.process_id = pr.id
JOIN lines l ON pr.line_id = l.id;
```

---

### 3.2.4 SQLite 초기 데이터 스크립트

```sql
-- backend/config/init_scada_db.sql

-- 1. 라인 등록
INSERT INTO lines (line_code, line_name, location, enabled) VALUES
('LINE01', 'TUB 가공 라인', '창원 공장', 1);

-- 2. 공정 등록 (34개 공정)
INSERT INTO processes (line_id, process_sequence, process_code, process_name, equipment_type, enabled) VALUES
(1, 1, 'KRCWO12ELOA101', 'Upper Loading', 'LOA', 1),
(1, 2, 'KRCWO12EWEM102', 'Welding Machine 1', 'WEM', 1),
(1, 3, 'KRCWO12EMOM103', 'Material Handling 1', 'MOM', 1),
(1, 4, 'KRCWO12EDRY104', 'Dryer 1', 'DRY', 1),
-- ... 30개 더 추가

-- 3. PLC 등록
INSERT INTO plc_connections (process_id, plc_code, ip_address, port, network_no, station_no, enabled) VALUES
(1, 'PLC01', '192.168.1.10', 5000, 0, 0, 1),
(2, 'PLC02', '192.168.1.11', 5000, 0, 0, 1),
(3, 'PLC03', '192.168.1.12', 5000, 0, 0, 1);

-- 4. 폴링 그룹 등록
INSERT INTO polling_groups (group_name, line_code, process_code, plc_id, mode, interval_ms, trigger_bit_address, trigger_bit_offset, auto_reset_trigger, enabled) VALUES
('Upper Loading - 핸드셰이크', 'LINE01', 'KRCWO12ELOA101', 1, 'HANDSHAKE', 500, 'B0110', 0, 1, 1),
('Welding - 고정 간격', 'LINE01', 'KRCWO12EWEM102', 2, 'FIXED', 1000, NULL, NULL, 0, 1);

-- 5. 태그 등록 (3,491개 태그)
-- 태그 리스트.xlsx 파일에서 CSV로 변환 후 일괄 등록
INSERT INTO tags (plc_id, process_id, tag_address, tag_name, tag_division, data_type, unit, scale, machine_code, polling_group_id, enabled) VALUES
(1, 1, 'W150', 'Upper셔틀#1 유효부하', '부하율', 'WORD', '%', 1.0, 'KRCWO12ELOA101', 1, 1),
(1, 1, 'W151', 'Upper셔틀#2 유효부하', '부하율', 'WORD', '%', 1.0, 'KRCWO12ELOA101', 1, 1),
-- ... 3,489개 더 추가
```

---

## 3.3 Oracle 데이터베이스 (폴링 결과 저장)

### 3.3.1 Oracle 테이블 개요

SCADA는 폴링 결과를 기존 Oracle DB의 **2개 테이블**에 INSERT합니다.

1. **알람/상태 데이터 테이블** (22 컬럼): 알람 조건 만족 시 또는 상태 변경 시 저장
2. **비트 폴링 결과 테이블** (10 컬럼): 모든 폴링 결과를 저장

---

### 3.3.2 테이블 1: 알람/상태 데이터 (22 컬럼)

> **참고**: 실제 테이블명은 사용자가 제공해야 합니다. 여기서는 `SCADA_ALARM_STATUS`로 가정합니다.

```sql
-- 테이블명: SCADA_ALARM_STATUS (가정)

MACHINE_DIV          VARCHAR2(20)      -- 'PLC' 고정
MACHINE_CODE         VARCHAR2(20)      -- 설비코드 (KRCWO12ELOA101)
MACHINE_STATUS_DIV   VARCHAR2(20)      -- 'ALARM', 'QC' 등
MACHINE_STATUS_VALUE VARCHAR2(20)      -- 상태값
MACHINE_MESSAGE      VARCHAR2(1000)    -- 태그명 또는 메시지
MACHINE_DATETIME     VARCHAR2(30)      -- YYYYMMDDHH24MISS
COMMENTS             VARCHAR2(1000)    -- 비고
ENTER_DATE           DATE              -- 입력 일자 (SYSDATE)
ENTER_BY             VARCHAR2(20)      -- 'SCADA' 고정
ORGANIZATION_ID      NUMBER            -- 조직 ID (고정값 1)
PLC_CODE             VARCHAR2(20)      -- PLC 코드
TAG_ADDRESS          VARCHAR2(20)      -- TAG 주소 (W150, M100 등)
ALARM_START_DATETIME DATE              -- 알람 시작 시각
ALARM_END_DATETIME   DATE              -- 알람 종료 시각
ALARM_TIME_TERM      NUMBER            -- 알람 지속 시간 (초)
PLC_TIMESTAMP        TIMESTAMP(6)      -- 폴링 시각
TAG_TYPE             VARCHAR2(20)      -- TAG 타입
IS_FIXED             VARCHAR2(20)      -- 수리 완료 여부
SCADA_ID             NUMBER            -- SCADA ID
EQP_STATE            VARCHAR2(20)      -- 설비 상태
CONTROL_STATE        VARCHAR2(20)      -- '수동', '자동'
TAG_ADDRESS_REASON   VARCHAR2(20)      -- TAG 주소 사유
```

#### Python 코드에서 INSERT 예시

```python
# src/database/oracle_writer.py

def _insert_alarm_record(self, data_point):
    """
    알람/상태 데이터 테이블에 INSERT

    조건: 알람 조건을 만족하는 경우 (예: 온도 > 100℃)
    """
    cursor = self.connection.cursor()

    try:
        cursor.execute(f"""
            INSERT INTO {self.table_alarm} (
                MACHINE_DIV,
                MACHINE_CODE,
                MACHINE_STATUS_DIV,
                MACHINE_STATUS_VALUE,
                MACHINE_MESSAGE,
                MACHINE_DATETIME,
                COMMENTS,
                ENTER_DATE,
                ENTER_BY,
                ORGANIZATION_ID,
                PLC_CODE,
                TAG_ADDRESS,
                ALARM_START_DATETIME,
                ALARM_END_DATETIME,
                ALARM_TIME_TERM,
                PLC_TIMESTAMP,
                TAG_TYPE,
                IS_FIXED,
                SCADA_ID,
                EQP_STATE,
                CONTROL_STATE,
                TAG_ADDRESS_REASON
            ) VALUES (
                'PLC',
                :machine_code,
                'ALARM',
                :machine_status_value,
                :machine_message,
                :machine_datetime,
                :comments,
                SYSDATE,
                'SCADA',
                1,
                :plc_code,
                :tag_address,
                :alarm_start_datetime,
                NULL,
                NULL,
                :plc_timestamp,
                :tag_type,
                'N',
                1,
                :eqp_state,
                :control_state,
                NULL
            )
        """, {
            'machine_code': data_point['process_code'],  # KRCWO12ELOA101
            'machine_status_value': '1',  # 알람 레벨
            'machine_message': f"{data_point['tag_name']} 알람 발생",
            'machine_datetime': data_point['timestamp'].strftime('%Y%m%d%H%M%S'),
            'comments': f"값: {data_point['value']} {data_point['unit']}",
            'plc_code': data_point['plc_code'],
            'tag_address': data_point['tag_address'],
            'alarm_start_datetime': data_point['timestamp'],
            'plc_timestamp': data_point['timestamp'],
            'tag_type': 'ANALOG',
            'eqp_state': 'RUNNING',
            'control_state': '자동'
        })

        self.connection.commit()

    except Exception as e:
        self.connection.rollback()
        self.logger.error.exception(f"Failed to insert alarm record: {e}")
        raise

    finally:
        cursor.close()
```

---

### 3.3.3 테이블 2: 비트 폴링 결과 (10 컬럼)

> **참고**: 실제 테이블명은 사용자가 제공해야 합니다. 여기서는 `SCADA_BIT_POLLING`으로 가정합니다.

```sql
-- 테이블명: SCADA_BIT_POLLING (가정)

PLC_CODE         VARCHAR2(20)      -- PLC 코드
MACHINE_CODE     VARCHAR2(20)      -- 설비코드
TAG_ADDRESS      VARCHAR2(20)      -- TAG 주소
TAG_VALUE        VARCHAR2(20)      -- 폴링 값 (스케일 적용 후)
MACHINE_DATETIME VARCHAR2(30)      -- YYYYMMDDHH24MISS
PLC_TIMESTAMP    TIMESTAMP(6)      -- 폴링 시각
COMMENTS         VARCHAR2(1000)    -- TAG 명 (비고)
ENTER_DATE       DATE              -- 입력 일자 (SYSDATE)
ENTER_BY         VARCHAR2(20)      -- 'SCADA' 고정
ORGANIZATION_ID  NUMBER            -- 조직 ID (고정값 1)
```

#### Python 코드에서 INSERT 예시

```python
# src/database/oracle_writer.py

def _batch_insert(self, batch):
    """
    비트 폴링 결과 테이블에 배치 INSERT

    모든 폴링 결과를 이 테이블에 저장
    """
    cursor = self.connection.cursor()

    try:
        for data_point in batch:
            cursor.execute(f"""
                INSERT INTO {self.table_bit} (
                    PLC_CODE,
                    MACHINE_CODE,
                    TAG_ADDRESS,
                    TAG_VALUE,
                    MACHINE_DATETIME,
                    PLC_TIMESTAMP,
                    COMMENTS,
                    ENTER_DATE,
                    ENTER_BY,
                    ORGANIZATION_ID
                ) VALUES (
                    :plc_code,
                    :machine_code,
                    :tag_address,
                    :tag_value,
                    :machine_datetime,
                    :plc_timestamp,
                    :comments,
                    SYSDATE,
                    'SCADA',
                    1
                )
            """, {
                'plc_code': data_point['plc_code'],
                'machine_code': data_point['process_code'],  # KRCWO12ELOA101
                'tag_address': data_point['tag_address'],
                'tag_value': str(data_point['value']),  # 스케일 적용 후 값
                'machine_datetime': data_point['timestamp'].strftime('%Y%m%d%H%M%S'),
                'plc_timestamp': data_point['timestamp'],
                'comments': data_point['tag_name']
            })

        self.connection.commit()
        self.logger.perf.info(f"Batch inserted {len(batch)} records to Oracle")

    except Exception as e:
        self.connection.rollback()
        self.logger.error.exception(f"Batch insert failed: {e}")
        raise

    finally:
        cursor.close()
```

---

## 3.4 데이터 매핑 전략

### 3.4.1 SQLite → Python 객체

```python
# src/database/models.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Tag:
    """태그 데이터 모델"""
    id: int
    plc_id: int
    process_id: int
    tag_address: str
    tag_name: str
    tag_division: str
    data_type: str
    unit: str
    scale: float
    machine_code: str
    polling_group_id: int
    enabled: bool

@dataclass
class PollingGroup:
    """폴링 그룹 데이터 모델"""
    id: int
    group_name: str
    line_code: str
    process_code: str
    plc_id: int
    mode: str  # 'FIXED' or 'HANDSHAKE'
    interval_ms: int
    trigger_bit_address: str
    trigger_bit_offset: int
    auto_reset_trigger: bool
    priority: str
    enabled: bool
    tags: list[Tag]  # 이 그룹에 속한 태그 리스트

@dataclass
class PLCConnection:
    """PLC 연결 데이터 모델"""
    id: int
    process_id: int
    plc_code: str
    ip_address: str
    port: int
    network_no: int
    station_no: int
    enabled: bool

@dataclass
class DataPoint:
    """폴링 데이터 포인트"""
    plc_code: str
    process_code: str
    tag_address: str
    tag_name: str
    value: float
    unit: str
    timestamp: datetime
    polling_group_id: int
```

---

### 3.4.2 Python 객체 → Oracle DB

```python
# src/database/oracle_writer.py

def _map_to_oracle_alarm_record(self, data_point: DataPoint) -> dict:
    """
    DataPoint 객체를 Oracle 알람/상태 데이터 레코드로 매핑
    """
    return {
        'machine_div': 'PLC',
        'machine_code': data_point.process_code,
        'machine_status_div': 'ALARM',
        'machine_status_value': '1',
        'machine_message': f"{data_point.tag_name} 알람 발생",
        'machine_datetime': data_point.timestamp.strftime('%Y%m%d%H%M%S'),
        'comments': f"값: {data_point.value} {data_point.unit}",
        'plc_code': data_point.plc_code,
        'tag_address': data_point.tag_address,
        'alarm_start_datetime': data_point.timestamp,
        'plc_timestamp': data_point.timestamp,
        'tag_type': 'ANALOG',
        'eqp_state': 'RUNNING',
        'control_state': '자동'
    }

def _map_to_oracle_bit_record(self, data_point: DataPoint) -> dict:
    """
    DataPoint 객체를 Oracle 비트 폴링 결과 레코드로 매핑
    """
    return {
        'plc_code': data_point.plc_code,
        'machine_code': data_point.process_code,
        'tag_address': data_point.tag_address,
        'tag_value': str(data_point.value),
        'machine_datetime': data_point.timestamp.strftime('%Y%m%d%H%M%S'),
        'plc_timestamp': data_point.timestamp,
        'comments': data_point.tag_name
    }
```

---

## 3.5 데이터베이스 관리

### 3.5.1 SQLite 백업 전략

```bash
# 매일 자동 백업 스크립트
# backend/scripts/backup_sqlite.sh

#!/bin/bash

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scada_$TIMESTAMP.db"

mkdir -p $BACKUP_DIR

# SQLite 백업
sqlite3 ./config/scada.db ".backup $BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "scada_*.db" -mtime +30 -delete
```

---

### 3.5.2 Oracle 데이터 보관 정책

```sql
-- Oracle 데이터 보관 정책 (예시)

-- 1년 이상 된 폴링 결과 데이터 삭제 (월별 배치)
DELETE FROM SCADA_BIT_POLLING
WHERE PLC_TIMESTAMP < ADD_MONTHS(SYSDATE, -12);

-- 알람 데이터는 3년 보관
DELETE FROM SCADA_ALARM_STATUS
WHERE ALARM_START_DATETIME < ADD_MONTHS(SYSDATE, -36);

COMMIT;
```

---

### 3.5.3 데이터베이스 초기화 스크립트

```python
# backend/scripts/init_database.py

import sqlite3
import os

def init_sqlite_database():
    """SQLite 데이터베이스 초기화"""
    db_path = './config/scada.db'

    # 기존 DB 삭제 (개발 환경)
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    # 연결 및 테이블 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 테이블 생성 (lines, processes, plc_connections, tags, polling_groups)
    with open('./config/init_scada_db.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()

    print(f"SQLite database initialized: {db_path}")

if __name__ == '__main__':
    init_sqlite_database()
```

---

## 3.6 데이터 흐름 다이어그램

```
┌────────────────────────────────────────────────────────────────┐
│                       데이터 흐름                               │
└────────────────────────────────────────────────────────────────┘

1. 백엔드 시작 시 설정 로드
   ┌──────────┐
   │ SQLite   │ ──────┐
   │ (config) │       │ SELECT
   └──────────┘       │
                      ▼
              ┌────────────────┐
              │ Config Loader  │
              │                │
              │ - lines        │
              │ - processes    │
              │ - PLCs         │
              │ - tags         │
              │ - polling_     │
              │   groups       │
              └───────┬────────┘
                      │
                      ▼
              ┌────────────────┐
              │ Polling Engine │
              │ (메모리에 로드) │
              └────────────────┘

2. 폴링 실행 중 데이터 흐름
   ┌────────┐
   │  PLC   │
   └───┬────┘
       │ MC 3E ASCII
       │ (배치 읽기)
       ▼
   ┌────────────────┐
   │ Polling Worker │
   │                │
   │ raw_value →    │
   │ scaled_value   │
   │ (scale 적용)   │
   └───────┬────────┘
           │
           │ DataPoint 객체
           ▼
   ┌────────────────┐
   │ Thread-Safe    │
   │ Data Buffer    │
   │ (Queue)        │
   └───────┬────────┘
           │
           │ Batch (1000개)
           ▼
   ┌────────────────┐
   │ Oracle DB      │
   │ Writer Thread  │
   │                │
   │ - 비트 폴링    │
   │   결과 INSERT  │
   │ - 알람/상태    │
   │   INSERT       │
   └───────┬────────┘
           │
           │ INSERT
           ▼
   ┌────────────────┐
   │ Oracle DB      │
   │                │
   │ - SCADA_BIT_   │
   │   POLLING      │
   │ - SCADA_ALARM_ │
   │   STATUS       │
   └────────────────┘

3. 웹 UI에서 설정 변경
   ┌──────────────┐
   │ Next.js      │
   │ 관리 웹      │
   └──────┬───────┘
          │ HTTP POST
          │ (태그 추가)
          ▼
   ┌──────────────┐
   │ FastAPI      │
   │ REST API     │
   └──────┬───────┘
          │ INSERT
          ▼
   ┌──────────────┐
   │ SQLite       │
   │ (tags 테이블)│
   └──────────────┘
```

---

## 3.7 데이터베이스 유틸리티

### 3.7.1 CSV에서 태그 일괄 등록

```python
# backend/scripts/import_tags_from_csv.py

import csv
import sqlite3

def import_tags_from_csv(csv_file_path):
    """
    CSV 파일에서 태그를 일괄 등록

    CSV 형식:
    PLC_CODE,TAG_ADDRESS,TAG_NAME,TAG_UNIT,TAG_SCALE,MACHINE_CODE,POLLING_GROUP_ID
    """
    conn = sqlite3.connect('./config/scada.db')
    cursor = conn.cursor()

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # PLC ID 조회
            cursor.execute("SELECT id FROM plc_connections WHERE plc_code = ?", (row['PLC_CODE'],))
            plc_id = cursor.fetchone()[0]

            # Process ID 조회
            cursor.execute("SELECT id FROM processes WHERE process_code = ?", (row['MACHINE_CODE'],))
            process_id = cursor.fetchone()[0]

            # 태그 INSERT
            cursor.execute("""
                INSERT INTO tags (
                    plc_id,
                    process_id,
                    tag_address,
                    tag_name,
                    unit,
                    scale,
                    machine_code,
                    polling_group_id,
                    enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plc_id,
                process_id,
                row['TAG_ADDRESS'],
                row['TAG_NAME'],
                row['TAG_UNIT'],
                float(row['TAG_SCALE']),
                row['MACHINE_CODE'],
                int(row['POLLING_GROUP_ID']),
                1
            ))

    conn.commit()
    conn.close()

    print(f"Imported tags from {csv_file_path}")

if __name__ == '__main__':
    import_tags_from_csv('./data/tags.csv')
```

---

## 3.8 쿼리 성능 최적화

### 3.8.1 SQLite 인덱스 전략

```sql
-- 자주 조회되는 컬럼에 인덱스 생성

-- 1. PLC 코드로 태그 조회 (자주 사용)
CREATE INDEX idx_tags_plc ON tags(plc_id);

-- 2. 폴링 그룹별 태그 조회 (폴링 엔진에서 사용)
CREATE INDEX idx_tags_polling_group ON tags(polling_group_id);

-- 3. 활성화된 폴링 그룹만 조회 (폴링 엔진에서 사용)
CREATE INDEX idx_polling_groups_enabled ON polling_groups(enabled);

-- 4. 태그 주소로 빠른 검색
CREATE INDEX idx_tags_address ON tags(tag_address);
```

---

### 3.8.2 Oracle 배치 INSERT 최적화

```python
# src/database/oracle_writer.py

def _batch_insert_optimized(self, batch):
    """
    최적화된 배치 INSERT (executemany 사용)
    """
    cursor = self.connection.cursor()

    try:
        # 데이터 준비
        rows = [
            (
                dp['plc_code'],
                dp['machine_code'],
                dp['tag_address'],
                str(dp['value']),
                dp['timestamp'].strftime('%Y%m%d%H%M%S'),
                dp['timestamp'],
                dp['tag_name']
            )
            for dp in batch
        ]

        # executemany로 배치 INSERT (빠름)
        cursor.executemany(f"""
            INSERT INTO {self.table_bit} (
                PLC_CODE, MACHINE_CODE, TAG_ADDRESS, TAG_VALUE,
                MACHINE_DATETIME, PLC_TIMESTAMP, COMMENTS,
                ENTER_DATE, ENTER_BY, ORGANIZATION_ID
            ) VALUES (
                :1, :2, :3, :4, :5, :6, :7,
                SYSDATE, 'SCADA', 1
            )
        """, rows)

        self.connection.commit()

    except Exception as e:
        self.connection.rollback()
        raise

    finally:
        cursor.close()
```

---

## 문서 이력

| 버전 | 일자 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | 2025-10-30 | Claude | 최초 작성 |

---

**이전 문서**: [02-SYSTEM-ARCHITECTURE.md](./02-SYSTEM-ARCHITECTURE.md)
**다음 문서**: [04-PYTHON-BACKEND-SPEC.md](./04-PYTHON-BACKEND-SPEC.md)
