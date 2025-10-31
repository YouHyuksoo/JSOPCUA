# Feature Specification: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정

**Feature Branch**: `001-project-structure-sqlite-setup`
**Created**: 2025-10-31
**Status**: Draft
**Input**: User description: "프로젝트 기본 구조 및 SQLite 데이터베이스 설정: JSScada 시스템의 기본 디렉토리 구조 생성 및 SQLite 로컬 데이터베이스 스키마 구축. 라인(lines), 공정(processes), PLC 연결(plc_connections), 태그(tags), 폴링 그룹(polling_groups) 테이블 생성. 14자리 설비 코드 체계 지원(예: KRCWO12ELOA101). 3,491개 태그를 지원하는 마스터 데이터 구조. CSV 일괄 등록 기능 포함. 백엔드는 Python 3.11+, 프론트엔드는 Next.js 14+, SQLite 3.40+ 사용. backend/, frontend-admin/, frontend-monitor/ 디렉토리 구조."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 프로젝트 디렉토리 구조 생성 (Priority: P1)

시스템 관리자는 JSScada 시스템 개발을 시작하기 위해 표준화된 프로젝트 디렉토리 구조가 필요합니다. backend/ (Python SCADA 백엔드), frontend-admin/ (관리 웹), frontend-monitor/ (모니터링 웹) 3개의 주요 디렉토리와 각각의 하위 구조가 생성되어야 합니다.

**Why this priority**: 모든 개발 작업의 기반이 되는 구조이며, 이 구조 없이는 다른 기능을 개발할 수 없습니다. 팀 전체가 동일한 구조에서 작업하여 일관성을 유지할 수 있습니다.

**Independent Test**: 프로젝트 루트에서 필수 디렉토리들의 존재를 확인하고, 각 디렉토리 내부에 기본 설정 파일들이 있는지 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 빈 프로젝트 저장소, **When** 프로젝트 구조를 초기화, **Then** backend/, frontend-admin/, frontend-monitor/, docs/ 디렉토리가 생성됨
2. **Given** 생성된 backend/ 디렉토리, **When** 디렉토리 내용을 확인, **Then** src/, config/, logs/, tests/ 하위 디렉토리가 존재
3. **Given** 생성된 프로젝트 구조, **When** 각 프론트엔드 디렉토리를 확인, **Then** Next.js 프로젝트 기본 구조(app/, components/, lib/) 존재

---

### User Story 2 - SQLite 데이터베이스 스키마 생성 (Priority: P1)

시스템 관리자는 SCADA 설정 정보를 저장하기 위해 로컬 SQLite 데이터베이스가 필요합니다. 라인, 공정, PLC 연결, 태그, 폴링 그룹 정보를 저장할 수 있는 테이블 구조가 구축되어야 합니다.

**Why this priority**: SCADA 시스템의 모든 설정 정보가 저장되는 핵심 데이터 저장소입니다. 이 스키마가 없으면 어떤 설정도 저장하거나 불러올 수 없습니다.

**Independent Test**: SQLite 데이터베이스 파일을 생성하고, 필수 테이블(lines, processes, plc_connections, tags, polling_groups)이 올바른 스키마로 생성되었는지 쿼리로 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** backend/config/ 디렉토리, **When** 데이터베이스 초기화 스크립트 실행, **Then** scada.db 파일이 생성됨
2. **Given** 생성된 scada.db, **When** 테이블 목록을 조회, **Then** lines, processes, plc_connections, tags, polling_groups 테이블이 존재
3. **Given** lines 테이블, **When** 테이블 스키마를 확인, **Then** id, line_code, line_name, location, enabled, created_at, updated_at 컬럼이 존재
4. **Given** processes 테이블, **When** 14자리 설비 코드 형식(예: KRCWO12ELOA101) 데이터 삽입, **Then** 데이터가 정상적으로 저장됨
5. **Given** tags 테이블, **When** 테이블 구조를 확인, **Then** 3,491개 이상의 태그를 저장할 수 있는 충분한 용량과 인덱스 보유

---

### User Story 3 - 데이터베이스 관계 및 제약 조건 설정 (Priority: P2)

시스템 관리자는 데이터 무결성을 보장하기 위해 테이블 간의 관계와 제약 조건이 필요합니다. Foreign Key를 통해 라인-공정-PLC-태그-폴링그룹 간의 계층적 관계가 유지되어야 합니다.

**Why this priority**: 데이터 무결성은 중요하지만, 기본 스키마가 있으면 먼저 개발을 시작할 수 있습니다. 제약 조건은 이후에도 추가 가능합니다.

**Independent Test**: 부모 레코드 없이 자식 레코드를 삽입하려고 시도하여 Foreign Key 제약이 작동하는지, CASCADE 삭제가 올바르게 동작하는지 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 공정(process) 레코드 없음, **When** PLC 연결 레코드를 삽입 시도, **Then** Foreign Key 제약 위반 오류 발생
2. **Given** 라인 레코드가 존재, **When** 라인을 삭제, **Then** CASCADE로 연결된 모든 공정, PLC, 태그 레코드도 자동 삭제
3. **Given** 폴링 그룹에 연결된 태그들, **When** 폴링 그룹을 삭제, **Then** 태그의 polling_group_id가 NULL로 설정(SET NULL)

---

### User Story 4 - CSV 일괄 태그 등록 기능 (Priority: P2)

시스템 관리자는 3,491개의 태그를 효율적으로 등록하기 위해 CSV 파일에서 태그 정보를 일괄 가져오는 기능이 필요합니다.

**Why this priority**: 수동으로 태그를 하나씩 입력하는 것은 비현실적이므로 대량 데이터 입력 기능이 필요합니다. 하지만 기본 스키마가 먼저 준비되어야 합니다.

**Independent Test**: 샘플 CSV 파일을 준비하고, 가져오기 스크립트를 실행하여 모든 태그가 올바르게 데이터베이스에 삽입되었는지 확인할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 태그 정보가 담긴 CSV 파일(PLC_CODE, TAG_ADDRESS, TAG_NAME, UNIT, SCALE, MACHINE_CODE 포함), **When** CSV 가져오기 스크립트 실행, **Then** 모든 태그가 tags 테이블에 삽입됨
2. **Given** 3,491개 태그가 담긴 CSV 파일, **When** 일괄 가져오기 실행, **Then** 5분 이내에 모든 태그가 등록 완료
3. **Given** 중복된 TAG_ADDRESS를 가진 CSV 파일, **When** 가져오기 실행, **Then** 중복 키 오류를 기록하고 유효한 태그만 삽입

---

### User Story 5 - 데이터베이스 초기 데이터 설정 (Priority: P3)

시스템 관리자는 개발 및 테스트를 위해 샘플 라인, 공정, PLC 연결 정보가 미리 입력된 데이터베이스가 필요합니다.

**Why this priority**: 초기 데이터는 개발 편의를 위한 것으로, 실제 운영 데이터는 관리 웹이나 CSV로 나중에 입력할 수 있습니다.

**Independent Test**: 데이터베이스를 초기화하고, 샘플 데이터(최소 1개 라인, 2개 공정, 2개 PLC, 10개 태그, 2개 폴링 그룹)가 존재하는지 확인할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 빈 데이터베이스, **When** 초기 데이터 삽입 스크립트 실행, **Then** 최소 1개의 라인("TUB 가공 라인") 생성
2. **Given** 초기화된 데이터베이스, **When** 폴링 그룹 조회, **Then** FIXED 모드와 HANDSHAKE 모드 샘플 그룹이 각각 1개씩 존재
3. **Given** 초기 데이터가 삽입된 상태, **When** 태그를 폴링 그룹별로 조회, **Then** 각 폴링 그룹에 최소 5개의 태그가 할당됨

---

### Edge Cases

- **빈 CSV 파일 처리**: CSV 파일이 헤더만 있고 데이터가 없을 때, 오류 없이 0건 처리 완료 메시지 출력
- **잘못된 CSV 형식**: 필수 컬럼이 누락된 CSV 파일을 가져올 때, 명확한 오류 메시지와 함께 가져오기 중단
- **데이터베이스 파일 손상**: scada.db 파일이 손상되었을 때, 백업에서 복구하거나 재생성하는 방법 제공
- **디스크 용량 부족**: 데이터베이스 생성 중 디스크 용량 부족 시, 명확한 오류 메시지 출력
- **동시 접근**: 여러 프로세스가 동시에 SQLite 데이터베이스에 접근할 때, 락킹 처리로 데이터 손상 방지
- **특수 문자 처리**: 태그명에 한글, 특수문자(%, °C)가 포함될 때 UTF-8 인코딩으로 정상 저장
- **14자리 설비 코드 검증**: process_code에 14자리가 아닌 값이 입력될 때 경고 또는 거부

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 backend/, frontend-admin/, frontend-monitor/ 3개의 주요 디렉토리를 생성해야 함
- **FR-002**: backend/ 디렉토리 내에 src/, config/, logs/, tests/ 하위 디렉토리를 포함해야 함
- **FR-003**: SQLite 데이터베이스 파일(scada.db)을 backend/config/ 디렉토리에 생성해야 함
- **FR-004**: lines 테이블에 id, line_code(고유), line_name, location, enabled, created_at, updated_at 컬럼이 있어야 함
- **FR-005**: processes 테이블에 id, line_id(FK), process_sequence, process_code(고유, 14자리), process_name, equipment_type, enabled, created_at, updated_at 컬럼이 있어야 함
- **FR-006**: plc_connections 테이블에 id, process_id(FK), plc_code(고유), ip_address, port(기본값 5000), network_no, station_no, enabled, created_at, updated_at 컬럼이 있어야 함
- **FR-007**: tags 테이블에 id, plc_id(FK), process_id(FK), tag_address, tag_name, tag_division, data_type, unit, scale, machine_code, polling_group_id(FK), enabled, created_at, updated_at 컬럼이 있어야 함
- **FR-008**: polling_groups 테이블에 id, group_name, line_code, process_code, plc_id(FK), mode(FIXED/HANDSHAKE), interval_ms, trigger_bit_address, trigger_bit_offset, auto_reset_trigger, priority, enabled, created_at, updated_at 컬럼이 있어야 함
- **FR-009**: processes 테이블의 process_code는 14자리 형식(예: KRCWO12ELOA101)을 저장할 수 있어야 함
- **FR-010**: tags 테이블은 최소 3,491개 이상의 레코드를 저장할 수 있어야 함
- **FR-011**: Foreign Key 제약으로 line → process → plc → tag → polling_group 관계를 유지해야 함
- **FR-012**: 라인 삭제 시 CASCADE로 연결된 모든 하위 데이터(공정, PLC, 태그)가 자동 삭제되어야 함
- **FR-013**: 폴링 그룹 삭제 시 태그의 polling_group_id가 NULL로 설정(SET NULL)되어야 함
- **FR-014**: CSV 파일에서 태그 정보를 읽어 tags 테이블에 일괄 삽입하는 스크립트를 제공해야 함
- **FR-015**: CSV 가져오기 시 PLC_CODE, TAG_ADDRESS, TAG_NAME, UNIT, SCALE, MACHINE_CODE 컬럼을 필수로 처리해야 함
- **FR-016**: CSV 가져오기 실패 시(중복 키, 잘못된 데이터 등) 오류 로그를 출력해야 함
- **FR-017**: 데이터베이스 초기화 SQL 스크립트를 제공하여 스키마 재생성을 지원해야 함
- **FR-018**: 개발 및 테스트를 위한 샘플 데이터(최소 1개 라인, 2개 공정, 2개 PLC, 10개 태그, 2개 폴링 그룹) 삽입 스크립트를 제공해야 함
- **FR-019**: 모든 텍스트 데이터는 UTF-8 인코딩으로 저장하여 한글 및 특수문자를 지원해야 함
- **FR-020**: 인덱스를 생성하여 plc_id, process_id, polling_group_id, tag_address로 빠른 조회를 지원해야 함

### Key Entities

- **Line (라인)**: 생산 라인 정보. 속성: 라인 코드, 라인명, 위치, 활성화 여부. 관계: 여러 공정을 포함.
- **Process (공정)**: 생산 공정 정보. 속성: 14자리 설비 코드, 공정명, 설비 타입, 순서. 관계: 하나의 라인에 속하며, 여러 PLC를 포함.
- **PLC Connection (PLC 연결)**: PLC 연결 정보. 속성: PLC 코드, IP 주소, 포트, 네트워크/스테이션 번호. 관계: 하나의 공정에 속하며, 여러 태그를 포함.
- **Tag (태그)**: PLC 메모리 주소와 연결된 데이터 포인트. 속성: 태그 주소(W150, M100 등), 태그명, 단위, 스케일, 데이터 타입. 관계: 하나의 PLC에 속하며, 하나의 폴링 그룹에 선택적으로 할당.
- **Polling Group (폴링 그룹)**: 동일한 폴링 설정을 공유하는 태그들의 논리적 그룹. 속성: 그룹명, 폴링 모드(FIXED/HANDSHAKE), 폴링 간격, 트리거 비트, 우선순위. 관계: 여러 태그를 포함.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 프로젝트 구조 초기화 스크립트를 실행하면 30초 이내에 모든 필수 디렉토리가 생성됨
- **SC-002**: SQLite 데이터베이스 스키마 생성 스크립트를 실행하면 10초 이내에 5개 테이블과 모든 인덱스가 생성됨
- **SC-003**: 3,491개 태그를 CSV에서 일괄 가져오기 시 5분 이내에 완료됨
- **SC-004**: 데이터베이스는 최소 10,000개 태그를 저장할 수 있는 확장성을 보유함
- **SC-005**: Foreign Key 제약 조건이 100% 정확하게 작동하여 잘못된 참조를 방지함
- **SC-006**: 한글, 특수문자(%, °C, ℃)가 포함된 태그명이 깨짐 없이 정상적으로 저장되고 조회됨
- **SC-007**: 샘플 데이터 삽입 후 폴링 그룹별 태그 조회 쿼리가 100ms 이내에 결과를 반환함
- **SC-008**: 데이터베이스 파일 크기가 초기 빈 상태에서 50MB 이하로 유지됨(3,491개 태그 기준)
- **SC-009**: 14자리 설비 코드 형식(KRCWO12ELOA101)이 processes 테이블에 올바르게 저장됨
- **SC-010**: 데이터베이스 백업 스크립트를 실행하면 10초 이내에 백업 파일이 생성됨

## Assumptions

- SQLite는 단일 서버 환경에서만 사용되며, 원격 접근이나 다중 서버 환경은 고려하지 않음
- CSV 파일은 UTF-8 인코딩으로 작성됨
- 개발 환경은 Windows 또는 Linux이며, SQLite 3.40 이상이 설치되어 있음
- Python 3.11 이상이 설치되어 있음
- 초기 버전에서는 사용자 인증 없이 로컬에서만 데이터베이스에 접근함
- 태그 수는 향후 10,000개까지 증가할 수 있음을 고려하여 설계
- 백업은 수동으로 수행하며, 자동 백업 스케줄링은 향후 기능으로 추가
