-- Add tag mapping fields to equipment_positions table
-- 설비 박스 위치 정보에 PLC 태그 매핑 필드 추가

-- 태그 ID 참조 (tags 테이블의 id)
ALTER TABLE equipment_positions ADD COLUMN tag_id INTEGER NULL;

-- 태그 주소 직접 지정 (예: "D100", "W150")
ALTER TABLE equipment_positions ADD COLUMN tag_address VARCHAR(20) NULL;

-- PLC 코드 (plc_connections 테이블의 plc_code)
ALTER TABLE equipment_positions ADD COLUMN plc_code VARCHAR(50) NULL;

-- 설비 코드 (machine_code, tags 테이블의 machine_code와 매칭)
ALTER TABLE equipment_positions ADD COLUMN machine_code VARCHAR(200) NULL;

-- 인덱스 추가 (태그 매핑 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_equipment_positions_tag_id ON equipment_positions(tag_id);
CREATE INDEX IF NOT EXISTS idx_equipment_positions_tag_address ON equipment_positions(tag_address, plc_code);
CREATE INDEX IF NOT EXISTS idx_equipment_positions_machine_code ON equipment_positions(machine_code);

-- 주석: tag_id 또는 (tag_address + plc_code) 중 하나를 사용하여 태그를 매핑할 수 있습니다.
-- machine_code는 태그와 설비를 매칭하는 데 사용됩니다.

