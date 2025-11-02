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

### 향후 기능
- Feature 4: Thread-Safe Buffer 및 Oracle DB Writer
- Feature 5: REST API 및 WebSocket 서버
- Feature 6: Next.js 관리 웹 (폴링 제어 및 시스템 관리)
- Feature 7: Next.js 모니터링 웹 (실시간 대시보드)
- Feature 8: 통합 테스트 및 배포 준비

## 빠른 시작

### 1. 전체 설치 (모노레포)

```bash
# 루트에서 모든 워크스페이스 설치
npm install
```

### 2. Backend 설정

```bash
cd backend

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env

# 데이터베이스 초기화
python src/scripts/init_database.py

# 샘플 데이터 생성 (선택사항)
python src/scripts/create_sample_data.py

# FastAPI 서버 실행
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend 개발 서버 실행

```bash
# 루트에서 실행

# 환경 변수 설정
cd apps/admin
cp .env.local.example .env.local
cd ../..

# Admin 웹 (http://localhost:3000)
npm run dev:admin

# Monitor 웹 (http://localhost:3001)
npm run dev:monitor

# 둘 다 실행
npm run dev
```

### 4. 접속 URL

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/polling
- **Admin Web**: http://localhost:3000
  - HTTP Polling UI: http://localhost:3000/polling
  - WebSocket UI: http://localhost:3000/polling-ws
- **Monitor Web**: http://localhost:3001

## 프로젝트 구조 (모노레포)

```
JSOPCUA/
├── apps/                 # 애플리케이션
│   ├── admin/           # Next.js 관리 웹 (@jsscada/admin)
│   │   ├── app/         # App Router
│   │   ├── components/  # 앱 전용 컴포넌트
│   │   └── lib/         # 앱 전용 유틸리티
│   └── monitor/         # Next.js 모니터링 웹 (@jsscada/monitor)
│       ├── app/         # App Router
│       ├── components/  # 앱 전용 컴포넌트
│       └── lib/         # 앱 전용 유틸리티
├── packages/            # 공용 패키지
│   ├── ui/             # 공용 UI 컴포넌트 (@jsscada/ui)
│   └── utils/          # 공용 유틸리티 (@jsscada/utils)
├── backend/            # Python 백엔드
│   ├── config/         # SQLite DB 및 설정
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
