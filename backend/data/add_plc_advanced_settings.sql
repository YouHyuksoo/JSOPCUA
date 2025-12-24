-- Add advanced PLC connection settings to plc_connections table
-- MELSEC, SSL/TLS, 네트워크, 소켓, 장치, 장치 블락 설정 추가

-- MELSEC 설정
ALTER TABLE plc_connections ADD COLUMN driver_version VARCHAR(10) DEFAULT 'V2';
ALTER TABLE plc_connections ADD COLUMN message_format VARCHAR(20) DEFAULT 'Binary';
ALTER TABLE plc_connections ADD COLUMN series VARCHAR(50) DEFAULT 'Q Series';

-- SSL/TLS 설정
ALTER TABLE plc_connections ADD COLUMN ssl_root_cert TEXT NULL;
ALTER TABLE plc_connections ADD COLUMN ssl_version VARCHAR(20) DEFAULT 'None';
ALTER TABLE plc_connections ADD COLUMN ssl_password VARCHAR(200) NULL;
ALTER TABLE plc_connections ADD COLUMN ssl_private_key TEXT NULL;
ALTER TABLE plc_connections ADD COLUMN ssl_certificate TEXT NULL;

-- 네트워크 설정
ALTER TABLE plc_connections ADD COLUMN local_address VARCHAR(50) NULL;
ALTER TABLE plc_connections ADD COLUMN network_type VARCHAR(10) DEFAULT 'tcp';

-- 소켓 설정
ALTER TABLE plc_connections ADD COLUMN keep_alive BOOLEAN DEFAULT 0;
ALTER TABLE plc_connections ADD COLUMN linger_time INTEGER DEFAULT -1;

-- 일반 설정
ALTER TABLE plc_connections ADD COLUMN description TEXT NULL;
ALTER TABLE plc_connections ADD COLUMN scan_time INTEGER DEFAULT 1000;

-- 장치 설정
ALTER TABLE plc_connections ADD COLUMN charset VARCHAR(20) DEFAULT 'UTF8';
ALTER TABLE plc_connections ADD COLUMN text_endian VARCHAR(20) DEFAULT 'None';

-- 장치 블락 설정
ALTER TABLE plc_connections ADD COLUMN unit_size VARCHAR(20) DEFAULT '16Bit';
ALTER TABLE plc_connections ADD COLUMN block_size INTEGER DEFAULT 64;

