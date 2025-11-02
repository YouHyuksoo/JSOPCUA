# Tasks: Thread-Safe Buffer and Oracle DB Writer

**Input**: Design documents from `/specs/004-buffer-oracle-writer/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: NOT requested in feature specification - implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Project type: Web application (backend only for this feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic buffer/Oracle module structure

- [X] T001 Create backend/src/buffer/ package structure with __init__.py
- [X] T002 [P] Create backend/src/buffer/exceptions.py for buffer-specific exceptions
- [X] T003 [P] Create backend/src/buffer/models.py for data classes (BufferedTagValue, WriteBatch, WriterMetrics)
- [X] T004 [P] Create backend/src/oracle_writer/ package structure with __init__.py
- [X] T005 [P] Create backend/backup/ directory for CSV backup files with .gitkeep
- [X] T006 Add python-oracledb to backend/requirements.txt
- [X] T007 [P] Update backend/.env.example with Oracle connection config variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Implement CircularBuffer class in backend/src/buffer/circular_buffer.py (deque-based, maxlen=100k, thread-safe)
- [X] T009 Implement RollingMetrics class in backend/src/oracle_writer/metrics.py (time-windowed averages for 5-minute rolling stats)
- [X] T010 Create Oracle connection config in backend/src/oracle_writer/config.py (load from env vars, validate required fields)
- [X] T011 Implement OracleConnectionPool wrapper in backend/src/oracle_writer/connection_pool.py (create_pool with min=2, max=5)
- [X] T012 Create test script backend/src/scripts/test_oracle_connection.py (verify Oracle connectivity before proceeding)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Reliable Data Persistence to Oracle (Priority: P1) 🎯 MVP

**Goal**: Consume from Feature 3 DataQueue, buffer data, batch write to Oracle with CSV backup on failure

**Independent Test**: Start buffer consumer + Oracle writer, poll 1 group, verify data in Oracle tag_values table within 2s, stop Oracle temporarily and verify CSV backup creation

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement BufferConsumer thread in backend/src/buffer/buffer_consumer.py (consume DataQueue, expand PollingData to BufferedTagValue items, push to CircularBuffer)
- [X] T014 [P] [US1] Implement OracleWriter thread in backend/src/oracle_writer/writer.py (consume CircularBuffer, batch 100-1000 items, executemany() bulk insert)
- [X] T015 [US1] Add Oracle batch write logic in backend/src/oracle_writer/writer.py (executemany with batcherrors=True)
- [X] T016 [US1] Implement retry logic with exponential backoff in backend/src/oracle_writer/writer.py (3 retries: 1s, 2s, 4s delays)
- [X] T017 [US1] Implement CSV backup in backend/src/oracle_writer/backup.py (save failed writes to timestamped CSV after all retries exhausted)
- [X] T018 [US1] Integrate BufferConsumer with Feature 3 DataQueue in backend/src/buffer/buffer_consumer.py (read PollingData objects)
- [X] T019 [US1] Add logging for buffer consumer and Oracle writer threads (buffer intake, batch writes, retry attempts, CSV backups)
- [X] T020 [US1] Create startup script backend/src/scripts/start_buffer_writer.py (launch BufferConsumer + OracleWriter threads)
- [X] T021 [US1] Create test script to verify end-to-end flow (poll → buffer → Oracle)

**Checkpoint**: MVP complete - data persists to Oracle with CSV backup failover

---

## Phase 4: User Story 2 - High-Throughput Batch Writing (Priority: P2)

**Goal**: Optimize batch writing for high volume (1,000+ values/sec) with configurable batch sizes and write triggers

**Independent Test**: Configure 10 polling groups (100 tags each, 1s interval), verify <2s write latency and buffer never exceeds 80% capacity

### Implementation for User Story 2

- [X] T022 [P] [US2] Add batch size optimization in backend/src/oracle_writer/writer.py (configurable batch size 100-1000, default 500)
- [X] T023 [P] [US2] Implement write trigger conditions in backend/src/oracle_writer/writer.py (1 second timer OR 500 items threshold, whichever occurs first)
- [X] T024 [US2] Add performance timing metrics in backend/src/oracle_writer/writer.py (track batch write latency with RollingMetrics)
- [X] T025 [US2] Optimize memory usage in backend/src/buffer/circular_buffer.py (verify ~25MB for 100k items, profile if needed)
- [X] T026 [US2] Add configurable batch size via environment variable in backend/src/oracle_writer/config.py
- [X] T027 [US2] Create performance test script backend/src/scripts/test_high_throughput.py (simulate 1,000 values/sec, verify <2s latency)

**Checkpoint**: High-throughput batch writing operational

---

## Phase 5: User Story 3 - Buffer Overflow Protection (Priority: P2)

**Goal**: Graceful FIFO overflow handling with alerts and monitoring

**Independent Test**: Fill buffer to capacity (100k items), continue adding data, verify FIFO eviction and overflow alerts

### Implementation for User Story 3

- [X] T028 [P] [US3] Add overflow detection in backend/src/buffer/circular_buffer.py (track overflow count when deque maxlen evicts items)
- [X] T029 [P] [US3] Implement overflow alerts in backend/src/buffer/circular_buffer.py (log warnings with overflow statistics)
- [X] T030 [US3] Add overflow rate calculation in backend/src/oracle_writer/metrics.py (track overflow percentage over 1-hour rolling window)
- [X] T031 [US3] Create test script backend/src/scripts/test_buffer_overflow.py (fill buffer, verify FIFO eviction, check overflow <1%)

**Checkpoint**: Buffer overflow protection complete - system stable under extreme load

---

## Phase 6: User Story 4 - Real-Time Monitoring and Observability (Priority: P3)

**Goal**: Expose buffer/writer metrics via REST API and integrate with Admin UI

**Independent Test**: Access GET /api/buffer/metrics, verify buffer utilization, write success/failure counts, avg batch size, avg latency, backup file count

### Implementation for User Story 4

- [X] T032 [P] [US4] Create buffer_routes.py in backend/src/api/ with GET /api/buffer/metrics endpoint
- [X] T033 [P] [US4] Implement metrics aggregation in backend/src/oracle_writer/metrics.py (current buffer size, max size, utilization %, write counts, rolling averages)
- [X] T034 [US4] Integrate buffer metrics route in backend/src/api/main.py (register buffer_routes router)
- [X] T035 [US4] Add backup file count tracking in backend/src/oracle_writer/backup.py (count .csv files in backup/ directory)
- [X] T036 [US4] Extend Admin UI monitoring page (apps/admin/app/buffer/page.tsx) to display buffer metrics
- [X] T037 [US4] Create monitoring test script backend/src/scripts/test_buffer_metrics.py (query API, verify metrics accuracy)

**Checkpoint**: Real-time monitoring operational - full observability via API and UI

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration, graceful shutdown, documentation

- [ ] T038 [P] Implement graceful shutdown in backend/src/buffer/buffer_consumer.py (flush remaining buffer data within 10s)
- [ ] T039 [P] Implement graceful shutdown in backend/src/oracle_writer/writer.py (complete pending batch writes)
- [ ] T040 [P] Create integrated startup script backend/src/scripts/start_all.py (Feature 3 polling + Feature 4 buffer + Oracle writer)
- [ ] T041 [P] Create graceful shutdown script backend/src/scripts/stop_all.py (stop all threads, flush buffers, close connections)
- [ ] T042 [P] Add comprehensive logging configuration in backend/src/buffer/__init__.py (RotatingFileHandler for buffer.log)
- [ ] T043 [P] Add comprehensive logging configuration in backend/src/oracle_writer/__init__.py (RotatingFileHandler for oracle_writer.log)
- [ ] T044 Create README for buffer module in backend/src/buffer/README.md (architecture overview, usage examples)
- [ ] T045 Create README for Oracle writer module in backend/src/oracle_writer/README.md (configuration guide, troubleshooting)
- [ ] T046 Update main backend/README.md with Feature 4 integration instructions
- [ ] T047 Create integration test backend/tests/integration/test_end_to_end.py (Feature 3 polling → Feature 4 buffer → Oracle → verify data)

---

## Dependencies

### Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1 - MVP)
                                          ↓
                                    Phase 4 (US2) can run in parallel with Phase 5 (US3)
                                          ↓
                                    Phase 6 (US4)
                                          ↓
                                    Phase 7 (Polish)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) is the MVP
**Parallel Opportunities**: US2, US3, US4 can be developed in parallel after US1 is complete

### Task Dependencies

**Phase 2 blocks everything** - must complete T008-T012 before any user story work

**Within User Stories** (can be parallelized):
- US1: T013-T014 can run in parallel (BufferConsumer and OracleWriter are independent until integrated)
- US2: T022-T023-T024 can run in parallel (batch optimization tasks in different files)
- US3: T028-T029 can run in parallel (overflow detection and alerts)
- US4: T032-T033 can run in parallel (API routes and metrics aggregation)

---

## Parallel Execution Examples

### After Phase 2 Complete:

**Scenario 1: Single developer, sequential MVP**
1. Complete US1 (T013-T021) → MVP ready for testing
2. Then add US2 (T022-T027) → Performance optimized
3. Then add US3 (T028-T031) → Overflow protection
4. Then add US4 (T032-T037) → Monitoring operational

**Scenario 2: Two developers, parallel features**
- Developer A: US1 (T013-T021) → MVP
- Developer B: US2 (T022-T027) after US1 completes T020
- Then merge, both work on US3 + US4 in parallel

**Scenario 3: Three developers, maximum parallelism**
- Dev A: US1 (T013-T021)
- Dev B: US2 (T022-T027) starting after T020 complete
- Dev C: US3 (T028-T031) starting after T020 complete
- All merge, then tackle US4 together

---

## Implementation Strategy

**MVP First** (Phase 1 → Phase 2 → Phase 3):
- Delivers core value: data persistence to Oracle with CSV backup
- Independent test: Polling → Buffer → Oracle → verify data
- Estimated effort: ~60% of total work
- Timeline: Implement T001-T021, verify US1 acceptance scenarios

**Incremental Delivery**:
1. **MVP**: US1 only (data persistence + CSV backup) - can deploy for basic Oracle storage
2. **v1.1**: Add US2 (batch optimization) - handles high-volume production load
3. **v1.2**: Add US3 (overflow protection) - production hardening for edge cases
4. **v1.3**: Add US4 (monitoring) - operational observability

**Acceptance Criteria per Story**:
- **US1**: Data appears in Oracle within 2s, CSV backup on Oracle failure, zero data loss
- **US2**: 1,000 values/sec throughput, <2s avg write latency, buffer <80% capacity
- **US3**: FIFO eviction when full, overflow <1% over 1 hour, clear alerts logged
- **US4**: Metrics API <500ms response, Admin UI displays buffer stats, backup file count

---

## Task Summary

**Total Tasks**: 47
- **Setup**: 7 tasks (T001-T007)
- **Foundational**: 5 tasks (T008-T012)
- **US1 (P1 - MVP)**: 9 tasks (T013-T021)
- **US2 (P2)**: 6 tasks (T022-T027)
- **US3 (P2)**: 4 tasks (T028-T031)
- **US4 (P3)**: 6 tasks (T032-T037)
- **Polish**: 10 tasks (T038-T047)

**Parallel Opportunities**: 18 tasks marked [P] can be parallelized

**MVP Scope**: T001-T021 (26 tasks) delivers User Story 1

**Format Validation**: ✅ All tasks follow `- [ ] [ID] [P?] [Story?] Description with file/path`
