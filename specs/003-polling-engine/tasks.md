# Tasks: Multi-threaded Polling Engine

**Input**: Design documents from `/specs/003-polling-engine/`
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

**Purpose**: Project initialization and basic polling module structure

- [X] T001 Create backend/src/polling/ package structure with __init__.py
- [X] T002 [P] Create backend/src/polling/exceptions.py for polling-specific exceptions
- [X] T003 [P] Create backend/src/polling/models.py for data classes (PollingGroup, PollingData, PollingStatus)
- [X] T004 [P] Create backend/tests/unit/ directory structure for polling unit tests
- [X] T005 [P] Create backend/tests/integration/ directory structure for polling integration tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement DataQueue wrapper class in backend/src/polling/data_queue.py (thread-safe queue with monitoring)
- [X] T007 Implement base PollingThread abstract class in backend/src/polling/polling_thread.py (common thread logic, state management)
- [X] T008 Implement PollingEngine class skeleton in backend/src/polling/polling_engine.py (thread registry, DB loading, lifecycle management)
- [X] T009 Add polling group configuration loader in backend/src/polling/polling_engine.py (load from SQLite polling_groups table)
- [X] T010 Implement thread-safe status tracking in backend/src/polling/polling_engine.py (success/error counters, timestamps)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automatic Fixed-Interval Data Collection (Priority: P1) 🎯 MVP

**Goal**: Enable automatic polling of PLC tags at fixed intervals (e.g., 1s, 5s) with data stored in thread-safe queue

**Independent Test**: Configure one FIXED mode polling group in SQLite, start engine, verify data collected every 1 second in queue

### Implementation for User Story 1

- [X] T011 [P] [US1] Implement FixedPollingThread class in backend/src/polling/fixed_polling_thread.py (inherits PollingThread, implements fixed-interval logic)
- [X] T012 [P] [US1] Add interval timing with drift correction in backend/src/polling/fixed_polling_thread.py (use time.perf_counter() per research.md)
- [X] T013 [US1] Implement polling cycle in backend/src/polling/fixed_polling_thread.py (load tags, call PoolManager.read_batch, create PollingData)
- [X] T014 [US1] Add graceful thread termination logic in backend/src/polling/fixed_polling_thread.py (check stop_event, complete current cycle)
- [X] T015 [US1] Integrate FixedPollingThread with PollingEngine in backend/src/polling/polling_engine.py (create thread for FIXED mode groups)
- [X] T016 [US1] Implement PollingEngine.start_all() method in backend/src/polling/polling_engine.py (start all active polling groups)
- [X] T017 [US1] Implement PollingEngine.stop_all() method in backend/src/polling/polling_engine.py (graceful shutdown with <5s timeout)
- [X] T018 [US1] Add logging for polling cycle start/completion/errors in backend/src/polling/fixed_polling_thread.py
- [X] T019 [US1] Create test script backend/src/scripts/test_polling_fixed.py (load 1 FIXED group, run 10 cycles, verify timing accuracy ±10%)

**Checkpoint**: FIXED mode polling fully functional - MVP complete

---

## Phase 4: User Story 2 - Manual On-Demand Data Collection (Priority: P2)

**Goal**: Enable manual trigger of polling via API for HANDSHAKE mode groups

**Independent Test**: Configure one HANDSHAKE mode group, call trigger API, verify immediate single poll execution

### Implementation for User Story 2

- [X] T020 [P] [US2] Implement HandshakePollingThread class in backend/src/polling/handshake_polling_thread.py (inherits PollingThread, waits for trigger event)
- [X] T021 [P] [US2] Add trigger event mechanism in backend/src/polling/handshake_polling_thread.py (threading.Event for manual activation)
- [X] T022 [US2] Implement single-shot polling cycle in backend/src/polling/handshake_polling_thread.py (poll once per trigger, return to waiting)
- [X] T023 [US2] Add trigger request deduplication in backend/src/polling/handshake_polling_thread.py (ignore duplicates within 1-second window)
- [X] T024 [US2] Integrate HandshakePollingThread with PollingEngine in backend/src/polling/polling_engine.py (create thread for HANDSHAKE mode groups)
- [X] T025 [US2] Implement PollingEngine.trigger_handshake(group_name) method in backend/src/polling/polling_engine.py
- [X] T026 [US2] Add response with execution status in backend/src/polling/polling_engine.py (return success/failure, tag count)
- [X] T027 [US2] Add logging for HANDSHAKE trigger events in backend/src/polling/handshake_polling_thread.py
- [X] T028 [US2] Create test script backend/src/scripts/test_polling_handshake.py (trigger poll, verify immediate execution, check queue data)

**Checkpoint**: HANDSHAKE mode polling fully functional - both polling modes working

---

## Phase 5: User Story 3 - Polling Engine Control and Monitoring (Priority: P2)

**Goal**: Provide APIs to start, stop, and query status of individual polling groups

**Independent Test**: Start individual group via API, query status (verify running state, counters), stop group (verify graceful termination)

### Implementation for User Story 3

- [X] T029 [P] [US3] Implement PollingEngine.start_group(group_name) method in backend/src/polling/polling_engine.py (start specific group by name)
- [X] T030 [P] [US3] Implement PollingEngine.stop_group(group_name) method in backend/src/polling/polling_engine.py (stop specific group gracefully)
- [X] T031 [P] [US3] Implement PollingEngine.get_status() method in backend/src/polling/polling_engine.py (return all groups: name, mode, state, last_poll_time, success_count, error_count)
- [X] T032 [P] [US3] Add queue size monitoring in backend/src/polling/polling_engine.py (return current DataQueue size in status)
- [X] T033 [US3] Add resource utilization metrics in backend/src/polling/polling_engine.py (active thread count, queue size)
- [X] T034 [US3] Implement maximum capacity check in backend/src/polling/polling_engine.py (reject start when 10 groups running)
- [X] T035 [US3] Add status API response formatting in backend/src/polling/polling_engine.py (JSON-serializable dict with all metrics)
- [X] T036 [US3] Optimize status query performance in backend/src/polling/polling_engine.py (ensure <200ms response time)
- [X] T037 [US3] Create test script backend/src/scripts/test_polling_engine.py (test start/stop/status APIs, verify capacity limits)

**Checkpoint**: Full engine control available - operational management ready

---

## Phase 6: User Story 4 - Error Recovery and Resilience (Priority: P3)

**Goal**: Handle PLC connection errors gracefully with automatic retry and error logging

**Independent Test**: Simulate PLC failure (disconnect network), verify error logged, polling continues at next interval, auto-recovers when connection restored

### Implementation for User Story 4

- [X] T038 [P] [US4] Add PLC connection error handling in backend/src/polling/polling_thread.py (catch PoolManager exceptions, log error)
- [X] T039 [P] [US4] Implement error counter tracking in backend/src/polling/polling_thread.py (increment error_count, track last_error_time)
- [X] T040 [P] [US4] Add detailed error logging in backend/src/polling/polling_thread.py (timestamp, group_name, error_type, tag_count, retry_strategy)
- [X] T041 [US4] Implement automatic retry logic in backend/src/polling/fixed_polling_thread.py (continue polling at next interval after error)
- [X] T042 [US4] Implement automatic retry logic in backend/src/polling/handshake_polling_thread.py (mark poll complete even on error, wait for next trigger)
- [X] T043 [US4] Add connection pool timeout handling in backend/src/polling/polling_thread.py (wait up to 10s for available connection)
- [X] T044 [US4] Implement thread isolation for errors in backend/src/polling/polling_engine.py (ensure one group's errors don't affect others)
- [X] T045 [US4] Add thread crash recovery in backend/src/polling/polling_engine.py (detect dead threads, log critical error, optional auto-restart)
- [X] T046 [US4] Create test script backend/src/scripts/test_error_recovery.py (simulate connection failures, verify logging, check auto-recovery)
- [X] T047 [US4] Create integration test backend/tests/integration/test_polling_resilience.py (multi-group test with intentional failures)

**Checkpoint**: Error recovery complete - system is production-ready

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, documentation, and deployment readiness

- [X] T048 [P] Add memory leak prevention checks in backend/src/polling/polling_engine.py (verify thread cleanup, queue cleanup on shutdown)
- [X] T049 [P] Optimize batch read performance in backend/src/polling/polling_thread.py (verify using PoolManager.read_batch for 100+ tags)
- [X] T050 [P] Add comprehensive logging configuration in backend/src/polling/__init__.py (RotatingFileHandler, configurable log levels)
- [X] T051 Update backend/requirements.txt if needed (confirm no new dependencies - all stdlib except Feature 2)
- [X] T052 Create integration test backend/tests/integration/test_polling_integration.py (10 concurrent groups, verify no conflicts, measure performance)
- [X] T053 [P] Add docstrings to all public methods in backend/src/polling/ modules
- [X] T054 [P] Create README for polling module in backend/src/polling/README.md (architecture overview, usage examples)
- [X] T055 Verify 24-hour continuous operation test (run engine for extended period, monitor memory/CPU, verify no leaks)

---

## Phase 8: Frontend and REST API (Extended - User Requested)

**Purpose**: Add REST API layer and web-based management UI for polling engine control

**Note**: This phase was added per user request ("전부추가" - add everything) beyond the original specification

- [X] T056 [P] Create backend/src/api/ package structure with __init__.py
- [X] T057 [P] Implement FastAPI application in backend/src/api/main.py (app setup, CORS, lifespan management)
- [X] T058 [P] Implement REST API routes in backend/src/api/polling_routes.py (GET /status, POST /start, POST /stop, POST /trigger endpoints)
- [X] T059 [P] Create WebSocket handler in backend/src/api/websocket_handler.py (real-time status updates via WebSocket)
- [X] T060 [P] Integrate WebSocket endpoint in backend/src/api/main.py (WebSocket route at /ws/polling)
- [X] T061 [P] Create TypeScript API client in frontend-admin/src/lib/api/pollingApi.ts (typed interfaces for all endpoints)
- [X] T062 [P] Create QueueMonitor component in frontend-admin/src/app/polling/components/QueueMonitor.tsx (visual queue status display)
- [X] T063 [P] Create PollingChart component in frontend-admin/src/app/polling/components/PollingChart.tsx (performance visualization with canvas)
- [X] T064 [P] Create polling management page in frontend-admin/src/app/polling/page.tsx (HTTP polling version with 2s refresh)
- [X] T065 [P] Create WebSocket hook in frontend-admin/src/lib/hooks/usePollingWebSocket.ts (React hook for WebSocket connection)
- [X] T066 [P] Create WebSocket-based polling page in frontend-admin/src/app/polling-ws/page.tsx (real-time updates version)

**Checkpoint**: Full-stack implementation complete - REST API + WebSocket + React UI operational

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
**Parallel Opportunities**: US2, US3 can be developed in parallel after US1 is complete

### Task Dependencies

**Phase 2 blocks everything** - must complete T006-T010 before any user story work

**Within User Stories** (can be parallelized):
- US1: T011-T012 can run in parallel (different aspects of FixedPollingThread)
- US2: T020-T021 can run in parallel (HandshakePollingThread base + event mechanism)
- US3: T029-T032 can run in parallel (different API methods)
- US4: T038-T040 can run in parallel (error handling in different modules)

---

## Parallel Execution Examples

### After Phase 2 Complete:

**Scenario 1: Single developer, sequential MVP**
1. Complete US1 (T011-T019) → MVP ready for testing
2. Then add US2 (T020-T028) → Manual triggering available
3. Then add US3 (T029-T037) → Full control APIs
4. Then add US4 (T038-T047) → Production hardening

**Scenario 2: Two developers, parallel features**
- Developer A: US1 (T011-T019) → MVP
- Developer B: US2 (T020-T028) after A finishes T010
- Then merge, both work on US3 + US4 in parallel

**Scenario 3: Three developers, maximum parallelism**
- Dev A: US1 (T011-T019)
- Dev B: US2 (T020-T028) starting after T010 complete
- Dev C: US3 (T029-T037) starting after T010 complete
- All merge, then tackle US4 together

---

## Implementation Strategy

**MVP First** (Phase 1 → Phase 2 → Phase 3):
- Delivers core value: automatic polling of PLC tags
- Independent test: Single FIXED mode group polling at 1-second interval
- Estimated effort: ~60% of total work
- Timeline: Implement T001-T019, verify US1 acceptance scenarios

**Incremental Delivery**:
1. **MVP**: US1 only (automatic polling) - can deploy for basic monitoring
2. **v1.1**: Add US2 (manual triggers) - enables diagnostics
3. **v1.2**: Add US3 (control APIs) - enables operational management
4. **v1.3**: Add US4 (error recovery) - production hardening

**Acceptance Criteria per Story**:
- **US1**: 100 tags polled at 1s interval with ±10% accuracy, data in queue
- **US2**: Trigger API responds <500ms, poll starts within 1s
- **US3**: Status API responds <200ms, graceful stop within 5s
- **US4**: Errors logged with full details, auto-recovery after connection restore

---

## Task Summary

**Total Tasks**: 66 (55 original + 11 frontend/API extension)
- **Setup**: 5 tasks (T001-T005)
- **Foundational**: 5 tasks (T006-T010)
- **US1 (P1 - MVP)**: 9 tasks (T011-T019)
- **US2 (P2)**: 9 tasks (T020-T028)
- **US3 (P2)**: 9 tasks (T029-T037)
- **US4 (P3)**: 10 tasks (T038-T047)
- **Polish**: 8 tasks (T048-T055)
- **Frontend/API (Extended)**: 11 tasks (T056-T066)

**Parallel Opportunities**: 29 tasks marked [P] can be parallelized (including all Phase 8 tasks)

**MVP Scope**: T001-T019 (24 tasks) delivers User Story 1
**Full-Stack Scope**: T001-T066 (66 tasks) delivers complete backend + REST API + WebSocket + React UI

**Format Validation**: ✅ All tasks follow `- [ ] [ID] [P?] [Story?] Description with file/path`
