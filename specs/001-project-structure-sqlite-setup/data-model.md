# Data Model: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정

**Feature**: 001-project-structure-sqlite-setup
**Date**: 2025-10-31
**Database**: SQLite 3.40+

## Entity Relationship Diagram

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

## Entities

### 1. Line (라인)

**Purpose**: 생산 라인 정보 관리

**Attributes**:
| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 자동 증가 ID |
| line_code | VARCHAR(50) | UNIQUE, NOT NULL | 라인 코드 (예: 'LINE01') |
| line_name | VARCHAR(200) | NOT NULL | 라인 명 (예: 'TUB 가공 라인') |
| location | VARCHAR(100) | NULL | 위치 (예: '창원 공장') |
| enabled | BOOLEAN | DEFAULT 1 | 활성화 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 일시 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 일시 |

**Relationships**:
- One-to-Many with Process: 하나의 라인은 여러 공정을 포함

**Business Rules**:
- line_code는 고유해야 함
- 라인 삭제 시 연결된 모든 공정, PLC, 태그가 CASCADE 삭제

**Sample Data**:
```sql
INSERT INTO lines (line_code, line_name, location, enabled) VALUES
('LINE01', 'TUB 가공 라인', '창원 공장', 1);
```

---

### 2. Process (공정)

**Purpose**: 생산 공정 및 설비 정보 관리

**Attributes**:
| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 자동 증가 ID |
| line_id | INTEGER | FOREIGN KEY(lines.id), NOT NULL | 라인 ID |
| process_sequence | INTEGER | NOT NULL | 공정 순서 (1, 2, 3, ...) |
| process_code | VARCHAR(50) | UNIQUE, NOT NULL | 14자리 설비 코드 (예: 'KRCWO12ELOA101') |
| process_name | VARCHAR(200) | NOT NULL | 공정 명 (예: 'Upper Loading') |
| equipment_type | VARCHAR(10) | NULL | 설비 타입 (예: 'LOA', 'WEM', 'DRY') |
| enabled | BOOLEAN | DEFAULT 1 | 활성화 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 일시 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 일시 |

**Relationships**:
- Many-to-One with Line: 여러 공정이 하나의 라인에 속함
- One-to-Many with PLCConnection: 하나의 공정은 여러 PLC를 포함

**Business Rules**:
- process_code는 14자리 형식: KRCWO12ELOA101
  - KR (국가) + CWO (공장) + 12 (라인) + ELO (설비타입) + A (구분) + 101 (번호)
- 공정 삭제 시 연결된 모든 PLC와 태그가 CASCADE 삭제

**Validation**:
```python
import re

PROCESS_CODE_PATTERN = r'^[A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}$'

def validate_process_code(code: str) -> bool:
    return bool(re.match(PROCESS_CODE_PATTERN, code)) and len(code) == 14
```

---

### 3. PLCConnection (PLC 연결)

**Purpose**: PLC 연결 정보 및 통신 설정 관리

**Attributes**:
| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 자동 증가 ID |
| process_id | INTEGER | FOREIGN KEY(processes.id), NOT NULL | 공정 ID |
| plc_code | VARCHAR(50) | UNIQUE, NOT NULL | PLC 코드 (예: 'PLC01') |
| ip_address | VARCHAR(50) | NOT NULL | PLC IP 주소 (예: '192.168.1.10') |
| port | INTEGER | DEFAULT 5000 | PLC 포트 번호 |
| network_no | INTEGER | DEFAULT 0 | MC 프로토콜 네트워크 번호 |
| station_no | INTEGER | DEFAULT 0 | MC 프로토콜 스테이션 번호 |
| enabled | BOOLEAN | DEFAULT 1 | 활성화 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 일시 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 일시 |

**Relationships**:
- Many-to-One with Process: 여러 PLC가 하나의 공정에 속함
- One-to-Many with Tag: 하나의 PLC는 여러 태그를 포함

**Business Rules**:
- plc_code는 고유해야 함
- ip_address는 유효한 IPv4 형식
- PLC 삭제 시 연결된 모든 태그가 CASCADE 삭제

**Validation**:
```python
import ipaddress

def validate_ip_address(ip: str) -> bool:
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False
```

---

### 4. Tag (태그)

**Purpose**: PLC 메모리 주소와 연결된 데이터 포인트 정보 관리

**Attributes**:
| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 자동 증가 ID |
| plc_id | INTEGER | FOREIGN KEY(plc_connections.id), NOT NULL | PLC ID |
| process_id | INTEGER | FOREIGN KEY(processes.id), NOT NULL | 공정 ID |
| tag_address | VARCHAR(20) | NOT NULL | TAG 주소 (예: 'W150', 'M100') |
| tag_name | VARCHAR(200) | NOT NULL | TAG 명 (예: 'Upper셔틀#1 유효부하') |
| tag_division | VARCHAR(50) | NULL | TAG 구분 (예: '부하율', '전류치') |
| data_type | VARCHAR(20) | DEFAULT 'WORD' | 데이터 타입 (WORD, DWORD, BIT 등) |
| unit | VARCHAR(20) | NULL | 단위 (예: '%', 'A', '℃') |
| scale | DECIMAL(10, 4) | DEFAULT 1.0 | 스케일 팩터 (예: 0.1, 1.0) |
| machine_code | VARCHAR(200) | NULL | 설비 코드 (KRCWO12ELOA101) |
| polling_group_id | INTEGER | FOREIGN KEY(polling_groups.id), NULL | 폴링 그룹 ID |
| enabled | BOOLEAN | DEFAULT 1 | 활성화 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 일시 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 일시 |

**Relationships**:
- Many-to-One with PLCConnection: 여러 태그가 하나의 PLC에 속함
- Many-to-One with Process: 여러 태그가 하나의 공정에 속함
- Many-to-One with PollingGroup: 여러 태그가 하나의 폴링 그룹에 선택적으로 속함

**Business Rules**:
- tag_address는 PLC 메모리 주소 (예: W150, M100, D200)
- scale은 원시 값에 곱해지는 계수
- polling_group_id는 NULL 가능 (미할당 태그)
- 폴링 그룹 삭제 시 polling_group_id는 NULL로 설정 (SET NULL)

**Indexes**:
```sql
CREATE INDEX idx_tags_plc ON tags(plc_id);
CREATE INDEX idx_tags_process ON tags(process_id);
CREATE INDEX idx_tags_polling_group ON tags(polling_group_id);
CREATE INDEX idx_tags_address ON tags(tag_address);
```

---

### 5. PollingGroup (폴링 그룹)

**Purpose**: 동일한 폴링 설정을 공유하는 태그들의 논리적 그룹 관리

**Attributes**:
| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 자동 증가 ID |
| group_name | VARCHAR(200) | NOT NULL | 그룹 명 (예: 'Upper Loading - 부하율') |
| line_code | VARCHAR(50) | NULL | 라인 코드 |
| process_code | VARCHAR(50) | NULL | 공정 코드 |
| plc_id | INTEGER | FOREIGN KEY(plc_connections.id), NOT NULL | PLC ID |
| mode | VARCHAR(20) | DEFAULT 'FIXED' | 폴링 모드 (FIXED, HANDSHAKE) |
| interval_ms | INTEGER | DEFAULT 1000 | 폴링 간격 (밀리초) |
| trigger_bit_address | VARCHAR(20) | NULL | 트리거 비트 주소 (예: 'B0110') |
| trigger_bit_offset | INTEGER | DEFAULT 0 | 트리거 비트 오프셋 (0~15) |
| auto_reset_trigger | BOOLEAN | DEFAULT 1 | 자동 트리거 리셋 여부 |
| priority | VARCHAR(20) | DEFAULT 'NORMAL' | 우선순위 (HIGH, NORMAL, LOW) |
| enabled | BOOLEAN | DEFAULT 1 | 활성화 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 일시 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 일시 |

**Relationships**:
- Many-to-One with PLCConnection: 여러 폴링 그룹이 하나의 PLC에 속함
- One-to-Many with Tag: 하나의 폴링 그룹은 여러 태그를 포함

**Business Rules**:
- mode는 'FIXED' 또는 'HANDSHAKE'
- FIXED 모드: interval_ms 마다 주기적 폴링
- HANDSHAKE 모드: trigger_bit_address 비트가 1일 때만 폴링
- trigger_bit_address는 HANDSHAKE 모드에서 필수

**Validation**:
```python
def validate_polling_group(group: dict) -> bool:
    if group['mode'] == 'HANDSHAKE':
        return group['trigger_bit_address'] is not None
    return True
```

---

## Database Schema SQL

### Table Creation

```sql
-- Enable Foreign Key constraints
PRAGMA foreign_keys = ON;

-- 1. Lines table
CREATE TABLE lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_code VARCHAR(50) UNIQUE NOT NULL,
    line_name VARCHAR(200) NOT NULL,
    location VARCHAR(100),
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lines_code ON lines(line_code);

-- 2. Processes table
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id INTEGER NOT NULL,
    process_sequence INTEGER NOT NULL,
    process_code VARCHAR(50) UNIQUE NOT NULL,
    process_name VARCHAR(200) NOT NULL,
    equipment_type VARCHAR(10),
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_id) REFERENCES lines(id) ON DELETE CASCADE
);

CREATE INDEX idx_processes_line ON processes(line_id);
CREATE INDEX idx_processes_code ON processes(process_code);

-- 3. PLC Connections table
CREATE TABLE plc_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    plc_code VARCHAR(50) UNIQUE NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    port INTEGER DEFAULT 5000,
    network_no INTEGER DEFAULT 0,
    station_no INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

CREATE INDEX idx_plc_process ON plc_connections(process_id);
CREATE INDEX idx_plc_code ON plc_connections(plc_code);

-- 4. Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,
    process_id INTEGER NOT NULL,
    tag_address VARCHAR(20) NOT NULL,
    tag_name VARCHAR(200) NOT NULL,
    tag_division VARCHAR(50),
    data_type VARCHAR(20) DEFAULT 'WORD',
    unit VARCHAR(20),
    scale DECIMAL(10, 4) DEFAULT 1.0,
    machine_code VARCHAR(200),
    polling_group_id INTEGER,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL
);

CREATE INDEX idx_tags_plc ON tags(plc_id);
CREATE INDEX idx_tags_process ON tags(process_id);
CREATE INDEX idx_tags_polling_group ON tags(polling_group_id);
CREATE INDEX idx_tags_address ON tags(tag_address);

-- 5. Polling Groups table
CREATE TABLE polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(200) NOT NULL,
    line_code VARCHAR(50),
    process_code VARCHAR(50),
    plc_id INTEGER NOT NULL,
    mode VARCHAR(20) DEFAULT 'FIXED',
    interval_ms INTEGER DEFAULT 1000,
    trigger_bit_address VARCHAR(20),
    trigger_bit_offset INTEGER DEFAULT 0,
    auto_reset_trigger BOOLEAN DEFAULT 1,
    priority VARCHAR(20) DEFAULT 'NORMAL',
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE
);

CREATE INDEX idx_polling_groups_plc ON polling_groups(plc_id);
CREATE INDEX idx_polling_groups_enabled ON polling_groups(enabled);
```

---

## Views

### v_tags_with_plc

태그 정보와 PLC 정보를 조인한 뷰

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

## Data Integrity Rules

### CASCADE Deletion Rules

1. **Line → Process → PLC → Tag**
   - 라인 삭제 시: 모든 공정, PLC, 태그 자동 삭제
   - 공정 삭제 시: 모든 PLC, 태그 자동 삭제
   - PLC 삭제 시: 모든 태그 자동 삭제

2. **PollingGroup → Tag**
   - 폴링 그룹 삭제 시: 태그는 유지, polling_group_id만 NULL로 설정

### Validation Rules

1. **process_code**: 14자리 형식 (정규표현식 검증)
2. **ip_address**: 유효한 IPv4 주소
3. **mode**: 'FIXED' 또는 'HANDSHAKE'만 허용
4. **interval_ms**: 양수 값 (최소 100ms 권장)

---

## Migration Strategy

초기 버전이므로 마이그레이션 불필요. 향후 스키마 변경 시:

1. 백업: `cp scada.db scada_backup_YYYYMMDD.db`
2. ALTER TABLE 실행
3. 데이터 검증
4. 문제 발생 시 백업 복구

---

## Performance Considerations

- **Expected Load**: 초기 3,491개 태그, 최대 10,000개 태그
- **Query Performance**: 인덱스로 100ms 이내 응답 목표
- **File Size**: 초기 50MB 이하, 최대 200MB 예상
- **Concurrent Access**: 읽기는 다중 접근 가능, 쓰기는 순차 처리

---

## Sample Data

### 초기 테스트 데이터

```sql
-- Line
INSERT INTO lines (line_code, line_name, location, enabled) VALUES
('LINE01', 'TUB 가공 라인', '창원 공장', 1);

-- Processes
INSERT INTO processes (line_id, process_sequence, process_code, process_name, equipment_type, enabled) VALUES
(1, 1, 'KRCWO12ELOA101', 'Upper Loading', 'LOA', 1),
(1, 2, 'KRCWO12EWEM102', 'Welding Machine 1', 'WEM', 1);

-- PLC Connections
INSERT INTO plc_connections (process_id, plc_code, ip_address, port, network_no, station_no, enabled) VALUES
(1, 'PLC01', '192.168.1.10', 5000, 0, 0, 1),
(2, 'PLC02', '192.168.1.11', 5000, 0, 0, 1);

-- Polling Groups
INSERT INTO polling_groups (group_name, line_code, process_code, plc_id, mode, interval_ms, trigger_bit_address, trigger_bit_offset, auto_reset_trigger, enabled) VALUES
('Upper Loading - 핸드셰이크', 'LINE01', 'KRCWO12ELOA101', 1, 'HANDSHAKE', 500, 'B0110', 0, 1, 1),
('Welding - 고정 간격', 'LINE01', 'KRCWO12EWEM102', 2, 'FIXED', 1000, NULL, NULL, 0, 1);

-- Tags
INSERT INTO tags (plc_id, process_id, tag_address, tag_name, tag_division, data_type, unit, scale, machine_code, polling_group_id, enabled) VALUES
(1, 1, 'W150', 'Upper셔틀#1 유효부하', '부하율', 'WORD', '%', 1.0, 'KRCWO12ELOA101', 1, 1),
(1, 1, 'W151', 'Upper셔틀#2 유효부하', '부하율', 'WORD', '%', 1.0, 'KRCWO12ELOA101', 1, 1),
(1, 1, 'W152', 'Upper샤프트모터 전류치', '전류치', 'WORD', 'A', 0.1, 'KRCWO12ELOA101', 1, 1);
```
