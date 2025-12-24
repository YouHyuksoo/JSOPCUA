-- Equipment Positions Table
-- 설비 박스 위치 정보 저장 (모니터링 화면용)

CREATE TABLE IF NOT EXISTS equipment_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_code VARCHAR(14) NOT NULL,                    -- 설비 코드 (FK to processes.process_code)
    layout_name VARCHAR(50) NOT NULL DEFAULT 'default',    -- 레이아웃 이름 (여러 레이아웃 지원)
    position_x REAL NOT NULL DEFAULT 0,                     -- X 좌표 (픽셀 또는 퍼센트)
    position_y REAL NOT NULL DEFAULT 0,                     -- Y 좌표 (픽셀 또는 퍼센트)
    width REAL DEFAULT 120,                                -- 박스 너비 (픽셀)
    height REAL DEFAULT 80,                                -- 박스 높이 (픽셀)
    z_index INTEGER DEFAULT 1,                             -- z-index (겹침 순서)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_code) REFERENCES processes(process_code) ON DELETE CASCADE,
    UNIQUE(process_code, layout_name)                      -- 설비당 레이아웃당 하나의 위치
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_equipment_positions_process_code ON equipment_positions(process_code);
CREATE INDEX IF NOT EXISTS idx_equipment_positions_layout ON equipment_positions(layout_name);

