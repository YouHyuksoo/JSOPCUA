# JSScada - JavaScript/Python SCADA System

JSScada는 Mitsubishi Q Series PLC와 통신하여 실시간 데이터를 수집하고 모니터링하는 SCADA 시스템입니다.

## 시스템 구성

- **Backend** (Python 3.11+): PLC 폴링 엔진, 데이터 수집, REST API/WebSocket 서버
- **Frontend Admin** (Next.js 14+): 시스템 관리 및 폴링 제어 웹 애플리케이션
- **Frontend Monitor** (Next.js 14+): 실시간 모니터링 대시보드
- **SQLite**: 로컬 설정 데이터베이스 (라인, 공정, PLC, 태그, 폴링 그룹)
- **Oracle DB**: 원격 데이터 저장소 (실시간 태그 값 저장)

## 주요 기능

### Feature 1: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정 ✅
- 표준화된 프로젝트 디렉토리 구조
- SQLite 데이터베이스 스키마 (5개 테이블, 8개 인덱스, 1개 뷰)
- 14자리 설비 코드 체계 지원 (예: KRCWO12ELOA101)
- 3,491개 태그 지원
- CSV 일괄 태그 등록 기능
- 샘플 데이터 자동 생성

### Feature 2: MC 3E ASCII 프로토콜 통신 및 Connection Pool ✅
- Mitsubishi Q Series PLC MC 3E ASCII 통신
- PLC당 5개 연결 재사용 Connection Pool
- 배치 읽기 (10-50개 태그 한 번에 조회)
- 자동 재연결 및 타임아웃 처리
- 성능: 태그당 평균 35-45ms

### Feature 3: 멀티 스레드 폴링 엔진 ✅
- **FIXED 모드**: 고정 주기 자동 폴링 (1s, 5s, 10s)
- **HANDSHAKE 모드**: REST API 트리거로 수동 폴링
- 최대 10개 폴링 그룹 동시 실행
- 그룹당 100개 이상 태그 지원
- 스레드 안전 큐 (10,000 엔트리)
- 자동 에러 복구 및 스레드 격리
- **REST API**: FastAPI 기반 8개 엔드포인트
- **WebSocket**: 실시간 상태 업데이트 (1초 간격)
- **관리 UI**: Next.js 폴링 제어 대시보드

### Feature 4: 메모리 버퍼 및 Oracle DB Writer ✅
- **Thread-Safe Circular Buffer**: 10,000 엔트리 FIFO 큐
- **Oracle Connection Pool**: 2-5 연결 재사용
- **배치 쓰기**: 500개 단위 고성능 쓰기 (1,000+ values/sec)
- **CSV 백업**: Oracle 실패 시 자동 백업
- **버퍼 오버플로 보호**: 임계값 알람 및 백프레셔
- **모니터링 API**: 실시간 메트릭 조회

### Feature 5: 데이터베이스 관리 REST API ✅
- 라인/공정 CRUD API
- PLC 연결 CRUD API (연결 테스트 포함)
- 태그 CRUD API (CSV 업로드, 배치 등록)
- 폴링 그룹 CRUD API (시작/중지/재시작)
- Foreign Key 검증 및 데이터 무결성
- Pydantic 모델 기반 검증
- 로깅 미들웨어

### Feature 6: Admin 웹 UI (시스템 관리) ✅
- **shadcn/ui 기반 관리 인터페이스**
- 라인/공정/PLC/태그 관리 페이지 (CRUD)
- 폴링 그룹 관리 페이지 (시작/중지 제어)
- 시스템 상태 대시보드 (실시간 모니터링)
- 로그 조회 (4종: scada/error/communication/performance)
- CSV 일괄 업로드 (태그)
- React Hook Form + Zod 검증
- Tailwind CSS 반응형 디자인

### 향후 기능

#### Feature 7: 실시간 데이터 조회 및 히스토리 API
- 현재 태그 값 조회 API (Oracle DB 연동)
- 시계열 히스토리 데이터 조회
- 집계 데이터 (평균/최대/최소)
- 태그 검색 및 필터링
- 페이징 및 성능 최적화

#### Feature 8: Monitor 웹 UI (실시간 모니터링)
- 실시간 태그 값 모니터링 (WebSocket)
- 라인별/공정별 필터링
- 트렌드 차트 (시계열 그래프)
- 태그 값 히스토리 조회
- 대시보드 레이아웃 (카드/테이블/차트)

#### Feature 9: 통합 테스트 및 배포 준비
- End-to-End 테스트
- 성능 및 부하 테스트
- Docker 컨테이너화
- 배포 문서 및 운영 가이드
│   ├── logs/           # 로그 파일
│   ├── src/
│   │   ├── database/   # DB 모델 및 관리
│   │   ├── plc/        # PLC 통신 (Feature 2)
│   │   ├── polling/    # 폴링 엔진 (Feature 3)
│   │   ├── api/        # REST API & WebSocket (Feature 3)
│   │   └── scripts/    # 유틸리티 스크립트
│   └── tests/          # 테스트
├── docs/               # 프로젝트 문서
├── specs/              # 기능 명세 (SpecKit)
└── package.json        # 모노레포 루트 설정
```

## 데이터베이스 스키마

### 핵심 테이블

1. **lines** - 생산 라인
2. **processes** - 공정 (14자리 설비 코드)
3. **plc_connections** - PLC 연결 정보
4. **tags** - PLC 태그 (최대 3,491개)
5. **polling_groups** - 폴링 그룹 (FIXED/HANDSHAKE)

### Foreign Key 관계

```
lines (라인)
  └─> processes (공정) [CASCADE]
       └─> plc_connections (PLC) [CASCADE]
            └─> tags (태그) [CASCADE]
                 └─> polling_groups (폴링 그룹) [SET NULL]
```

## 설비 코드 체계

14자리 형식: `KRCWO12ELOA101`
- KR: 국가 코드
- CWO: 공장 코드
- 12: 라인 번호
- ELO: 설비 유형
- A: 카테고리
- 101: 순번

## CSV 태그 등록

```bash
cd backend
python src/scripts/import_tags_csv.py path/to/tags.csv
```

CSV 형식:
```csv
PLC_CODE,TAG_ADDRESS,TAG_NAME,UNIT,SCALE,MACHINE_CODE
PLC01,D100,온도센서1,°C,1.0,KRCWO12ELOA101
```

## 개발 가이드

### 브랜치 전략

- `main`: 안정 버전
- `001-project-structure-sqlite-setup`: Feature 1
- `002-mc3e-protocol-connection-pool`: Feature 2 (예정)
- ...

### SpecKit 워크플로우

이 프로젝트는 SpecKit 워크플로우를 사용합니다:
1. `/speckit.specify` - 기능 명세 작성
2. `/speckit.plan` - 구현 계획 수립
3. `/speckit.tasks` - 작업 분해
4. `/speckit.implement` - 구현 실행

자세한 내용은 `CLAUDE.md` 참조.

## 기술 스택

### Backend
- Python 3.11+
- SQLite 3.40+
- pymcprotocol (PLC 통신)
- FastAPI (REST API)
- uvicorn (ASGI 서버)
- websockets (WebSocket 서버)
- pydantic (데이터 검증)
- cx_Oracle (Oracle DB 연동, 향후)

### Frontend
- Next.js 14+ (App Router)
- React 18+
- TypeScript 5.3+
- Tailwind CSS

## 라이선스

Proprietary

## 문의

프로젝트 관련 문의는 개발팀에게 연락하세요.
