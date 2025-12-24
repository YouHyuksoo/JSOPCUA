-- JSScada SQLite Database Schema
-- Feature 1: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정
-- 5개 테이블, 8개 인덱스, 1개 뷰

-- Enable Foreign Key support
PRAGMA foreign_keys = ON;

-- =============================================================================
-- Table: machines (생산 설비)
-- =============================================================================
CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_code VARCHAR(50) NOT NULL UNIQUE,
    machine_name VARCHAR(200) NOT NULL,
    location TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Table: processes (공정)
-- 14자리 설비 코드 지원: KRCWO12ELOA101
-- =============================================================================
CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id INTEGER NOT NULL,
    process_code VARCHAR(14) NOT NULL UNIQUE,
    process_name VARCHAR(100) NOT NULL,
    description TEXT,
    sequence_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE
);

-- =============================================================================
-- Table: plc_connections (PLC 연결)
-- =============================================================================
CREATE TABLE IF NOT EXISTS plc_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    plc_code VARCHAR(20) NOT NULL UNIQUE,
    plc_name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    port INTEGER NOT NULL DEFAULT 5010,
    protocol VARCHAR(20) NOT NULL DEFAULT 'MC_3E_ASCII',
    connection_timeout INTEGER DEFAULT 5,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- =============================================================================
-- Table: polling_groups (폴링 그룹)
-- FIXED: 고정 주기 폴링, HANDSHAKE: 핸드셰이크 모드
-- =============================================================================
CREATE TABLE IF NOT EXISTS polling_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(50) NOT NULL UNIQUE,
    polling_mode VARCHAR(20) NOT NULL CHECK(polling_mode IN ('FIXED', 'HANDSHAKE')),
    polling_interval_ms INTEGER NOT NULL DEFAULT 1000,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Table: tags (PLC 태그)
-- 최대 3,491개 태그 지원
-- =============================================================================
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plc_id INTEGER NOT NULL,
    polling_group_id INTEGER,
    tag_address VARCHAR(50) NOT NULL,
    tag_name VARCHAR(100) NOT NULL,
    tag_type VARCHAR(20) NOT NULL DEFAULT 'INT',
    unit VARCHAR(20),
    scale REAL DEFAULT 1.0,
    offset REAL DEFAULT 0.0,
    min_value REAL,
    max_value REAL,
    machine_code VARCHAR(14),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_value TEXT,
    last_updated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL,
    UNIQUE(plc_id, tag_address)
);

-- =============================================================================
-- Indexes (성능 최적화)
-- =============================================================================

-- Index 1: processes - machine_id 기반 조회
CREATE INDEX IF NOT EXISTS idx_processes_machine_id ON processes(machine_id);

-- Index 2: processes - process_code 기반 조회
CREATE INDEX IF NOT EXISTS idx_processes_code ON processes(process_code);

-- Index 3: plc_connections - process_id 기반 조회
CREATE INDEX IF NOT EXISTS idx_plc_process_id ON plc_connections(process_id);

-- Index 4: plc_connections - is_active 필터링
CREATE INDEX IF NOT EXISTS idx_plc_active ON plc_connections(is_active);

-- Index 5: tags - plc_id 기반 조회
CREATE INDEX IF NOT EXISTS idx_tags_plc_id ON tags(plc_id);

-- Index 6: tags - polling_group_id 기반 조회
CREATE INDEX IF NOT EXISTS idx_tags_polling_group ON tags(polling_group_id);

-- Index 7: tags - machine_code 기반 조회
CREATE INDEX IF NOT EXISTS idx_tags_machine_code ON tags(machine_code);

-- Index 8: tags - is_active 필터링
CREATE INDEX IF NOT EXISTS idx_tags_active ON tags(is_active);

-- =============================================================================
-- View: v_tags_with_plc (태그와 PLC 정보 조인 뷰)
-- =============================================================================
CREATE VIEW IF NOT EXISTS v_tags_with_plc AS
SELECT
    t.id AS tag_id,
    t.tag_address,
    t.tag_name,
    t.tag_type,
    t.unit,
    t.scale,
    t.offset,
    t.machine_code,
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
    m.id AS machine_id,
    m.machine_code,
    m.machine_name,
    pg.id AS polling_group_id,
    pg.group_name,
    pg.polling_mode,
    pg.polling_interval_ms
FROM tags t
INNER JOIN plc_connections plc ON t.plc_id = plc.id
INNER JOIN processes p ON plc.process_id = p.id
INNER JOIN machines m ON p.machine_id = m.id
LEFT JOIN polling_groups pg ON t.polling_group_id = pg.id;

-- =============================================================================
-- Initial Data (기본 데이터는 create_sample_data.py에서 생성)
-- =============================================================================

-- 데이터베이스 초기화 완료
