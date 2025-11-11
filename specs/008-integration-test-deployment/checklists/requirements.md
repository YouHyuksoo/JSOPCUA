# Requirements Checklist: 통합 테스트 및 배포 준비

**Feature**: 008-integration-test-deployment
**Created**: 2025-11-04

Complete each item before implementation begins. Mark items with [X] when complete.

---

## User Story 1: E2E 통합 테스트 (P1)

### Functional Requirements
- [ ] FR-001: PLC → 폴링 → Buffer → Oracle → UI 전체 플로우 1초 이내 지연 처리 검증
- [ ] FR-002: Feature 1-7 모든 주요 기능 자동 검증 스크립트 작성
- [ ] FR-003: PLC 시뮬레이터 구현 (실제 PLC 없이 테스트 가능)
- [ ] FR-004: HTML 리포트 생성 (성공/실패 건수, 실행 시간, 에러 로그)
- [ ] FR-005: CI/CD 파이프라인 통합 (exit code 기반)

### Acceptance Scenarios
- [ ] PLC → Oracle → UI 데이터 일관성 검증 (1초 이내 지연)
- [ ] 폴링 그룹 3개 동시 실행 시 에러 격리 확인
- [ ] Oracle DB 연결 실패 시 CSV 백업 자동 생성 확인
- [ ] Admin UI에서 태그 수정 후 폴링 그룹 재시작 시 즉시 반영 확인
- [ ] Monitor UI 3개 탭 동시 WebSocket 연결 시 동일 업데이트 확인

### Success Criteria
- [ ] SC-001: E2E 테스트 100% 자동화 및 Feature 1-7 검증
- [ ] SC-002: 데이터 일관성 검증 테스트 99% 성공률
- [ ] SC-003: 통합 테스트 실행 시간 5분 이내
- [ ] SC-004: CI/CD 파이프라인 통합 완료

---

## User Story 2: Docker 컨테이너화 (P2)

### Functional Requirements
- [ ] FR-006: 멀티스테이지 빌드로 이미지 크기 최소화
- [ ] FR-007: docker-compose.yml에 백엔드/Admin/Monitor 정의
- [ ] FR-008: 환경 변수 파일(.env.production)로 설정 외부화
- [ ] FR-009: Docker 볼륨으로 SQLite/로그/CSV 영구 저장
- [ ] FR-010: 헬스 체크 엔드포인트(/health) 구현

### Acceptance Scenarios
- [ ] `docker-compose up -d` 실행 시 3개 서비스 모두 healthy 상태
- [ ] 환경 변수 파일로 Oracle/PLC 설정 로드 확인
- [ ] Docker 이미지 크기 확인 (백엔드 <500MB, 프론트엔드 <200MB)
- [ ] 컨테이너 재시작 후 SQLite DB 및 로그 유지 확인

### Success Criteria
- [ ] SC-005: `docker-compose up` 2분 이내 전체 스택 시작
- [ ] SC-006: 이미지 크기 목표 달성 (백엔드 <500MB, 프론트엔드 <200MB)
- [ ] SC-007: Docker 볼륨으로 데이터 영구성 보장
- [ ] SC-008: 환경 변수로 3가지 환경(dev/staging/prod) 지원

---

## User Story 3: 운영 문서 (P3)

### Functional Requirements
- [ ] FR-011: docs/installation-guide.md - OS별 설치 절차
- [ ] FR-012: docs/configuration-guide.md - 환경 변수 설정
- [ ] FR-013: docs/troubleshooting.md - 10가지 에러 해결 방법
- [ ] FR-014: docs/backup-restore.md - 백업/복구 절차
- [ ] FR-015: docs/api-reference.md - REST API 36개 엔드포인트 문서화

### Acceptance Scenarios
- [ ] 신규 운영자가 installation-guide.md로 30분 이내 설치 성공
- [ ] configuration-guide.md로 5분 이내 환경 변수 수정 완료
- [ ] troubleshooting.md로 PLC 통신 에러 원인 파악
- [ ] backup-restore.md로 SQLite/CSV 백업 복구 절차 수행

### Success Criteria
- [ ] SC-009: 30분 이내 설치 및 첫 폴링 실행 성공
- [ ] SC-010: 10가지 에러 해결 방법 문서화
- [ ] SC-011: 36개 API 엔드포인트 예제와 함께 문서화
- [ ] SC-012: 백업/복구 절차 100% 데이터 복구 성공

---

## User Story 4: 성능 벤치마킹 (P3)

### Functional Requirements
- [ ] FR-016: 벤치마크 스크립트 - 폴링 지연, Oracle 처리량, WebSocket 지연 측정
- [ ] FR-017: 성능 측정 결과 CSV 저장 (타임스탬프, 메트릭명, 값)
- [ ] FR-018: 부하 테스트 도구(Locust/JMeter)로 동시 사용자 50명 시뮬레이션
- [ ] FR-019: 메모리 프로파일링 도구(memory_profiler)로 8시간 실행 메모리 누수 검증
- [ ] FR-020: 성능 목표 미달성 시 경고 메시지 및 exit code 1 반환

### Acceptance Scenarios
- [ ] 3,491개 태그, 10개 폴링 그룹 동시 실행 시 평균 지연 <1초 확인
- [ ] Oracle Writer 1,000+ values/sec 처리량 확인
- [ ] Monitor UI WebSocket 50개 연결 시 100ms 이내 업데이트 확인
- [ ] 8시간 연속 실행 시 메모리 <1GB 유지 확인

### Success Criteria
- [ ] SC-013: 평균 폴링 지연 <1초, 99 percentile <2초
- [ ] SC-014: Oracle Writer 1,000+ values/sec, 성공률 >99%
- [ ] SC-015: 8시간 실행 시 메모리 <1GB 유지

---

## 공통 요구사항

### File Structure
- [ ] FR-021: backend/src/scripts/integration_test/ 디렉토리에 테스트 스크립트 위치
- [ ] FR-022: 루트 디렉토리에 Dockerfile, docker-compose.yml 위치
- [ ] FR-023: docs/ 디렉토리에 Markdown 문서 위치
- [ ] FR-024: README.md에 Feature 8 상태 및 시스템 아키텍처 다이어그램 추가

### Edge Cases
- [ ] PLC 시뮬레이터 없이 Mock PLC 서버로 E2E 테스트
- [ ] Oracle DB 장시간 다운타임 시 CSV 백업 10,000개+ 재처리 시나리오
- [ ] Docker 네트워크 분리 시 CORS/WebSocket 연결 처리
- [ ] 로그 파일 1GB+ 시 로그 로테이션 및 압축 자동화
- [ ] 동일 호스트에서 dev/staging/prod 환경 동시 실행 시 포트 충돌 방지

---

## Sign-off

Before proceeding to `/speckit.plan`:
- [ ] All functional requirements are clear and testable
- [ ] All acceptance scenarios are realistic and measurable
- [ ] All success criteria have specific numeric targets
- [ ] All edge cases are documented
- [ ] User stories are independently testable
- [ ] Priorities are justified

**Reviewed by**: _______________  
**Date**: _______________
