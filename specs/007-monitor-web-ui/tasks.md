# Tasks: 실시간 설비 모니터링 웹 UI

**Input**: Design documents from `/specs/007-monitor-web-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT requested in the specification - manual testing will be performed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `apps/monitor/` (monorepo structure)
- All paths are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Monitor UI 프로젝트 초기화 및 기본 구조 생성

- [X] T001 Create Monitor UI app structure in apps/monitor/ directory
- [X] T002 Initialize Next.js 14 project with App Router in apps/monitor/
- [X] T003 [P] Install shadcn/ui dependencies in apps/monitor/ (reuse from admin)
- [X] T004 [P] Configure Tailwind CSS with 1280px breakpoint in apps/monitor/tailwind.config.ts
- [X] T005 [P] Setup TypeScript types for equipment and alarm in apps/monitor/lib/types/
- [X] T006 [P] Create WebSocket custom hook template in apps/monitor/lib/hooks/useWebSocket.ts
- [X] T007 [P] Add dev:monitor script to root package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 백엔드 API 및 WebSocket 엔드포인트 구현 (모든 User Story의 선행 조건)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create Oracle DB ALARMS table schema in backend/ (if not exists)
- [X] T009 Create Pydantic models for Alarm and AlarmStatistics in backend/src/api/models.py
- [X] T010 [P] Implement GET /api/alarms/statistics endpoint in backend/src/api/alarm_routes.py
- [X] T011 [P] Implement GET /api/alarms/recent endpoint in backend/src/api/alarm_routes.py
- [X] T012 Register alarm_routes in backend/src/api/main.py
- [X] T013 Implement WebSocket /ws/monitor endpoint in backend/src/api/websocket_monitor.py
- [X] T014 Update backend WebSocket server to broadcast equipment status (1s interval)
- [X] T015 Add CORS configuration for localhost:3001 in backend/src/api/main.py

**Checkpoint**: 백엔드 API 및 WebSocket 준비 완료 - 프론트엔드 User Story 구현 시작 가능

---

## Phase 3: User Story 1 - 실시간 설비 상태 모니터링 (Priority: P1) 🎯 MVP

**Goal**: WebSocket 연결을 통해 17개 설비의 실시간 상태를 1초 주기로 모니터링하고, 5가지 색상으로 설비 상태를 표시합니다.

**Independent Test**: WebSocket 연결 후 1초마다 설비 상태 박스가 업데이트되고, 5가지 색상(Green/Yellow/Red/Purple/Gray)에 따라 정확하게 표시되는지 확인합니다. PLC 연결을 끊으면 해당 설비가 Gray(접속이상)로 변경되는지 테스트합니다.

### Implementation for User Story 1

- [X] T016 [P] [US1] Create Equipment type definitions in apps/monitor/lib/types/equipment.ts
- [X] T017 [P] [US1] Create WebSocket message type definitions in apps/monitor/lib/types/equipment.ts
- [X] T018 [US1] Implement useWebSocket hook with auto-reconnect in apps/monitor/lib/hooks/useWebSocket.ts
- [X] T019 [US1] Implement getEquipmentColor mapping function in apps/monitor/lib/utils.ts
- [X] T020 [P] [US1] Create EquipmentStatusBox component in apps/monitor/components/EquipmentStatusBox.tsx
- [X] T021 [US1] Create EquipmentLayout component with 17 status boxes in apps/monitor/components/EquipmentLayout.tsx
- [X] T022 [US1] Add equipment layout background image to apps/monitor/public/equipment-layout.png
- [X] T023 [US1] Implement main Monitor page with WebSocket connection in apps/monitor/app/page.tsx
- [X] T024 [US1] Add WebSocket connection status indicator in apps/monitor/app/page.tsx
- [X] T025 [US1] Implement reconnection logic (3s interval, 5 retries) in apps/monitor/lib/hooks/useWebSocket.ts
- [X] T026 [US1] Add error handling for WebSocket failures in apps/monitor/app/page.tsx
- [X] T027 [US1] Create global CSS for equipment status colors in apps/monitor/app/globals.css
- [X] T028 [US1] Test WebSocket connection and equipment status display

**Checkpoint**: User Story 1 완료 - WebSocket 연결 및 17개 설비 실시간 상태 모니터링 가능

---

## Phase 4: User Story 2 - 설비별 알람 통계 조회 (Priority: P2)

**Goal**: 17개 설비별 알람 발생 건수와 일반 건수를 Oracle DB에서 조회하여 상단 그리드에 표시하고, 10초 주기로 자동 갱신합니다.

**Independent Test**: 페이지 로드 시 상단 그리드에 17개 설비별 알람 통계가 표시되고, 10초마다 자동으로 갱신되는지 확인합니다. Oracle DB에 새 알람 데이터를 추가한 후 10초 후 그리드가 업데이트되는지 테스트합니다.

### Implementation for User Story 2

- [X] T029 [P] [US2] Create AlarmStatistics type definition in apps/monitor/lib/types/alarm.ts
- [X] T030 [P] [US2] Create Axios API client for alarms in apps/monitor/lib/api/alarms.ts
- [X] T031 [US2] Implement getAlarmStatistics API function in apps/monitor/lib/api/alarms.ts
- [X] T032 [P] [US2] Create EquipmentGrid component for alarm statistics in apps/monitor/components/EquipmentGrid.tsx
- [X] T033 [US2] Add 10-second auto-refresh logic to EquipmentGrid component
- [X] T034 [US2] Add C/Time indicator (10초) to EquipmentGrid component
- [X] T035 [US2] Integrate EquipmentGrid into main Monitor page in apps/monitor/app/page.tsx
- [X] T036 [US2] Add error handling for Oracle DB connection failure in EquipmentGrid component
- [X] T037 [US2] Test alarm statistics display and 10-second auto-refresh

**Checkpoint**: User Story 2 완료 - 설비별 알람 통계 조회 및 자동 갱신 가능

---

## Phase 5: User Story 3 - 최근 알람 목록 조회 (Priority: P3)

**Goal**: 최근 발생한 5개 알람의 발생 시간과 메시지를 Oracle DB에서 조회하여 하단 우측에 표시하고, 10초 주기로 자동 갱신합니다.

**Independent Test**: 페이지 로드 시 하단 우측 테이블에 최근 5개 알람이 시간 역순으로 표시되고, 10초마다 자동으로 갱신되는지 확인합니다. 새 알람이 발생한 후 10초 후 목록 최상단에 추가되는지 테스트합니다.

### Implementation for User Story 3

- [X] T038 [P] [US3] Create Alarm type definition in apps/monitor/lib/types/alarm.ts
- [X] T039 [P] [US3] Implement getRecentAlarms API function in apps/monitor/lib/api/alarms.ts
- [X] T040 [P] [US3] Create AlarmList component for recent 5 alarms in apps/monitor/components/AlarmList.tsx
- [X] T041 [US3] Add 10-second auto-refresh logic to AlarmList component
- [X] T042 [US3] Format occurred_at timestamp to HH:MM in AlarmList component
- [X] T043 [US3] Integrate AlarmList into main Monitor page in apps/monitor/app/page.tsx
- [X] T044 [US3] Add error handling for Oracle DB connection failure in AlarmList component
- [X] T045 [US3] Test recent alarm list display and 10-second auto-refresh

**Checkpoint**: User Story 3 완료 - 최근 5개 알람 목록 조회 및 자동 갱신 가능

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 반응형 디자인, 성능 최적화, 문서화

- [X] T046 [P] Implement responsive layout (1280px breakpoint) in apps/monitor/app/page.tsx
- [X] T047 [P] Add loading spinners for initial data fetch in all components
- [X] T048 [P] Optimize WebSocket message parsing performance
- [X] T049 [P] Add environment variable configuration for API and WebSocket URLs
- [X] T050 [P] Create test script for Monitor UI in backend/src/scripts/test_monitor_ui.py
- [X] T051 [P] Update root package.json with dev:monitor script (if not done in T007)
- [X] T052 Validate all Success Criteria (SC-001 to SC-008) from spec.md
- [X] T053 Run quickstart.md validation and update documentation
- [X] T054 Update README.md with Feature 7 status and Monitor UI URL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
  - Or in parallel if team capacity allows
- **Polish (Phase 6)**: Depends on all user stories (Phase 3-5) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1 (independently testable)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on US1/US2 (independently testable)

### Within Each User Story

- Type definitions before API functions and components
- API functions before components that use them
- Components before page integration
- Core implementation before error handling and testing
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005, T006, T007 can run in parallel

**Phase 2 (Foundational)**: T009, T010, T011 can run in parallel after T008

**Phase 3 (User Story 1)**:
- T016, T017, T020 can run in parallel (different files)

**Phase 4 (User Story 2)**:
- T029, T030, T032 can run in parallel (different files)

**Phase 5 (User Story 3)**:
- T038, T039, T040 can run in parallel (different files)

**Phase 6 (Polish)**:
- T046, T047, T048, T049, T050, T051 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch type definitions and components in parallel:
Task: "Create Equipment type definitions in apps/monitor/lib/types/equipment.ts"
Task: "Create WebSocket message type definitions in apps/monitor/lib/types/equipment.ts"
Task: "Create EquipmentStatusBox component in apps/monitor/components/EquipmentStatusBox.tsx"

# After T016-T020 complete, proceed sequentially:
Task: "Implement useWebSocket hook with auto-reconnect"
Task: "Create EquipmentLayout component with 17 status boxes"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - CRITICAL
3. Complete Phase 3: User Story 1 (T016-T028)
4. **STOP and VALIDATE**: Test WebSocket connection and equipment status display
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Backend API 및 WebSocket 준비
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! 실시간 설비 상태 모니터링)
3. Add User Story 2 → Test independently → Deploy/Demo (알람 통계 추가)
4. Add User Story 3 → Test independently → Deploy/Demo (최근 알람 목록 추가)
5. Add Polish → Final validation and optimization

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done (after T015):
   - Developer A: User Story 1 (T016-T028)
   - Developer B: User Story 2 (T029-T037)
   - Developer C: User Story 3 (T038-T045)
3. Stories complete and integrate independently
4. Team completes Polish together (T046-T054)

---

## Task Summary

- **Total Tasks**: 54 tasks
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (User Story 1)**: 13 tasks
- **Phase 4 (User Story 2)**: 9 tasks
- **Phase 5 (User Story 3)**: 8 tasks
- **Phase 6 (Polish)**: 9 tasks

**Parallel Opportunities**: 18 tasks marked with [P] can run in parallel

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 28 tasks

**Independent Test Criteria**:
- US1: WebSocket 연결 및 설비 상태 5가지 색상 표시
- US2: 알람 통계 그리드 10초 자동 갱신
- US3: 최근 5개 알람 목록 10초 자동 갱신

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- No tests requested - manual testing using quickstart.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- python-oracledb MUST be used (NOT cx_Oracle) - verified in Phase 2
