# Implementation Plan: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정

**Branch**: `001-project-structure-sqlite-setup` | **Date**: 2025-10-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-project-structure-sqlite-setup/spec.md`

## Summary

JSScada SCADA 시스템의 기반 인프라 구축: 3개 주요 디렉토리(backend/, frontend-admin/, frontend-monitor/)와 SQLite 로컬 데이터베이스 스키마 생성. 라인, 공정, PLC 연결, 태그, 폴링 그룹 테이블을 포함한 계층적 데이터 구조 설계. 14자리 설비 코드 체계 지원 및 3,491개 이상 태그 저장 가능. CSV 일괄 등록 기능 포함.

## Technical Context

**Language/Version**:
- Python 3.11+ (백엔드)
- TypeScript 5.3+ (프론트엔드)
- Node.js 20+ (프론트엔드 런타임)

**Primary Dependencies**:
- SQLite 3.40+ (로컬 설정 데이터베이스)
- Next.js 14+ (프론트엔드 프레임워크)
- Python 표준 라이브러리 sqlite3 모듈

**Storage**: SQLite 파일 기반 데이터베이스 (backend/config/scada.db)

**Testing**:
- Python: pytest (백엔드 테스트)
- TypeScript: Jest (프론트엔드 테스트)
- 수동 검증: SQLite CLI를 통한 스키마 검증

**Target Platform**:
- Windows 10/11, Linux (Ubuntu 20.04+)
- 로컬 개발 환경

**Project Type**: Web (백엔드 + 2개 프론트엔드)

**Performance Goals**:
- 데이터베이스 초기화: 10초 이내
- 3,491개 태그 CSV 가져오기: 5분 이내
- 쿼리 응답: 100ms 이내

**Constraints**:
- SQLite 파일 크기: 초기 50MB 이하 (3,491개 태그 기준)
- 단일 서버 환경 (원격 DB 접근 불필요)
- UTF-8 인코딩 필수 (한글, 특수문자 지원)

**Scale/Scope**:
- 초기 3,491개 태그
- 확장성: 최대 10,000개 태그
- 5개 핵심 테이블 (lines, processes, plc_connections, tags, polling_groups)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS - Constitution 파일이 템플릿 상태이므로 특정 원칙 검증 불필요

**Notes**:
- 프로젝트에 특정 Constitution 원칙이 정의되지 않았음
- 향후 `/speckit.constitution` 명령으로 프로젝트 원칙 정의 가능
- 현재는 일반적인 소프트웨어 개발 best practice 적용

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── sqlite_manager.py      # SQLite 연결 및 쿼리 관리
│   │   └── models.py               # 데이터 모델 정의
│   ├── scripts/
│   │   ├── init_database.py        # DB 초기화 스크립트
│   │   ├── import_tags_csv.py      # CSV 가져오기
│   │   └── create_sample_data.py   # 샘플 데이터 생성
│   └── __init__.py
├── config/
│   ├── scada.db                    # SQLite 데이터베이스 파일 (생성됨)
│   └── init_scada_db.sql           # 스키마 초기화 SQL
├── logs/                           # 로그 디렉토리 (빈 폴더)
├── tests/
│   ├── test_database.py            # 데이터베이스 테스트
│   └── test_csv_import.py          # CSV 가져오기 테스트
├── requirements.txt                # Python 패키지 목록
├── .env.example                    # 환경 변수 템플릿
└── README.md                       # 백엔드 README

frontend-admin/
├── app/
│   ├── layout.tsx                  # 루트 레이아웃
│   ├── page.tsx                    # 홈 페이지
│   └── globals.css                 # 글로벌 스타일
├── components/
│   └── ui/                         # shadcn/ui 컴포넌트 (향후 추가)
├── lib/
│   └── utils.ts                    # 유틸리티 함수
├── public/                         # 정적 파일
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── README.md                       # 관리 웹 README

frontend-monitor/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── ui/
├── lib/
│   └── utils.ts
├── public/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── README.md                       # 모니터링 웹 README

docs/                               # 프로젝트 문서 (기존 유지)
├── 01-PROJECT-OVERVIEW.md
├── 02-SYSTEM-ARCHITECTURE.md
└── 03-DATABASE-SCHEMA.md

.gitignore                          # Git 무시 파일
CLAUDE.md                           # Claude Code 가이드 (기존)
README.md                           # 프로젝트 루트 README
```

**Structure Decision**: Web application with 1 backend + 2 frontends

docs 폴더의 기존 문서를 기반으로 3계층 구조를 선택:
1. **backend/** - Python 3.11+ 기반 SCADA 백엔드 (SQLite 관리)
2. **frontend-admin/** - Next.js 14+ 관리 웹 (설정, 제어)
3. **frontend-monitor/** - Next.js 14+ 모니터링 웹 (실시간 대시보드)

## Complexity Tracking

**Status**: ✅ No complexity violations

Constitution 파일이 템플릿 상태이므로 특정 제약 사항 없음. 현재 설계는 단순하고 명확함.
