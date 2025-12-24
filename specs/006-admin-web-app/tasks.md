# Tasks: Next.js 관리 웹 애플리케이션

**Feature**: 006-admin-web-app | **Branch**: 006-admin-web-app | **Date**: 2025-11-02

## Task Summary

**Total Tasks**: 87
**User Stories**: 4 (P1: 마스터 데이터 관리, P2: 폴링 제어, P3: 시스템 모니터링, P4: 로그 조회)
**Phases**: 7 (Setup, Foundational, US1, US2, US3, US4, Polish)
**Parallel Opportunities**: 45 tasks marked [P]

## Dependencies

**User Story Completion Order**:
1. Phase 1 (Setup) → Phase 2 (Foundational) - MUST complete before user stories
2. Phase 3 (US1) - Can start after Phase 2
3. Phase 4 (US2) - Can start after Phase 2, independent
4. Phase 5 (US3) - Can start after Phase 2, independent
5. Phase 6 (US4) - Can start after Phase 2, independent
6. Phase 7 (Polish) - After all user stories

**MVP Scope**: Phase 3 (US1) only

## Implementation Strategy

**Incremental Delivery**: US1 → US2 → US3 → US4
**Parallel Execution**: Tasks marked [P] can run in parallel

---

## Phase 1: Setup

- [ ] T001 Install shadcn/ui: npx shadcn-ui@latest init in apps/admin/
- [ ] T002 Install dependencies: axios zod react-hook-form papaparse
- [ ] T003 [P] Add button: npx shadcn-ui@latest add button
- [ ] T004 [P] Add card: npx shadcn-ui@latest add card
- [ ] T005 [P] Add table: npx shadcn-ui@latest add table
- [ ] T006 [P] Add dialog: npx shadcn-ui@latest add dialog
- [ ] T007 [P] Add toast: npx shadcn-ui@latest add toast
- [ ] T008 [P] Add select: npx shadcn-ui@latest add select
- [ ] T009 [P] Add input: npx shadcn-ui@latest add input
- [ ] T010 [P] Add textarea: npx shadcn-ui@latest add textarea
- [ ] T011 [P] Add label: npx shadcn-ui@latest add label
- [ ] T012 [P] Add form: npx shadcn-ui@latest add form
- [ ] T013 [P] Add checkbox: npx shadcn-ui@latest add checkbox
- [ ] T014 [P] Add tabs: npx shadcn-ui@latest add tabs
- [ ] T015 [P] Add badge: npx shadcn-ui@latest add badge
- [ ] T016 [P] Add alert: npx shadcn-ui@latest add alert
- [ ] T017 [P] Add pagination: npx shadcn-ui@latest add pagination
- [ ] T018 [P] Add separator: npx shadcn-ui@latest add separator
- [ ] T019 [P] Add skeleton: npx shadcn-ui@latest add skeleton

---

## Phase 2: Foundational

- [ ] T020 Create API client in apps/admin/lib/api/client.ts
- [ ] T021 Add error interceptor to API client
- [ ] T022 [P] Create Line types in apps/admin/lib/types/line.ts
- [ ] T023 [P] Create Process types in apps/admin/lib/types/process.ts
- [ ] T024 [P] Create PLC types in apps/admin/lib/types/plc.ts
- [ ] T025 [P] Create Tag types in apps/admin/lib/types/tag.ts
- [ ] T026 [P] Create PollingGroup types in apps/admin/lib/types/polling-group.ts
- [ ] T027 [P] Create SystemStatus types in apps/admin/lib/types/system-status.ts
- [ ] T028 [P] Create Log types in apps/admin/lib/types/log.ts
- [ ] T029 Create PaginatedResponse in apps/admin/lib/types/common.ts
- [ ] T030 Update layout.tsx with ToastProvider in apps/admin/app/layout.tsx
- [ ] T031 Create nav component in apps/admin/components/nav.tsx
- [ ] T032 Update homepage in apps/admin/app/page.tsx

---

## Phase 3: US1 - 라인/공정/PLC/태그 관리

- [ ] T033 [P] [US1] Create Line API in apps/admin/lib/api/lines.ts
- [ ] T034 [P] [US1] Create Line validator in apps/admin/lib/validators.ts
- [ ] T035 [US1] Create LineForm in apps/admin/components/line-form.tsx
- [ ] T036 [US1] Create lines list at apps/admin/app/lines/page.tsx
- [ ] T037 [US1] Create line create at apps/admin/app/lines/new/page.tsx
- [ ] T038 [US1] Create line edit at apps/admin/app/lines/[id]/page.tsx
- [ ] T039 [P] [US1] Create Process API in apps/admin/lib/api/processes.ts
- [ ] T040 [P] [US1] Create Process validator in apps/admin/lib/validators.ts
- [ ] T041 [US1] Create ProcessForm in apps/admin/components/process-form.tsx
- [ ] T042 [US1] Create processes list at apps/admin/app/processes/page.tsx
- [ ] T043 [US1] Create process create at apps/admin/app/processes/new/page.tsx
- [ ] T044 [US1] Create process edit at apps/admin/app/processes/[id]/page.tsx
- [ ] T045 [P] [US1] Create PLC API in apps/admin/lib/api/plcs.ts
- [ ] T046 [P] [US1] Create PLC validator in apps/admin/lib/validators.ts
- [ ] T047 [US1] Create PLCForm in apps/admin/components/plc-form.tsx
- [ ] T048 [US1] Create plcs list at apps/admin/app/plcs/page.tsx
- [ ] T049 [US1] Create plc create at apps/admin/app/plcs/new/page.tsx
- [ ] T050 [US1] Create plc edit at apps/admin/app/plcs/[id]/page.tsx
- [ ] T051 [P] [US1] Create Tag API in apps/admin/lib/api/tags.ts
- [ ] T052 [P] [US1] Create Tag validator in apps/admin/lib/validators.ts
- [ ] T053 [US1] Create TagForm in apps/admin/components/tag-form.tsx
- [ ] T054 [US1] Create CSVUpload in apps/admin/components/csv-upload.tsx
- [ ] T055 [US1] Create tags list at apps/admin/app/tags/page.tsx
- [ ] T056 [US1] Create tag create at apps/admin/app/tags/new/page.tsx
- [ ] T057 [US1] Create tag edit at apps/admin/app/tags/[id]/page.tsx
- [ ] T058 [US1] Create tag upload at apps/admin/app/tags/upload/page.tsx
- [ ] T059 [US1] Create DeleteDialog in apps/admin/components/delete-confirm-dialog.tsx

---

## Phase 4: US2 - 폴링 그룹 제어

- [ ] T060 [P] [US2] Create PollingGroup API in apps/admin/lib/api/polling-groups.ts
- [ ] T061 [P] [US2] Create PollingGroup validator in apps/admin/lib/validators.ts
- [ ] T062 [US2] Create PollingGroupForm in apps/admin/components/polling-group-form.tsx
- [ ] T063 [US2] Create polling-groups list at apps/admin/app/polling-groups/page.tsx
- [ ] T064 [US2] Create polling-group create at apps/admin/app/polling-groups/new/page.tsx
- [ ] T065 [US2] Create polling-group edit at apps/admin/app/polling-groups/[id]/page.tsx
- [ ] T066 [US2] Add Start All/Stop All to polling-groups list page

---

## Phase 5: US3 - 시스템 모니터링

- [ ] T067 [P] [US3] Create SystemStatus API in apps/admin/lib/api/system-status.ts
- [ ] T068 [US3] Create SystemStatusCard in apps/admin/components/system-status-card.tsx
- [ ] T069 [US3] Create PLCStatusCard in apps/admin/components/plc-status-card.tsx
- [ ] T070 [US3] Create BufferStatusCard in apps/admin/components/buffer-status-card.tsx
- [ ] T071 [US3] Create OracleWriterCard in apps/admin/components/oracle-writer-card.tsx
- [ ] T072 [US3] Create dashboard at apps/admin/app/dashboard/page.tsx with 5s refresh
- [ ] T073 [US3] Add threshold warnings to dashboard cards

---

## Phase 6: US4 - 로그 조회

- [ ] T074 [P] [US4] Create Logs API in apps/admin/lib/api/logs.ts
- [ ] T075 [US4] Create LogFilter in apps/admin/components/log-filter.tsx
- [ ] T076 [US4] Create logs page at apps/admin/app/logs/page.tsx
- [ ] T077 [US4] Add keyword highlighting in log viewer
- [ ] T078 [US4] Add CSV download button to logs page

---

## Phase 7: Polish

- [ ] T079 [P] Add loading spinners with Skeleton
- [ ] T080 [P] Add responsive Tailwind classes (mobile/tablet/desktop)
- [ ] T081 [P] Add error boundaries to pages
- [ ] T082 [P] Add form validation error display
- [ ] T083 [P] Test mobile viewport (375px)
- [ ] T084 Update homepage with all page links
- [ ] T085 Create apps/admin/README.md
- [ ] T086 Test full CRUD workflow end-to-end
- [ ] T087 Commit Feature 6 completion

---

**Format**: All tasks follow 
**Ready for /speckit.implement**
