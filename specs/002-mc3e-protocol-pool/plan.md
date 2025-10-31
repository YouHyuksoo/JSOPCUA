# Implementation Plan: MC 3E ASCII 프로토콜 통신 및 Connection Pool

**Branch**: `002-mc3e-protocol-pool` | **Date**: 2025-10-31 | **Spec**: [spec.md](./spec.md)

## Summary

Mitsubishi Q Series PLC와 MC 3E ASCII 프로토콜로 통신하는 Connection Pool 기반 통신 모듈 구현. PLC당 5개 연결을 재사용하여 태그 읽기 성능 최적화 (태그당 50ms 이하). pymcprotocol 라이브러리 사용, 배치 읽기, 자동 재연결, 타임아웃 처리 포함.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pymcprotocol (PLC 통신), queue (스레드 안전 큐), threading (멀티스레딩)
**Storage**: SQLite (Feature 1의 plc_connections, tags 테이블 활용)
**Testing**: pytest, unittest.mock (PLC 모킹), pytest-timeout
**Target Platform**: Linux/Windows server
**Project Type**: Web application (backend only for this feature)
**Performance Goals**: 태그당 평균 응답시간 50ms 이하, 배치 읽기 50개 태그 500ms 이내
**Constraints**: PLC당 최대 5개 동시 연결, 타임아웃 5초, 재연결 3회 시도
**Scale/Scope**: 최대 10개 PLC 동시 관리, PLC당 최대 500개 태그 지원

## Constitution Check

*Constitution 파일이 템플릿 상태이므로 이 프로젝트는 constitution 제약이 없습니다. 건너뜀.*

## Project Structure

### Documentation (this feature)

```text
specs/002-mc3e-protocol-pool/
├── plan.md              # 이 파일
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── plc/                    # 새로 추가 (Feature 2)
│   │   ├── __init__.py
│   │   ├── mc3e_client.py      # MC 3E ASCII 프로토콜 클라이언트
│   │   ├── connection_pool.py  # Connection Pool 관리
│   │   ├── pool_manager.py     # 멀티 PLC Pool 관리자
│   │   └── models.py           # PLC 통신 관련 데이터 모델
│   ├── database/               # 기존 (Feature 1)
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── sqlite_manager.py
│   └── scripts/                # 기존 (Feature 1)
│       └── test_plc_connection.py  # 새로 추가: PLC 연결 테스트 스크립트
├── tests/
│   ├── unit/
│   │   ├── test_mc3e_client.py
│   │   ├── test_connection_pool.py
│   │   └── test_pool_manager.py
│   └── integration/
│       └── test_plc_integration.py  # 실제 PLC 또는 시뮬레이터 필요
├── config/                     # 기존 (Feature 1)
│   ├── init_scada_db.sql
│   └── scada.db
└── requirements.txt            # pymcprotocol 추가
```

**Structure Decision**: Web application 구조 유지 (Feature 1에서 설정됨). backend/src/plc/ 패키지를 새로 추가하여 PLC 통신 로직 캡슐화. SQLite 데이터베이스는 기존 구조 활용.

## Complexity Tracking

*Constitution 제약이 없으므로 해당 없음*

