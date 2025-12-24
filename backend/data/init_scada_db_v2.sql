-- JSScada SQLite Database Schema V2
-- 스키마 재설계: PLC와 공정을 독립적으로 분리, Tags가 중심 연결 테이블
-- 4개 핵심 테이블: plc_connections, processes, tags, alarm_masters

-- Enable Foreign Key support
PRAGMA foreign_keys = ON;

-- =============================================================================
-- Table: plc_connections (PLC 마스터 - 독립 테이블)
-- =============================================================================
CREATE TABLE IF NOT EXISTS plc_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_code VARCHAR(20) NOT NULL UNIQUE,               -- "PLC01", "PLC02", "PLC03"
    plc_name VARCHAR(100) NOT NULL,                     -- "메인 CPU PLC"
    ip_address VARCHAR(45) NOT NULL,                    -- "192.168.1.10"
    port INTEGER NOT NULL DEFAULT 5010,
    protocol VARCHAR(20) NOT NULL DEFAULT 'MC_3E_ASCII',
    network_no INTEGER DEFAULT 0,                       -- MC 프로토콜 네트워크 번호
    station_no INTEGER DEFAULT 0,                       -- MC 프로토콜 국번
    connection_timeout INTEGER DEFAULT 5,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Table: processes (공정/설비 마스터 - 독립 테이블)
-- 14자리 설비 코드 지원: KRCWO12ELOA101
-- =============================================================================
CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_code VARCHAR(14) NOT NULL UNIQUE,           -- "KRCWO12ELOA101" (14자리)
    process_name VARCHAR(100) NOT NULL,                 -- "엘레베이터 A 공정"
    location VARCHAR(100),                              -- "1동 2층"
    sequence_order INTEGER DEFAULT 0,                   -- 공정 순서
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Table: polling_groups (폴링 그룹)
-- FIXED: 고정 주기 폴링, HANDSHAKE: 핸드셰이크 모드
-- =============================================================================
CREATE TABLE IF NOT EXISTS polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(50) NOT NULL UNIQUE,
    plc_id INTEGER NOT NULL,                            -- FK to plc_connections
    polling_mode VARCHAR(20) NOT NULL CHECK(polling_mode IN ('FIXED', 'HANDSHAKE')),
    polling_interval_ms INTEGER NOT NULL DEFAULT 1000,
    group_category VARCHAR(20) NOT NULL DEFAULT 'OPERATION' CHECK(group_category IN ('OPERATION', 'STATE', 'ALARM')),  -- Oracle 테이블 구분
    trigger_bit_address VARCHAR(20),                    -- HANDSHAKE 모드 트리거 주소
    trigger_bit_offset INTEGER DEFAULT 0,
    auto_reset_trigger BOOLEAN DEFAULT 1,
    priority VARCHAR(20) DEFAULT 'NORMAL',              -- "HIGH", "NORMAL", "LOW"
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE
);

-- =============================================================================
-- Table: tags (태그 마스터 - PLC + 공정 연결 중심 테이블)
-- 최대 3,491개 태그 지원
-- =============================================================================
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,                            -- FK to plc_connections
    process_id INTEGER NOT NULL,                        -- FK to processes
    tag_address VARCHAR(50) NOT NULL,                   -- "D100", "W200", "M100"
    tag_name VARCHAR(100) NOT NULL,                     -- "엘레베이터 A 온도"
    tag_type VARCHAR(20) NOT NULL DEFAULT 'INT',        -- "INT", "FLOAT", "BIT", "DWORD"
    unit VARCHAR(20),                                   -- "℃", "bar", "rpm"
    scale REAL DEFAULT 1.0,                             -- 스케일 배율
    offset REAL DEFAULT 0.0,                            -- 오프셋
    min_value REAL,                                     -- 최소값
    max_value REAL,                                     -- 최대값
    polling_group_id INTEGER,                           -- FK to polling_groups (NULL 허용)
    log_mode VARCHAR(20) NOT NULL DEFAULT 'ALWAYS' CHECK(log_mode IN ('ALWAYS', 'ON_CHANGE', 'NEVER')),  -- 로그 저장 방식
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_value TEXT,                                    -- 마지막 폴링값
    last_updated_at TIMESTAMP,                          -- 마지막 업데이트 시각
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL,
    UNIQUE(plc_id, tag_address)                         -- PLC + 주소 = 유일키
);

-- =============================================================================
-- Table: alarm_masters (알람 마스터)
-- M 주소 알람 정의 관리
-- =============================================================================
CREATE TABLE IF NOT EXISTS alarm_masters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,                            -- FK to plc_connections
    process_id INTEGER NOT NULL,                        -- FK to processes
    alarm_address VARCHAR(50) NOT NULL,                 -- "M100", "M101", "M102"
    alarm_code VARCHAR(50) NOT NULL UNIQUE,             -- "ALM_OVERHEAT_01"
    alarm_message VARCHAR(200) NOT NULL,                -- "과열 알람 발생"
    alarm_description TEXT,                             -- 상세 설명
    severity VARCHAR(20) NOT NULL DEFAULT 'WARNING',    -- "INFO", "WARNING", "ERROR", "CRITICAL"
    action_guide TEXT,                                  -- 조치 가이드
    polling_group_id INTEGER,                           -- FK to polling_groups (알람 폴링 그룹)
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL,
    UNIQUE(plc_id, alarm_address)                       -- PLC + 알람주소 = 유일키
);

-- =============================================================================
-- Indexes (성능 최적화)
-- =============================================================================

-- PLC Connections
CREATE INDEX IF NOT EXISTS idx_plc_code ON plc_connections(plc_code);
CREATE INDEX IF NOT EXISTS idx_plc_active ON plc_connections(is_active);

-- Processes
CREATE INDEX IF NOT EXISTS idx_process_code ON processes(process_code);
CREATE INDEX IF NOT EXISTS idx_process_active ON processes(is_active);

-- Polling Groups
CREATE INDEX IF NOT EXISTS idx_polling_plc_id ON polling_groups(plc_id);
CREATE INDEX IF NOT EXISTS idx_polling_active ON polling_groups(is_active);

-- Tags
CREATE INDEX IF NOT EXISTS idx_tags_plc_id ON tags(plc_id);
CREATE INDEX IF NOT EXISTS idx_tags_process_id ON tags(process_id);
CREATE INDEX IF NOT EXISTS idx_tags_polling_group ON tags(polling_group_id);
CREATE INDEX IF NOT EXISTS idx_tags_active ON tags(is_active);
CREATE INDEX IF NOT EXISTS idx_tags_address ON tags(tag_address);

-- Alarm Masters
CREATE INDEX IF NOT EXISTS idx_alarm_plc_id ON alarm_masters(plc_id);
CREATE INDEX IF NOT EXISTS idx_alarm_process_id ON alarm_masters(process_id);
CREATE INDEX IF NOT EXISTS idx_alarm_polling_group ON alarm_masters(polling_group_id);
CREATE INDEX IF NOT EXISTS idx_alarm_severity ON alarm_masters(severity);
CREATE INDEX IF NOT EXISTS idx_alarm_active ON alarm_masters(is_active);
CREATE INDEX IF NOT EXISTS idx_alarm_code ON alarm_masters(alarm_code);

-- =============================================================================
-- View: v_tags_full (태그 전체 정보 조인 뷰)
-- =============================================================================
CREATE VIEW IF NOT EXISTS v_tags_full AS
SELECT
    t.id AS tag_id,
    t.tag_address,
    t.tag_name,
    t.tag_type,
    t.unit,
    t.scale,
    t.offset,
    t.is_active AS tag_active,
    t.last_value,
    t.last_updated_at,
    plc.id AS plc_id,
    plc.plc_code,
    plc.plc_name,
    plc.ip_address,
    plc.port,
    plc.is_active AS plc_active,
    p.id AS process_id,
    p.process_code,
    p.process_name,
    p.location AS process_location,
    pg.id AS polling_group_id,
    pg.group_name,
    pg.polling_mode,
    pg.polling_interval_ms
FROM tags t
INNER JOIN plc_connections plc ON t.plc_id = plc.id
INNER JOIN processes p ON t.process_id = p.id
LEFT JOIN polling_groups pg ON t.polling_group_id = pg.id;

-- =============================================================================
-- View: v_alarms_full (알람 전체 정보 조인 뷰)
-- =============================================================================
CREATE VIEW IF NOT EXISTS v_alarms_full AS
SELECT
    a.id AS alarm_id,
    a.alarm_address,
    a.alarm_code,
    a.alarm_message,
    a.alarm_description,
    a.severity,
    a.action_guide,
    a.is_active AS alarm_active,
    plc.id AS plc_id,
    plc.plc_code,
    plc.plc_name,
    plc.ip_address,
    p.id AS process_id,
    p.process_code,
    p.process_name,
    p.location AS process_location,
    pg.id AS polling_group_id,
    pg.group_name
FROM alarm_masters a
INNER JOIN plc_connections plc ON a.plc_id = plc.id
INNER JOIN processes p ON a.process_id = p.id
LEFT JOIN polling_groups pg ON a.polling_group_id = pg.id;

-- =============================================================================
-- Initial Data (기본 데이터는 create_sample_data.py에서 생성)
-- =============================================================================

-- 데이터베이스 초기화 완료
