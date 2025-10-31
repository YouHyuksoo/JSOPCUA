# Tasks: MC 3E ASCII 프로토콜 통신 및 Connection Pool

**Input**: Design documents from `/specs/002-mc3e-protocol-pool/`
**Prerequisites**: plan.md (완료), spec.md (완료), research.md (완료), data-model.md (완료), quickstart.md (완료)

**Tests**: 이 기능은 테스트가 명시적으로 요청되지 않았으므로 테스트 작성은 선택 사항입니다. 구현 중 필요에 따라 추가할 수 있습니다.

**Organization**: 작업은 User Story별로 그룹화되어 각 Story를 독립적으로 구현하고 테스트할 수 있도록 구성되었습니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 작업이 속한 User Story (예: US1, US2, US3)
- 설명에 정확한 파일 경로 포함

## Path Conventions

이 프로젝트는 **Web application** 구조를 사용합니다:
- Backend: `backend/src/`
- Tests: `backend/tests/`
- Config: `backend/config/`

---

## Phase 1: Setup (공유 인프라)

**목적**: 프로젝트 초기화 및 기본 구조 설정

- [X] T001 pymcprotocol 의존성 추가 in backend/requirements.txt
- [X] T002 [P] PLC 통신 패키지 디렉토리 생성 backend/src/plc/
- [X] T003 [P] 테스트 디렉토리 구조 생성 backend/tests/unit/, backend/tests/integration/

---

## Phase 2: Foundational (필수 선행 작업)

**목적**: 모든 User Story가 의존하는 핵심 인프라 구현

**⚠️ 중요**: 이 Phase가 완료되어야 User Story 작업을 시작할 수 있습니다

- [X] T004 PLC 통신 데이터 모델 정의 in backend/src/plc/models.py
- [X] T005 [P] 로깅 설정 및 유틸리티 함수 구현 in backend/src/plc/__init__.py
- [X] T006 [P] PLC 연결 예외 클래스 정의 in backend/src/plc/exceptions.py

**Checkpoint**: 기초 구조 완료 - User Story 구현 시작 가능

---

## Phase 3: User Story 1 - PLC 연결 및 단일 태그 읽기 (Priority: P1) 🎯 MVP

**목표**: Mitsubishi Q Series PLC와 TCP/IP로 연결하여 단일 태그 값을 읽을 수 있다.

**독립 테스트**: SQLite DB에 등록된 PLC 정보(IP, 포트)로 연결하고, 하나의 태그 주소(예: D100)를 읽어서 값을 반환하는지 확인. 연결 성공/실패 로그 확인.

### Implementation for User Story 1

- [X] T007 [P] [US1] MC 3E ASCII 클라이언트 기본 클래스 생성 in backend/src/plc/mc3e_client.py
- [X] T008 [US1] PLC 연결 메서드 구현 (connect, disconnect) in backend/src/plc/mc3e_client.py
- [X] T009 [US1] 단일 태그 읽기 메서드 구현 (read_single) in backend/src/plc/mc3e_client.py
- [X] T010 [US1] 타임아웃 처리 로직 추가 (socket timeout 5초) in backend/src/plc/mc3e_client.py
- [X] T011 [US1] 연결 실패 시 에러 처리 및 로깅 추가 in backend/src/plc/mc3e_client.py
- [X] T012 [US1] PLC 프로토콜 에러 파싱 및 변환 로직 구현 in backend/src/plc/mc3e_client.py
- [X] T013 [US1] SQLite에서 PLC 연결 정보 읽기 통합 in backend/src/scripts/test_plc_connection.py

**Checkpoint**: User Story 1이 독립적으로 동작하며 테스트 가능해야 함

---

## Phase 4: User Story 2 - Connection Pool을 통한 연결 재사용 (Priority: P1) 🎯 MVP

**목표**: PLC당 5개의 연결을 풀로 관리하여 매번 새로 연결하지 않고 기존 연결을 재사용한다.

**독립 테스트**: 동일한 PLC에 대해 10개의 연속 읽기 요청을 보내고, Connection Pool에서 연결이 재사용되는지 확인 (새 연결 생성이 최대 5개까지만 발생하는지 확인).

### Implementation for User Story 2

- [X] T014 [P] [US2] PooledConnection wrapper 클래스 구현 in backend/src/plc/connection_pool.py
- [X] T015 [P] [US2] ConnectionPool 클래스 기본 구조 생성 in backend/src/plc/connection_pool.py
- [X] T016 [US2] Queue 기반 연결 풀 관리 로직 구현 (max_size=5) in backend/src/plc/connection_pool.py
- [X] T017 [US2] get_connection 메서드 구현 (타임아웃 5초) in backend/src/plc/connection_pool.py
- [X] T018 [US2] return_connection 메서드 구현 in backend/src/plc/connection_pool.py
- [X] T019 [US2] close_all 메서드 구현 (모든 연결 종료) in backend/src/plc/connection_pool.py
- [X] T020 [US2] 유휴 연결 정리 로직 구현 (10분 타임아웃) in backend/src/plc/connection_pool.py
- [X] T021 [US2] 백그라운드 cleanup 스레드 추가 in backend/src/plc/connection_pool.py
- [X] T022 [US2] PoolManager 클래스 생성 (멀티 PLC 관리) in backend/src/plc/pool_manager.py
- [X] T023 [US2] PoolManager 초기화 로직 (SQLite에서 PLC 목록 로드) in backend/src/plc/pool_manager.py
- [X] T024 [US2] PoolManager read_single 메서드 구현 (Pool 사용) in backend/src/plc/pool_manager.py
- [X] T025 [US2] PoolManager shutdown 메서드 구현 in backend/src/plc/pool_manager.py

**Checkpoint**: User Story 1과 2가 모두 독립적으로 동작해야 함

---

## Phase 5: User Story 3 - 배치 읽기로 여러 태그 동시 조회 (Priority: P2)

**목표**: 한 번의 통신으로 10~50개의 태그를 배치로 읽어서 통신 횟수를 줄인다.

**독립 테스트**: PLC에 연속된 태그 주소(D100~D149)를 배치로 읽기 요청하고, 한 번의 통신으로 모든 값이 반환되는지 확인. 개별 읽기 대비 응답 시간 비교.

### Implementation for User Story 3

- [X] T026 [P] [US3] 태그 주소 파싱 유틸리티 함수 구현 in backend/src/plc/utils.py
- [X] T027 [US3] 연속 주소 그룹화 알고리즘 구현 in backend/src/plc/utils.py
- [X] T028 [US3] MC3EClient에 배치 읽기 메서드 추가 (read_batch) in backend/src/plc/mc3e_client.py
- [X] T029 [US3] pymcprotocol batchread_wordunits 통합 in backend/src/plc/mc3e_client.py
- [X] T030 [US3] 비연속 주소 처리 로직 (개별 읽기 폴백) in backend/src/plc/mc3e_client.py
- [X] T031 [US3] PoolManager read_batch 메서드 구현 in backend/src/plc/pool_manager.py
- [X] T032 [US3] 배치 읽기 성능 테스트 스크립트 작성 in backend/src/scripts/test_batch_read.py

**Checkpoint**: 모든 User Story (1, 2, 3)가 독립적으로 동작해야 함

---

## Phase 6: User Story 4 - 연결 끊김 감지 및 자동 재연결 (Priority: P2)

**목표**: PLC 연결이 끊어진 경우 이를 감지하고 자동으로 재연결을 시도한다.

**독립 테스트**: PLC 연결을 강제로 끊고 (네트워크 차단 또는 PLC 전원 끄기), 시스템이 연결 끊김을 감지하고 자동으로 재연결을 시도하는지 확인. 재연결 로그 확인.

### Implementation for User Story 4

- [X] T033 [P] [US4] 연결 상태 확인 메서드 구현 in backend/src/plc/mc3e_client.py
- [X] T034 [US4] 연결 끊김 감지 로직 추가 (socket exceptions 처리) in backend/src/plc/mc3e_client.py
- [X] T035 [US4] Exponential Backoff 재연결 로직 구현 (5s, 10s, 20s) in backend/src/plc/mc3e_client.py
- [X] T036 [US4] 재연결 시도 횟수 제한 (최대 3회) in backend/src/plc/mc3e_client.py
- [X] T037 [US4] 재연결 실패 시 PLC 비활성화 로직 in backend/src/plc/pool_manager.py
- [X] T038 [US4] 연결 상태 변경 이벤트 로깅 in backend/src/plc/mc3e_client.py
- [X] T039 [US4] PooledConnection에 에러 카운터 추가 in backend/src/plc/connection_pool.py

**Checkpoint**: 모든 User Story (1, 2, 3, 4)가 독립적으로 동작해야 함

---

## Phase 7: User Story 5 - 타임아웃 처리 및 에러 복구 (Priority: P3)

**목표**: PLC 응답이 지연되거나 에러가 발생했을 때 적절히 처리하고 복구한다.

**독립 테스트**: PLC 응답을 의도적으로 지연시키거나 (방화벽 규칙으로 지연 추가) 잘못된 응답을 보내고, 타임아웃과 에러 처리가 올바르게 작동하는지 확인.

### Implementation for User Story 5

- [X] T040 [P] [US5] Application level timeout 구현 (10초) in backend/src/plc/mc3e_client.py
- [X] T041 [US5] 타임아웃 발생 시 연결 정리 로직 in backend/src/plc/connection_pool.py
- [X] T042 [US5] 프로토콜 에러 응답 상세 파싱 in backend/src/plc/mc3e_client.py
- [X] T043 [US5] 연속 에러 임계값 처리 (3회 이상 시 재연결) in backend/src/plc/mc3e_client.py
- [X] T044 [US5] 에러 복구 로직 테스트 (실패 후 정상화 시나리오) in backend/src/scripts/test_error_recovery.py

**Checkpoint**: 모든 User Story가 독립적으로 동작하고 안정적임

---

## Phase 8: Polish & Cross-Cutting Concerns

**목적**: 여러 User Story에 걸친 개선 사항

- [X] T045 [P] RotatingFileHandler로 로그 파일 rotation 설정 in backend/src/plc/__init__.py
- [X] T046 [P] Connection Pool 상태 조회 메서드 구현 in backend/src/plc/pool_manager.py
- [X] T047 [P] 성능 메트릭 수집 로직 추가 (응답 시간, 풀 hit rate) in backend/src/plc/pool_manager.py
- [X] T048 quickstart.md 시나리오 검증 (5가지 시나리오 실행)
- [X] T049 [P] 코드 문서화 (docstrings 추가) in backend/src/plc/
- [X] T050 [P] 에러 메시지 한국어/영어 다국어 지원 in backend/src/plc/exceptions.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 시작 - 모든 User Story를 블로킹함
- **User Stories (Phase 3~7)**: Foundational 완료 후 시작 가능
  - User Story들은 병렬로 진행 가능 (팀 역량에 따라)
  - 또는 우선순위 순서대로 진행 (P1 → P2 → P3)
- **Polish (Phase 8)**: 필요한 User Story 모두 완료 후 시작

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 완료 후 시작 - 다른 Story 의존성 없음
- **User Story 2 (P1)**: Foundational 완료 후 시작 - US1과 통합되지만 독립 테스트 가능
- **User Story 3 (P2)**: Foundational 완료 후 시작 - US1, US2와 통합되지만 독립 테스트 가능
- **User Story 4 (P2)**: Foundational 완료 후 시작 - US2 Connection Pool을 확장
- **User Story 5 (P3)**: Foundational 완료 후 시작 - US1, US4와 통합되지만 독립 테스트 가능

### Within Each User Story

- 모델 → 서비스 → 엔드포인트
- 핵심 구현 → 통합
- Story 완료 후 다음 우선순위로 이동

### Parallel Opportunities

- Setup 단계의 모든 [P] 작업 병렬 실행 가능
- Foundational 단계의 모든 [P] 작업 병렬 실행 가능 (Phase 2 내에서)
- Foundational 완료 후 모든 User Story 병렬 시작 가능 (팀 역량 허용 시)
- 각 User Story 내 [P] 마크된 작업들 병렬 실행 가능
- 다른 팀원이 다른 User Story를 병렬로 작업 가능

---

## Parallel Example: User Story 1

```bash
# User Story 1의 병렬 작업:
Task T007: "MC 3E ASCII 클라이언트 기본 클래스 생성 in backend/src/plc/mc3e_client.py"

# 이후 순차 실행:
Task T008 → T009 → T010 → T011 → T012 → T013
```

## Parallel Example: User Story 2

```bash
# User Story 2의 병렬 작업:
Task T014: "PooledConnection wrapper 클래스 구현 in backend/src/plc/connection_pool.py"
Task T015: "ConnectionPool 클래스 기본 구조 생성 in backend/src/plc/connection_pool.py"

# 이후 순차 실행:
Task T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024 → T025
```

---

## Implementation Strategy

### MVP First (User Story 1 & 2만)

1. Phase 1 완료: Setup
2. Phase 2 완료: Foundational (중요 - 모든 Story 블로킹)
3. Phase 3 완료: User Story 1 (PLC 연결 및 단일 태그 읽기)
4. Phase 4 완료: User Story 2 (Connection Pool)
5. **중단 및 검증**: User Story 1, 2를 독립적으로 테스트
6. 준비되면 배포/데모

### Incremental Delivery

1. Setup + Foundational 완료 → 기반 완성
2. User Story 1 추가 → 독립 테스트 → 배포/데모
3. User Story 2 추가 → 독립 테스트 → 배포/데모 (MVP!)
4. User Story 3 추가 → 독립 테스트 → 배포/데모
5. User Story 4 추가 → 독립 테스트 → 배포/데모
6. User Story 5 추가 → 독립 테스트 → 배포/데모
7. 각 Story는 이전 Story를 깨뜨리지 않으면서 가치를 추가

### Parallel Team Strategy

여러 개발자가 작업하는 경우:

1. 팀이 Setup + Foundational을 함께 완료
2. Foundational 완료 후:
   - Developer A: User Story 1 & 2 (P1 - MVP)
   - Developer B: User Story 3 (P2)
   - Developer C: User Story 4 (P2)
   - Developer D: User Story 5 (P3)
3. 각 Story가 독립적으로 완료되고 통합됨

---

## Notes

- [P] 작업 = 다른 파일, 의존성 없음
- [Story] 레이블 = 추적성을 위해 특정 User Story에 매핑
- 각 User Story는 독립적으로 완료 및 테스트 가능해야 함
- 구현 전 로직 검증
- 각 작업 또는 논리적 그룹 후 커밋
- 각 checkpoint에서 Story를 독립적으로 검증하기 위해 중단
- 피해야 할 것: 모호한 작업, 동일 파일 충돌, Story 독립성을 깨는 교차 의존성

---

## Summary

- **총 작업 수**: 50개
- **User Story별 작업 수**:
  - Setup: 3개
  - Foundational: 3개
  - User Story 1: 7개
  - User Story 2: 12개
  - User Story 3: 7개
  - User Story 4: 7개
  - User Story 5: 5개
  - Polish: 6개
- **병렬 실행 기회**: 17개 작업에 [P] 마크
- **독립 테스트 기준**: 각 User Story별로 명시됨
- **권장 MVP 범위**: User Story 1 & 2 (P1 - 기본 연결 + Connection Pool)
