# Feature Specification: 통합 테스트 및 배포 준비

**Feature Branch**: `008-integration-test-deployment`
**Created**: 2025-11-04
**Status**: Draft
**Input**: Feature 8 - 전체 SCADA 시스템의 통합 테스트, 성능 검증, Docker 컨테이너화, 배포 문서화

## User Scenarios & Testing

### User Story 1 - End-to-End 통합 테스트 (Priority: P1) 🎯 MVP

운영팀이 전체 SCADA 시스템(PLC 통신 → 데이터 수집 → Oracle 저장 → Admin/Monitor UI 조회)이 실제 운영 환경에서 안정적으로 동작하는지 검증하고자 합니다. 모든 Feature(1-7)가 통합된 상태에서 실제 시나리오를 재현하여 테스트합니다.

**Why this priority**: 전체 시스템이 통합된 상태에서 정상 동작하지 않으면 운영이 불가능합니다. 이는 배포 전 필수 검증 단계입니다.

**Independent Test**: PLC 시뮬레이터를 실행하고, 백엔드 서버를 시작한 후, Admin UI에서 폴링 그룹을 시작합니다. 30초 후 Monitor UI에서 실시간 설비 상태가 업데이트되고, Oracle DB에 데이터가 저장되며, 알람이 정상적으로 표시되는지 확인합니다. 이 테스트는 다른 User Story와 독립적으로 수행 가능하며, 시스템의 핵심 가치인 "실시간 데이터 수집 및 모니터링"을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 모든 Feature(1-7) 구현 완료, **When** PLC 연결 → 폴링 시작 → 데이터 수집 → Oracle 저장 → UI 조회 전체 플로우 실행, **Then** 각 단계가 1초 이내 지연으로 성공하고 데이터가 일관성 있게 전달됨
2. **Given** 폴링 그룹 3개 동시 실행 중, **When** 한 PLC 연결 실패, **Then** 해당 그룹만 에러 상태로 변경되고 다른 그룹은 정상 동작 유지
3. **Given** Oracle DB 연결 실패, **When** 폴링 데이터 수집 계속 진행, **Then** Circular Buffer에 데이터가 쌓이고 CSV 백업 파일이 생성됨
4. **Given** Admin UI에서 태그 수정, **When** 폴링 그룹 재시작, **Then** 변경된 태그 설정이 즉시 반영되어 올바른 PLC 주소에서 데이터 수집
5. **Given** Monitor UI 3개 브라우저 탭 동시 접속, **When** WebSocket 연결, **Then** 모든 탭이 1초 주기로 동일한 설비 상태 업데이트 수신

---

### User Story 2 - Docker 컨테이너화 및 배포 준비 (Priority: P2)

운영팀이 SCADA 시스템을 Docker 컨테이너로 패키징하여 개발/스테이징/프로덕션 환경에 일관되게 배포하고자 합니다. Docker Compose를 사용하여 전체 스택(Backend, Admin, Monitor)을 한 번에 실행할 수 있어야 합니다.

**Why this priority**: Docker 컨테이너화는 배포 자동화와 환경 일관성을 보장하며, 운영 환경에서 필수적입니다.

**Independent Test**: `docker-compose up` 명령어 하나로 백엔드, Admin UI, Monitor UI가 모두 시작되고, 각 서비스가 정상적으로 통신하는지 확인합니다. 이 테스트는 US1과 독립적으로 수행 가능하며, 컨테이너 이미지 빌드 및 네트워크 설정을 검증합니다.

**Acceptance Scenarios**:

1. **Given** Dockerfile 및 docker-compose.yml 작성 완료, **When** `docker-compose up -d` 실행, **Then** 3개 서비스(backend, admin, monitor)가 모두 healthy 상태로 시작되고 서로 통신 가능
2. **Given** 환경 변수 파일(.env.production), **When** Docker Compose로 배포, **Then** 모든 서비스가 올바른 환경 변수(Oracle 연결 정보, PLC IP 등)를 로드하여 실행
3. **Given** Docker 이미지 빌드, **When** 이미지 크기 확인, **Then** 백엔드 이미지 <500MB, 프론트엔드 이미지 <200MB
4. **Given** Docker 볼륨 설정(SQLite DB, 로그), **When** 컨테이너 재시작, **Then** 데이터 및 로그가 유지됨

---

### User Story 3 - 운영 문서 및 배포 가이드 (Priority: P3)

신규 운영자가 SCADA 시스템을 처음 설치하고 운영할 때 필요한 모든 문서(설치 가이드, 설정 가이드, 트러블슈팅)를 제공하여 별도 교육 없이 시스템을 배포할 수 있어야 합니다.

**Why this priority**: 문서가 없으면 운영팀이 시스템을 유지보수할 수 없습니다. 장기적인 운영 효율성을 위해 필수입니다.

**Independent Test**: 신규 운영자가 docs/deployment-guide.md 문서만 보고 30분 이내에 시스템을 설치하고 첫 번째 폴링 그룹을 실행할 수 있는지 확인합니다. 이 테스트는 US1, US2와 독립적으로 수행 가능하며, 문서의 완전성과 명확성을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 새로운 서버 환경, **When** docs/installation-guide.md 따라 설치, **Then** 30분 이내에 전체 스택 실행 성공
2. **Given** Oracle 연결 정보 변경 필요, **When** docs/configuration-guide.md 참조, **Then** 5분 이내에 환경 변수 수정 및 서비스 재시작 완료
3. **Given** PLC 통신 에러 발생, **When** docs/troubleshooting.md 참조, **Then** 에러 원인 파악 및 해결 방법 확인
4. **Given** 백업 및 복구 필요, **When** docs/backup-restore.md 참조, **Then** SQLite DB 및 CSV 백업 파일 복구 절차 수행

---

### User Story 4 - 성능 벤치마킹 및 최적화 (Priority: P3)

운영팀이 SCADA 시스템의 성능 지표(폴링 지연, Oracle 쓰기 처리량, WebSocket 업데이트 지연)를 측정하고 목표 성능을 달성하는지 검증하고자 합니다.

**Why this priority**: 성능 지표가 명확하지 않으면 시스템 확장 시 병목 지점을 파악할 수 없습니다. 운영 안정성을 위해 필요합니다.

**Independent Test**: 벤치마크 스크립트를 실행하여 3,491개 태그를 10개 폴링 그룹으로 동시에 폴링할 때, 평균 폴링 지연 <1초, Oracle 쓰기 처리량 >1,000 values/sec, WebSocket 업데이트 지연 <100ms인지 확인합니다. 이 테스트는 다른 User Story와 독립적으로 수행 가능하며, 시스템의 확장 가능성을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 3,491개 태그, 10개 폴링 그룹 동시 실행, **When** 1분간 성능 측정, **Then** 평균 폴링 지연 <1초, 99 percentile <2초
2. **Given** Oracle Writer 동작 중, **When** 1분간 처리량 측정, **Then** 평균 1,000+ values/sec 처리, 배치 쓰기 성공률 >99%
3. **Given** Monitor UI WebSocket 연결 50개, **When** 설비 상태 업데이트, **Then** 모든 클라이언트가 100ms 이내에 업데이트 수신
4. **Given** 8시간 연속 실행, **When** 메모리 사용량 모니터링, **Then** 메모리 누수 없음, 백엔드 메모리 <1GB 유지

---

### Edge Cases

- **PLC 시뮬레이터 없이 테스트**: Mock PLC 서버를 구현하여 실제 PLC 없이도 E2E 테스트 가능
- **Oracle DB 장시간 다운타임**: CSV 백업 파일이 10,000개 이상 쌓였을 때 Oracle 복구 후 재처리 시나리오
- **Docker 네트워크 분리**: Admin UI와 Monitor UI를 다른 Docker 네트워크에 배포했을 때 CORS 및 WebSocket 연결 처리
- **대용량 로그 파일**: 로그 파일이 1GB 이상일 때 로그 로테이션 및 압축 자동화
- **동시 배포 시나리오**: 개발/스테이징/프로덕션 환경이 동일한 호스트에서 실행될 때 포트 충돌 방지

## Requirements

### Functional Requirements

#### E2E 통합 테스트 (US1)
- **FR-001**: 시스템은 PLC 연결 → 폴링 → Circular Buffer → Oracle Writer → UI 조회까지 전체 플로우를 1초 이내 지연으로 처리해야 함
- **FR-002**: E2E 테스트 스크립트는 Feature 1-7의 모든 주요 기능을 자동으로 검증해야 함
- **FR-003**: 통합 테스트는 PLC 시뮬레이터를 사용하여 실제 PLC 없이 실행 가능해야 함
- **FR-004**: 테스트 결과는 HTML 리포트 형식으로 생성되어야 함 (성공/실패 건수, 실행 시간, 에러 로그)
- **FR-005**: 통합 테스트는 CI/CD 파이프라인에 통합 가능해야 함 (exit code 0: 성공, 1: 실패)

#### Docker 컨테이너화 (US2)
- **FR-006**: Dockerfile은 멀티스테이지 빌드를 사용하여 이미지 크기를 최소화해야 함
- **FR-007**: docker-compose.yml은 백엔드, Admin UI, Monitor UI를 정의하고 서비스 간 네트워크를 설정해야 함
- **FR-008**: 환경 변수 파일(.env.production)로 Oracle 연결 정보, PLC IP, 포트 등을 외부화해야 함
- **FR-009**: Docker 볼륨을 사용하여 SQLite DB, 로그 파일, CSV 백업을 영구 저장해야 함
- **FR-010**: 헬스 체크 엔드포인트(/health)를 구현하여 Docker Compose의 healthcheck와 통합해야 함

#### 운영 문서 (US3)
- **FR-011**: docs/installation-guide.md는 OS별(Ubuntu, CentOS, Windows Server) 설치 절차를 포함해야 함
- **FR-012**: docs/configuration-guide.md는 환경 변수, SQLite 경로, Oracle 연결 정보 설정 방법을 포함해야 함
- **FR-013**: docs/troubleshooting.md는 자주 발생하는 10가지 에러와 해결 방법을 포함해야 함
- **FR-014**: docs/backup-restore.md는 SQLite DB 및 Oracle 데이터 백업/복구 절차를 포함해야 함
- **FR-015**: docs/api-reference.md는 모든 REST API 엔드포인트(29개 + 알람 3개 + 버퍼 4개)를 문서화해야 함

#### 성능 벤치마킹 (US4)
- **FR-016**: 벤치마크 스크립트는 폴링 지연, Oracle 쓰기 처리량, WebSocket 지연을 자동 측정해야 함
- **FR-017**: 성능 측정 결과는 CSV 파일로 저장되어야 함 (타임스탬프, 메트릭명, 값)
- **FR-018**: 부하 테스트 도구(Locust 또는 JMeter)를 사용하여 동시 사용자 50명 시나리오를 시뮬레이션해야 함
- **FR-019**: 메모리 프로파일링 도구(memory_profiler)를 사용하여 8시간 실행 시 메모리 누수를 검증해야 함
- **FR-020**: 성능 목표 미달성 시 경고 메시지를 출력하고 exit code 1을 반환해야 함

#### 공통 요구사항
- **FR-021**: 모든 테스트 스크립트는 backend/src/scripts/integration_test/ 디렉토리에 위치해야 함
- **FR-022**: 모든 Docker 파일은 루트 디렉토리에 위치해야 함 (Dockerfile, docker-compose.yml)
- **FR-023**: 모든 문서는 docs/ 디렉토리에 위치하고 Markdown 형식으로 작성되어야 함
- **FR-024**: README.md는 Feature 8 완료 상태를 반영하고 전체 시스템 아키텍처 다이어그램을 포함해야 함

### Key Entities

- **IntegrationTestResult**: E2E 테스트 실행 결과 (test_name, status, duration, error_message)
- **PerformanceMetric**: 성능 측정 데이터 (timestamp, metric_name, value, unit)
- **DockerService**: Docker Compose 서비스 정의 (service_name, image, ports, volumes, environment)
- **DeploymentEnvironment**: 배포 환경 설정 (env_name, oracle_dsn, plc_ips, admin_port, monitor_port)

## Success Criteria

### Measurable Outcomes

#### E2E 통합 테스트 (US1)
- **SC-001**: 전체 플로우 E2E 테스트가 100% 자동화되어 실행되고 모든 Feature(1-7) 주요 기능을 검증함
- **SC-002**: PLC → Oracle → UI 데이터 일관성 검증 테스트가 99% 이상 성공률을 달성함
- **SC-003**: 통합 테스트 실행 시간이 5분 이내로 완료됨
- **SC-004**: CI/CD 파이프라인에 통합되어 코드 푸시 시 자동 테스트 실행됨

#### Docker 컨테이너화 (US2)
- **SC-005**: `docker-compose up` 명령어로 전체 스택이 2분 이내에 시작되고 모든 서비스가 healthy 상태가 됨
- **SC-006**: Docker 이미지 크기가 목표 크기 이내 (백엔드 <500MB, 프론트엔드 <200MB)
- **SC-007**: Docker 볼륨을 사용하여 컨테이너 재시작 후에도 SQLite DB 및 로그가 유지됨
- **SC-008**: 환경 변수 파일(.env.production)로 3가지 환경(dev/staging/prod)을 지원함

#### 운영 문서 (US3)
- **SC-009**: 신규 운영자가 docs/installation-guide.md만 보고 30분 이내에 시스템을 설치하고 첫 번째 폴링 실행에 성공함
- **SC-010**: 자주 발생하는 10가지 에러가 docs/troubleshooting.md에 해결 방법과 함께 문서화됨
- **SC-011**: 모든 REST API 엔드포인트(36개)가 docs/api-reference.md에 예제 요청/응답과 함께 문서화됨
- **SC-012**: 백업/복구 절차를 docs/backup-restore.md에 따라 수행 시 100% 데이터 복구 성공함

#### 성능 벤치마킹 (US4)
- **SC-013**: 3,491개 태그, 10개 폴링 그룹 동시 실행 시 평균 폴링 지연 <1초, 99 percentile <2초
- **SC-014**: Oracle Writer 처리량이 1,000+ values/sec 달성하고 배치 쓰기 성공률 >99%
- **SC-015**: 8시간 연속 실행 시 백엔드 메모리 사용량 <1GB 유지 (메모리 누수 없음)
