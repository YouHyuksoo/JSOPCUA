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

#### Feature 7: Monitor 웹 UI (실시간 모니터링)
- 실시간 태그 값 모니터링 (WebSocket 기반)
- 라인별/공정별/폴링그룹별 필터링
- 태그 상태 카드 (현재 값, 최종 업데이트 시간)
- 대시보드 레이아웃 (그리드/테이블 뷰)
- 알람/경고 표시 (임계값 기반)
- 자동 새로고침 및 연결 상태 표시

> **참고**: Oracle DB에 저장된 **히스토리 데이터 조회 및 분석**은 **별도 시스템**에서 수행하므로, 이 프로젝트 범위에 포함되지 않습니다.

#### Feature 8: 통합 테스트 및 배포 준비
- End-to-End 테스트
- 성능 및 부하 테스트
- Docker 컨테이너화
- 배포 문서 및 운영 가이드

## 시스템 범위 명확화

### ✅ 포함 (이 프로젝트)
1. **데이터 수집**: PLC에서 태그 값 폴링
2. **데이터 저장**: Oracle DB에 실시간 저장
3. **시스템 관리**: 라인/공정/PLC/태그/폴링그룹 CRUD
4. **실시간 모니터링**: WebSocket 기반 현재 값 표시

### ❌ 제외 (별도 시스템)
1. **히스토리 조회**: Oracle DB에서 과거 데이터 조회
2. **시계열 분석**: 집계 데이터 (평균/최대/최소)
3. **트렌드 차트**: 시간별 그래프
4. **리포트 생성**: 통계 및 분석 리포트

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
- **Monitor Web**: http://localhost:3001

## 프로젝트 구조 (모노레포)

```
JSOPCUA/
├── apps/                 # 애플리케이션
│   ├── admin/           # Next.js 관리 웹
│   └── monitor/         # Next.js 모니터링 웹
├── backend/            # Python 백엔드
│   ├── config/         # SQLite DB 및 설정
│   ├── logs/           # 로그 파일
│   ├── src/
│   │   ├── database/   # DB 모델 및 관리
│   │   ├── plc/        # PLC 통신
│   │   ├── polling/    # 폴링 엔진
│   │   ├── buffer/     # 메모리 버퍼
│   │   ├── oracle_writer/ # Oracle DB Writer
│   │   ├── api/        # REST API & WebSocket
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

## 기술 스택

### Backend
- Python 3.11+
- SQLite 3.40+
- pymcprotocol (PLC 통신)
- FastAPI (REST API)
- uvicorn (ASGI 서버)
- websockets (WebSocket 서버)
- pydantic (데이터 검증)
- cx_Oracle (Oracle DB 연동)

### Frontend
- Next.js 14+ (App Router)
- React 18+
- TypeScript 5.3+
- Tailwind CSS
- shadcn/ui

## 라이선스

Proprietary

## 문의

프로젝트 관련 문의는 개발팀에게 연락하세요.
