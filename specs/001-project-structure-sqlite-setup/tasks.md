# Tasks: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정

**Input**: Design documents from `/specs/001-project-structure-sqlite-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: 이 기능에는 테스트가 명시적으로 요청되지 않았으므로 수동 검증으로 진행합니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend-admin/`, `frontend-monitor/`
- Paths follow plan.md structure (1 backend + 2 frontends)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend/ directory structure (src/, config/, logs/, tests/)
- [ ] T002 Create frontend-admin/ directory structure (app/, components/, lib/, public/)
- [ ] T003 Create frontend-monitor/ directory structure (app/, components/, lib/, public/)
- [ ] T004 [P] Create backend/requirements.txt with Python dependencies
- [ ] T005 [P] Create backend/.env.example with environment variable templates
- [ ] T006 [P] Create backend/README.md with setup instructions
- [ ] T007 [P] Create frontend-admin/package.json with Next.js dependencies
- [ ] T008 [P] Create frontend-monitor/package.json with Next.js dependencies
- [ ] T009 [P] Create .gitignore for Python and Node.js projects
- [ ] T010 [P] Create root README.md with project overview

**Checkpoint**: All directories and basic configuration files created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create backend/config/init_scada_db.sql with complete database schema
- [ ] T012 Create backend/src/database/__init__.py
- [ ] T013 Create backend/src/database/models.py with Python data models
- [ ] T014 Create backend/src/database/sqlite_manager.py with connection and query management
- [ ] T015 Create backend/src/scripts/__init__.py
- [ ] T016 Create backend/src/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 프로젝트 디렉토리 구조 생성 (Priority: P1) 🎯 MVP

**Goal**: 표준화된 프로젝트 디렉토리 구조 생성 및 검증

**Independent Test**: 필수 디렉토리들의 존재를 확인하고 기본 설정 파일 검증

### Implementation for User Story 1

- [ ] T017 [US1] Create backend/src/scripts/init_project_structure.py for automated directory creation
- [ ] T018 [US1] Implement directory creation logic in init_project_structure.py
- [ ] T019 [US1] Add basic file templates (README.md, __init__.py) generation to init_project_structure.py
- [ ] T020 [US1] Test directory structure creation by running init_project_structure.py
- [ ] T021 [US1] Verify all backend/ subdirectories exist (src/database, src/scripts, config, logs, tests)
- [ ] T022 [US1] Verify all frontend-admin/ subdirectories exist (app, components/ui, lib, public)
- [ ] T023 [US1] Verify all frontend-monitor/ subdirectories exist (app, components/ui, lib, public)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - SQLite 데이터베이스 스키마 생성 (Priority: P1) 🎯 MVP

**Goal**: SQLite 데이터베이스 파일 생성 및 5개 테이블 스키마 구축

**Independent Test**: scada.db 파일 생성 및 테이블 목록, 스키마 쿼리로 검증

### Implementation for User Story 2

- [ ] T024 [P] [US2] Add lines table SQL to init_scada_db.sql
- [ ] T025 [P] [US2] Add processes table SQL to init_scada_db.sql
- [ ] T026 [P] [US2] Add plc_connections table SQL to init_scada_db.sql
- [ ] T027 [P] [US2] Add tags table SQL to init_scada_db.sql
- [ ] T028 [P] [US2] Add polling_groups table SQL to init_scada_db.sql
- [ ] T029 [US2] Add all indexes to init_scada_db.sql (8 indexes)
- [ ] T030 [US2] Add v_tags_with_plc view to init_scada_db.sql
- [ ] T031 [US2] Create backend/src/scripts/init_database.py for database initialization
- [ ] T032 [US2] Implement database creation logic in init_database.py (execute SQL script)
- [ ] T033 [US2] Add PRAGMA foreign_keys = ON to database initialization
- [ ] T034 [US2] Test database initialization by running init_database.py
- [ ] T035 [US2] Verify scada.db file created in backend/config/
- [ ] T036 [US2] Verify all 5 tables exist using SQLite query
- [ ] T037 [US2] Verify table schemas match data-model.md specifications
- [ ] T038 [US2] Test 14-digit process_code insertion (KRCWO12ELOA101)
- [ ] T039 [US2] Verify UTF-8 encoding for Korean characters (태그명 테스트)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - 데이터베이스 관계 및 제약 조건 설정 (Priority: P2)

**Goal**: Foreign Key 제약으로 데이터 무결성 보장

**Independent Test**: Foreign Key 제약 위반 테스트 및 CASCADE 삭제 동작 검증

### Implementation for User Story 3

- [ ] T040 [US3] Add Foreign Key constraints to init_scada_db.sql (if not already added)
- [ ] T041 [US3] Implement CASCADE deletion for line → process → plc → tag
- [ ] T042 [US3] Implement SET NULL for polling_group → tag relationship
- [ ] T043 [US3] Create backend/tests/test_database.py for database constraint tests
- [ ] T044 [US3] Test Foreign Key constraint: Insert PLC without process (should fail)
- [ ] T045 [US3] Test CASCADE deletion: Delete line and verify all children deleted
- [ ] T046 [US3] Test SET NULL: Delete polling group and verify tags remain with NULL polling_group_id

**Checkpoint**: All user stories 1-3 should now be independently functional with data integrity

---

## Phase 6: User Story 4 - CSV 일괄 태그 등록 기능 (Priority: P2)

**Goal**: CSV 파일에서 3,491개 태그를 5분 이내에 일괄 등록

**Independent Test**: 샘플 CSV 파일 준비 및 가져오기 실행 후 태그 개수 검증

### Implementation for User Story 4

- [ ] T047 [US4] Create backend/src/scripts/import_tags_csv.py for CSV import
- [ ] T048 [US4] Implement CSV reading logic with UTF-8 encoding
- [ ] T049 [US4] Implement batch INSERT with transactions (500 rows per batch)
- [ ] T050 [US4] Add validation for required columns (PLC_CODE, TAG_ADDRESS, TAG_NAME, UNIT, SCALE, MACHINE_CODE)
- [ ] T051 [US4] Add error handling and logging for CSV import
- [ ] T052 [US4] Implement executemany() for performance optimization
- [ ] T053 [US4] Create sample CSV file (backend/tests/sample_tags.csv) with 10 tags
- [ ] T054 [US4] Test CSV import with sample file
- [ ] T055 [US4] Verify all tags inserted correctly
- [ ] T056 [US4] Test duplicate TAG_ADDRESS handling (should log error)
- [ ] T057 [US4] Test empty CSV file handling (should return 0 records processed)
- [ ] T058 [US4] Create backend/tests/test_csv_import.py for CSV import tests

**Checkpoint**: CSV bulk import feature fully functional

---

## Phase 7: User Story 5 - 데이터베이스 초기 데이터 설정 (Priority: P3)

**Goal**: 개발 및 테스트용 샘플 데이터 자동 생성

**Independent Test**: 샘플 데이터 생성 후 최소 1개 라인, 2개 공정, 2개 PLC, 10개 태그, 2개 폴링 그룹 확인

### Implementation for User Story 5

- [ ] T059 [US5] Create backend/src/scripts/create_sample_data.py for sample data generation
- [ ] T060 [US5] Implement sample line insertion (LINE01: TUB 가공 라인)
- [ ] T061 [US5] Implement sample processes insertion (2 processes: Upper Loading, Welding)
- [ ] T062 [US5] Implement sample PLC connections insertion (PLC01, PLC02)
- [ ] T063 [US5] Implement sample polling groups insertion (1 FIXED, 1 HANDSHAKE)
- [ ] T064 [US5] Implement sample tags insertion (10 tags with Korean names)
- [ ] T065 [US5] Test sample data generation by running create_sample_data.py
- [ ] T066 [US5] Verify 1 line exists
- [ ] T067 [US5] Verify 2 processes exist
- [ ] T068 [US5] Verify 2 PLCs exist
- [ ] T069 [US5] Verify 2 polling groups exist (1 FIXED, 1 HANDSHAKE)
- [ ] T070 [US5] Verify at least 10 tags exist
- [ ] T071 [US5] Verify tags are assigned to polling groups

**Checkpoint**: All user stories should now be independently functional with sample data

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T072 [P] Create backend/scripts/backup_sqlite.sh for database backup
- [ ] T073 [P] Test database backup script
- [ ] T074 [P] Update backend/README.md with quickstart instructions
- [ ] T075 [P] Update frontend-admin/README.md with setup instructions
- [ ] T076 [P] Update frontend-monitor/README.md with setup instructions
- [ ] T077 [P] Update root README.md with project structure overview
- [ ] T078 [P] Add SQLite query examples to backend/README.md
- [ ] T079 Test all user stories end-to-end (US1 → US2 → US3 → US4 → US5)
- [ ] T080 Run quickstart.md validation (5-minute quick start test)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Independent - can start after Foundational
  - US2 (P1): Depends on US1 (needs directory structure)
  - US3 (P2): Depends on US2 (needs database schema)
  - US4 (P2): Depends on US2 and US3 (needs database with constraints)
  - US5 (P3): Depends on US2 (needs database schema)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 for directory structure
- **User Story 3 (P2)**: Depends on US2 for database existence
- **User Story 4 (P2)**: Depends on US2 and US3 for full database setup
- **User Story 5 (P3)**: Depends on US2 for database schema

### Within Each User Story

- Directory creation tasks can run in parallel [P]
- SQL schema additions can run in parallel [P]
- Scripts must be created before testing
- Verification tasks run after implementation

### Parallel Opportunities

- **Phase 1 Setup**: All file creation tasks (T004-T010) can run in parallel
- **Phase 2 Foundational**: Model files can be created in parallel
- **Phase 4 US2**: All SQL table additions (T024-T028) can run in parallel
- **Phase 8 Polish**: All documentation updates (T072-T078) can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Directory structure)
4. Complete Phase 4: User Story 2 (Database schema)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently (Directory structure works)
3. Add User Story 2 → Test independently (Database creation works)
4. Add User Story 3 → Test independently (Constraints work)
5. Add User Story 4 → Test independently (CSV import works)
6. Add User Story 5 → Test independently (Sample data works)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2 preparation (SQL schemas)
3. After US1 complete:
   - Developer B: User Story 2 (depends on US1)
   - Developer C: User Story 5 preparation
4. After US2 complete:
   - Developer A: User Story 3
   - Developer C: User Story 4
   - Developer D: User Story 5

---

## Task Summary

- **Total Tasks**: 80
- **Setup Phase**: 10 tasks
- **Foundational Phase**: 6 tasks
- **User Story 1**: 7 tasks
- **User Story 2**: 16 tasks
- **User Story 3**: 7 tasks
- **User Story 4**: 12 tasks
- **User Story 5**: 13 tasks
- **Polish Phase**: 9 tasks

**Parallel Opportunities**: 20+ tasks can run in parallel (marked with [P])

**MVP Scope**: User Stories 1 + 2 (완전히 독립적으로 테스트 가능한 기본 기능)

**Estimated Time**:
- MVP (US1 + US2): 4-6 hours
- Full Feature (US1-US5): 8-12 hours

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are absolute from project root
- SQLite database file: `backend/config/scada.db`
- Tests are optional and validated through manual verification
