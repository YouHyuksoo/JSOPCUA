# JSOPCUA - JavaScript/Python OPC UA SCADA System

JSOPCUA는 Mitsubishi Q Series PLC와 통신하여 실시간 데이터를 수집하고 모니터링하는 엔터프라이즈급 SCADA 시스템입니다. 멀티스레드 폴링 엔진, 메모리 버퍼, Oracle DB Writer를 통해 고성능 데이터 수집과 저장을 지원합니다.

## 시스템 구성

- **Backend** (Python 3.11+): MC 3E ASCII 프로토콜 기반 PLC 통신, 멀티스레드 폴링 엔진, REST API/WebSocket 서버
- **Admin UI** (Next.js 14+, shadcn/ui): 시스템 관리, 설정, 폴링 제어 웹 애플리케이션
- **Monitor Dashboard** (Next.js 14+, shadcn/ui): 실시간 설비 상태 모니터링 (준비 중)
- **SQLite**: 로컬 설정 데이터베이스 (라인, 공정, PLC, 태그, 폴링 그룹)
- **Oracle DB**: 원격 데이터 저장소 (실시간 수집 데이터 저장)

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
- **시스템 제어 패널**: SCADA 시스템 시작/중지/재시작 (수동 제어)
- 라인/공정/PLC/태그 관리 페이지 (CRUD)
- 폴링 그룹 관리 페이지 (시작/중지 제어)
- 시스템 상태 대시보드 (실시간 모니터링)
- 로그 조회 (4종: scada/error/communication/performance)
- CSV 일괄 업로드 (태그)
- React Hook Form + Zod 검증
- Tailwind CSS 반응형 디자인
- 다크 모드 테마

### 진행 중인 기능

#### Feature 7: Monitor Web UI (실시간 모니터링) - 준비 중
- 실시간 설비 상태 모니터링 (WebSocket)
- 알람 통계 조회 (Oracle DB 연동)
- 최근 알람 목록 표시
- 대시보드 레이아웃 (그리드/테이블 뷰)

#### Feature 8: 통합 테스트 및 배포 준비 - 진행 중
- End-to-End 테스트 (Backend/Frontend)
- 성능 및 부하 테스트
- Docker 컨테이너화
- 배포 문서 및 운영 가이드

> **참고**: Oracle DB에 저장된 **히스토리 데이터 조회 및 분석**은 **별도 시스템**에서 수행하므로, 이 프로젝트 범위에 포함되지 않습니다.

## 시스템 범위 명확화

### ✅ 포함 (이 프로젝트)
1. **데이터 수집**: PLC에서 태그 값 폴링
2. **데이터 저장**: Oracle DB에 실시간 저장
3. **시스템 관리**: 라인/공정/PLC/태그/폴링그룹 CRUD
4. **실시간 모니터링**: WebSocket 기반 현재 값 표시
5. **시스템 제어**: 수동 시작/중지 (백엔드 서버 시작 시 자동 실행 안 됨)

### ❌ 제외 (별도 시스템)
1. **히스토리 조회**: Oracle DB에서 과거 데이터 조회
2. **시계열 분석**: 집계 데이터 (평균/최대/최소)
3. **트렌드 차트**: 시간별 그래프
4. **리포트 생성**: 통계 및 분석 리포트

## 빠른 시작

### 사전 체크리스트

시작하기 전에 다음을 확인하세요:

- [ ] Python 3.11+ 설치
- [ ] Node.js 18+ 설치
- [ ] `backend/config/scada.db` 파일 존재 여부 확인 (없으면 초기화 필요)
- [ ] `backend/.env` 파일 존재 여부 확인 (없으면 `.env.example` 복사 필요)

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

# 환경 설정 파일 생성 및 수정
copy .env.example .env  # Windows
# 또는
cp .env.example .env    # Linux/Mac

# .env 파일을 열어서 필요한 설정 수정
# - LOG_LEVEL: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
# - ORACLE_HOST, ORACLE_PORT: Oracle DB 호스트, 포트
# - ORACLE_SERVICE_NAME: Oracle Service Name (예: ORCL, XE)
# - ORACLE_USERNAME, ORACLE_PASSWORD: Oracle DB 연결 정보
# - ORACLE_POOL_MIN, ORACLE_POOL_MAX: 연결 풀 크기 (기본: 2, 5)
notepad .env  # Windows
# 또는
nano .env     # Linux/Mac

# .env 파일 예시
# LOG_LEVEL=INFO
# ORACLE_HOST=oracle.example.com
# ORACLE_PORT=1521
# ORACLE_SERVICE_NAME=ORCL
# ORACLE_USERNAME=scada_user
# ORACLE_PASSWORD=secure_password
# ORACLE_POOL_MIN=2
# ORACLE_POOL_MAX=5

# 데이터베이스 초기화 (선택사항 - 이미 config/scada.db가 있으면 스킵)
# 스키마가 이미 생성되어 있는지 확인
python -c "import os; print('✅ DB exists' if os.path.exists('config/scada.db') else '❌ DB not found - need to initialize')"

# DB가 없거나 완전히 리셋하려면 초기화 실행
python src/scripts/init_database.py

# 샘플 데이터 생성 (선택사항)
python src/scripts/create_sample_data.py

# FastAPI 서버 실행 (.env 파일 설정 자동 적용)
python src/api/main.py

# 또는 개발 모드 (자동 리로드)
uvicorn src.api.main:app --reload

# ⚠️ 중요: SCADA 폴링 시스템은 자동으로 시작되지 않습니다
# Admin Web UI (http://localhost:3000)에서 시스템 제어 패널을 통해 수동으로 시작해야 합니다
```

**데이터베이스 초기화가 필요한 경우:**
- ❌ **불필요**: `config/scada.db` 파일이 이미 존재하고 테이블이 생성되어 있는 경우
- ✅ **필요**: 처음 프로젝트를 clone했거나, 데이터베이스를 완전히 리셋하고 싶은 경우

**로그 레벨 변경:**
- `.env` 파일에서 `LOG_LEVEL=DEBUG` 설정 후 재시작
- 외부 환경변수 설정 불필요!

**데이터 입력 방법:**
- Admin Web UI (http://localhost:3000)에서 수동으로 설비, 공정, PLC, 태그 등록
- 또는 샘플 데이터 스크립트 실행 (있는 경우)

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
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Admin Web**: http://localhost:3000
- **Monitor Web**: http://localhost:3001

### 5. Backend API 주요 엔드포인트

#### PLC 연결 관리
- `GET /api/plc-connections` - PLC 목록 조회
- `POST /api/plc-connections` - PLC 추가
- `POST /api/plc-connections/{id}/test` - 연결 테스트

#### 태그 관리
- `GET /api/tags` - 태그 목록 조회
- `POST /api/tags` - 태그 추가
- `POST /api/tags/batch` - CSV 일괄 업로드

#### 폴링 그룹 관리
- `GET /api/polling-groups` - 폴링 그룹 목록
- `POST /api/polling-groups` - 폴링 그룹 생성
- `POST /api/polling-groups/{id}/start` - 폴링 시작
- `POST /api/polling-groups/{id}/stop` - 폴링 중지

#### 시스템 모니터링
- `GET /api/buffer/stats` - 메모리 버퍼 및 Oracle Writer 통계
- `GET /api/logs` - 시스템 로그 조회
- `GET /api/logs?type=scada` - SCADA 시스템 로그
- `GET /api/logs?type=error` - 에러 로그
- `GET /api/logs?type=communication` - PLC 통신 로그
- `GET /api/logs?type=performance` - 성능 메트릭 로그
- `ws://localhost:8000/ws/polling` - WebSocket 실시간 상태

#### Oracle 데이터 조회 (모니터링용)
- `GET /api/oracle/tag-values?limit=100&order=desc` - 최근 태그 값 조회
- `GET /api/oracle/statistics` - Oracle 저장 통계
- `GET /api/oracle/sync-status` - 마스터 데이터 동기화 상태

> API 상세 문서: http://localhost:8000/docs

## 프로젝트 구조 (모노레포)

```
JSOPCUA/
├── apps/                        # Next.js 애플리케이션
│   ├── admin/                  # Admin UI (시스템 관리)
│   │   ├── app/               # App Router
│   │   ├── components/        # React 컴포넌트
│   │   ├── lib/               # 유틸리티
│   │   └── public/            # 정적 자산
│   └── monitor/               # Monitor Dashboard (준비 중)
│       ├── app/
│       ├── components/
│       └── lib/
├── backend/                     # Python 백엔드
│   ├── config/                # SQLite DB, 설정
│   ├── logs/                  # 로그 파일 (scada/error/communication/performance)
│   └── src/
│       ├── database/          # SQLite 모델, 관리
│       ├── plc/               # MC 3E ASCII 프로토콜, Connection Pool
│       ├── polling/           # 멀티스레드 폴링 엔진
│       ├── buffer/            # 스레드 안전 Circular Buffer
│       ├── oracle_writer/     # Oracle DB Writer (배치 쓰기)
│       ├── api/               # FastAPI 엔드포인트
│       │   ├── models.py      # Pydantic 모델
│       │   ├── main.py        # FastAPI 서버
│       │   ├── *_routes.py    # API 라우터
│       │   └── ...
│       ├── config/            # 설정 (경로, DB)
│       └── scripts/           # 초기화, 샘플 데이터
├── docs/                        # 프로젝트 문서
├── specs/                       # 기능 명세 (SpecKit)
│   ├── 001-project-structure/  # Feature 1
│   ├── 002-mc3e-protocol/      # Feature 2
│   ├── 003-polling-engine/     # Feature 3
│   ├── 004-buffer-oracle/      # Feature 4
│   ├── 005-database-crud/      # Feature 5
│   ├── 006-admin-web/          # Feature 6
│   ├── 007-monitor-web/        # Feature 7
│   └── 008-integration-test/   # Feature 8
├── package.json                 # 모노레포 루트 (Workspace)
├── README.md                    # 이 파일
├── CLAUDE.md                    # Claude AI 지침
└── .specify/                    # SpecKit 설정
```

## 데이터베이스 스키마

### SQLite (로컬 설정)

#### 핵심 테이블

1. **lines** - 생산 라인 (라인 코드, 이름)
2. **processes/workstages** - 공정 (14자리 설비 코드 예: KRCWO12ELOA101)
3. **plc_connections** - PLC 연결 정보 (호스트, 포트, 타입)
4. **tags** - PLC 태그 (최대 3,491개, 주소, 타입, 폴링 속성)
5. **polling_groups** - 폴링 그룹 (FIXED/HANDSHAKE 모드)

#### 스키마 관계도

```
lines (라인)
  └─> processes/workstages (공정) [CASCADE]
       └─> plc_connections (PLC) [CASCADE]
            └─> tags (태그) [CASCADE]
                 └─> polling_groups (폴링 그룹) [SET NULL]
```

#### 주요 인덱스
- `idx_workstages_process_name`: 공정 검색 최적화
- `idx_tags_plc_id`: PLC별 태그 검색
- `idx_tags_polling_group_id`: 폴링 그룹별 태그 검색
- `idx_polling_groups_is_active`: 활성 폴링 그룹 검색

### Oracle Database (데이터 저장)

#### 데이터 저장 테이블

1. **XSCADA_DATATAG_LOG** - 알람/데이터 태그 값 로그 (시계열 데이터)
   - `ID`: 자동 증가 번호 (NUMBER(19,0), 기본키)
   - `CTIME`: 생성 시간 (TIMESTAMP(6), 기본값: CURRENT_TIMESTAMP)
   - `OTIME`: 폴링 시간 (TIMESTAMP(6), 실제 데이터 수집 시간)
   - `DATATAG_NAME`: 태그 이름 (NVARCHAR2(255), 예: "알람1", "센서A")
   - `DATATAG_TYPE`: 태그 타입 (CHAR(1), 'A'=알람, 'D'=데이터, 기본값: 'A')
   - `VALUE_STR`: 문자열 값 (NVARCHAR2(255))
   - `VALUE_NUM`: 수치형 값 (NUMBER)
   - `VALUE_RAW`: 원본 값 (NVARCHAR2(2000))

2. **XSCADA_OPERATION** - Operation/Control 타입 태그 값 로그 (시계열 데이터)
   - `TIME`: 동작 시간 (TIMESTAMP(6), 실제 데이터 수집 시간)
   - `NAME`: Operation 태그 이름 (VARCHAR2(200), 예: "PLC01.Operation.KRCWO12EBEM113.W0DDE")
   - `VALUE`: 제어값 (VARCHAR2(100), 예: "0", "1", "1699", "3305")

3. **ICOM_MACHINE_MASTER** - 설비 마스터 정보 (동기화)
   - `MACHINE_CODE`: 설비 코드 (14자리)
   - `MACHINE_NAME`: 설비 명칭
   - `MACHINE_LOCATION`: 설비 위치
   - `USE_YN`: 사용 여부

3. **ICOM_PLC_MASTER** - PLC 마스터 정보 (동기화)
   - `PLC_CODE`: PLC 코드
   - `PLC_NAME`, `PLC_SPEC`, `PLC_TYPE`: PLC 정보
   - `PLC_IP`, `PLC_PORT`: 네트워크 정보
   - `PLC_NETWORK_NO`, `PLC_STATION_NO`: 통신 파라미터

4. **ICOM_PLC_TAG_MASTER** - PLC 태그 마스터 (동기화)
   - `PLC_CODE`, `TAG_ADDRESS`: 기본키
   - `MACHINE_CODE`, `TAG_NAME`, `TAG_TYPE`: 태그 정보
   - `TAG_DATA_TYPE`: 데이터 타입 (INT, FLOAT, STRING)
   - `TARGET_MIN_VALUE`, `TARGET_MAX_VALUE`: 임계값

#### 마스터 데이터 동기화

SQLite에 정의된 machines, plc_connections, tags는 Oracle의 ICOM_*_MASTER 테이블과 자동으로 동기화됩니다:

```
Oracle (마스터)                SQLite (로컬 캐시)
├─ ICOM_MACHINE_MASTER   ←→  machines
├─ ICOM_PLC_MASTER       ←→  plc_connections
├─ ICOM_PLC_TAG_MASTER   ←→  tags
└─ ICOM_WORKSTAGE_MASTER ←→  workstages
```

#### 폴링 결과 입력 흐름

```
Polling Engine (멀티스레드)
        ↓
   BufferedTagValue
        ↓
  Circular Buffer
  (Thread-Safe FIFO)
        ↓
Oracle Writer Thread
(배치 모드: 500개씩)
        ↓
OracleConnectionPool
(2-5 연결 재사용)
        ↓
   XSCADA_DATATAG_LOG 테이블
   XSCADA_OPERATION 테이블
   (실시간 저장)
        ↓
   [실패 시]
   CSV 백업 파일
```

## Oracle Writer 입력 루틴 상세

### 1. 데이터 수집 및 버퍼링

**Polling Engine** (멀티스레드)에서 PLC로부터 폴링한 데이터는 `BufferedTagValue` 객체로 변환됩니다:

```python
BufferedTagValue(
    timestamp=datetime.now(),      # 폴링 시간
    plc_code="KRCWO12ELOA101",    # PLC 코드
    tag_address="D100",             # 태그 주소
    tag_value=12.34,                # 폴링된 값
    quality=0                       # 데이터 품질
)
```

이 데이터들은 **스레드 안전 Circular Buffer** (10,000 엔트리 FIFO)에 저장됩니다.

### 2. Oracle Writer Thread 배치 쓰기

별도의 **Oracle Writer 백그라운드 스레드**가 버퍼에서 데이터를 소비하여 Oracle DB에 저장합니다.

#### 쓰기 트리거 (둘 중 하나 먼저 발생)

- **시간 기반**: 1초마다 한 번 쓰기 시도
- **크기 기반**: 버퍼에 500개 이상 데이터 축적

#### 배치 쓰기 처리

**SQL INSERT 문 (파라미터 바인딩) - 두 가지 경우**:

1. **태그 값 저장 (알람/데이터 타입 태그)**:
```sql
INSERT INTO XSCADA_DATATAG_LOG (CTIME, OTIME, DATATAG_NAME, DATATAG_TYPE, VALUE_STR, VALUE_NUM, VALUE_RAW)
VALUES (CURRENT_TIMESTAMP, :otime, :datatag_name, :datatag_type, :value_str, :value_num, :value_raw)
```

2. **Operation/Control 태그 값 저장 (Operation 타입 태그)**:
```sql
INSERT INTO XSCADA_OPERATION (TIME, NAME, VALUE)
VALUES (:time, :tag_name, :tag_value)
```

**Python 실행 코드**:
```python
# 1. XSCADA_DATATAG_LOG 테이블에 태그 값 저장
datatag_log_insert = """
    INSERT INTO XSCADA_DATATAG_LOG (CTIME, OTIME, DATATAG_NAME, DATATAG_TYPE, VALUE_STR, VALUE_NUM, VALUE_RAW)
    VALUES (CURRENT_TIMESTAMP, :otime, :datatag_name, :datatag_type, :value_str, :value_num, :value_raw)
"""

# 태그 값 파라미터 준비 (알람/데이터 타입)
datatag_parameters = [
    {
        'otime': item.timestamp,                    # 폴링 시간 (TIMESTAMP)
        'datatag_name': item.tag_name,              # 태그 이름 (예: "PLC01.Alarm.KRCWO12EANN107.M35070")
        'datatag_type': item.tag_type,              # 'A'(Alarm), 'B'(BIT-PLC), 'H'(BIT-HOST), 'O'(Operation), 'S'(State), 'WH'(WORD-HOST)
        'value_str': str(item.tag_value),           # 문자열 값 (예: "Off", "On", "정상")
        'value_num': float(item.tag_value) if isinstance(item.tag_value, (int, float)) else None,
        'value_raw': str(item.tag_value)            # 원본 값
    }
    for item in items if item.is_datatag  # DATATAG_TYPE 데이터만 (Alarm, Data)
]

# 2. XSCADA_OPERATION 테이블에 Operation 타입 태그 값 저장
operation_insert = """
    INSERT INTO XSCADA_OPERATION (TIME, NAME, VALUE)
    VALUES (:time, :tag_name, :tag_value)
"""

# Operation 파라미터 준비 (Operation 타입 태그)
operation_parameters = [
    {
        'time': item.timestamp,                     # 데이터 수집 시간 (TIMESTAMP)
        'tag_name': item.tag_name,                  # Operation 태그 이름 (형식: PLC코드.Operation.설비코드.태그주소)
        'tag_value': str(item.tag_value)            # 제어값 (숫자/문자열, 예: "0", "1", "1699", "3305")
    }
    for item in items if item.is_operation  # Operation 타입 태그만
]

# 3. 배치 실행 및 에러 처리
with connection_pool.get_connection() as conn:
    cursor = conn.cursor()

    # XSCADA_DATATAG_LOG 배치 삽입
    if datatag_parameters:
        cursor.executemany(datatag_log_insert, datatag_parameters, batcherrors=True)
        errors = cursor.getbatcherrors()
        if errors:
            logger.warning(f"XSCADA_DATATAG_LOG batch insert: {len(errors)} errors")

    # XSCADA_OPERATION 배치 삽입
    if operation_parameters:
        cursor.executemany(operation_insert, operation_parameters, batcherrors=True)
        errors = cursor.getbatcherrors()
        if errors:
            logger.warning(f"XSCADA_OPERATION batch insert: {len(errors)} errors")

    conn.commit()  # 트랜잭션 커밋
    logger.info(f"Batch write completed: {len(datatag_parameters)} tag values, {len(operation_parameters)} operations")
```

**Oracle 테이블 구조** (이미 생성되어 있음):

1. **XSCADA_DATATAG_LOG 테이블 (태그 값 로그)**:
   - `ID`: NUMBER(19,0) PRIMARY KEY - 자동 증가 번호
   - `CTIME`: TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP - 생성 시간 (자동)
   - `OTIME`: TIMESTAMP(6) NOT NULL - 폴링 시간 (실제 데이터 수집 시간)
   - `DATATAG_NAME`: NVARCHAR2(255) NOT NULL - 태그 이름 (형식: PLC코드.동작구분.설비코드.태그주소)
     - 예: "PLC01.Alarm.KRCWO12EANN107.M35070" (알람), "PLC01.BIT.KRCWO12EANN107.M35071" (BIT)
   - `DATATAG_TYPE`: CHAR(1) DEFAULT 'A' NOT NULL - 태그 타입 ('A'=Alarm, 'B'=BIT(PLC), 'H'=BIT(HOST), 'O'=Operation, 'S'=State, 'WH'=WORD(HOST))
   - `VALUE_STR`: NVARCHAR2(255) - 문자열 값 (예: "Off", "On", "정상", "경고")
   - `VALUE_NUM`: NUMBER - 수치형 값 (예: 0, 1, 12.34)
   - `VALUE_RAW`: NVARCHAR2(2000) - 원본 값

2. **XSCADA_OPERATION 테이블 (Operation/State 타입 태그 값 로그)**:
   - `TIME`: TIMESTAMP(6) NOT NULL - 데이터 수집 시간
   - `NAME`: VARCHAR2(200) NOT NULL - 태그 이름 (형식: PLC코드.동작구분.설비코드.태그주소)
     - 예: "PLC01.Operation.KRCWO12EANN212.W0CD0" (제어), "PLC01.State.KRCWO12EANN212.M35070" (상태)
   - `VALUE`: VARCHAR2(100) - 태그값 (숫자/문자열, 예: "0", "1", "1699", "3305")

**XSCADA_DATATAG_LOG 데이터 예시**:
```
ID      | CTIME                           | OTIME                           | DATATAG_NAME                         | DATATAG_TYPE | VALUE_STR | VALUE_NUM | VALUE_RAW
4276534 | 2022/07/22 14:27:12.159000000 | 2022/07/22 05:27:29.216000000 | PLC01.Alarm.KRCWO12EANN107.M35070 | A            | Off       | 0         | false
4319704 | 2022/07/25 17:50:52.251000000 | 2022/07/25 08:51:14.269000000 | PLC01.BIT.KRCWO12EANN107.M35073   | B            | 1         | 1         | 1
4371379 | 2022/07/27 17:21:45.778000000 | 2022/07/27 08:22:08.053000000 | PLC01.Alarm.KRCWO12EANN107.M35071 | A            | On        | 1         | true
4394918 | 2022/07/28 10:22:20.794000000 | 2022/07/28 01:22:40.715000000 | PLC01.WORD.KRCWO12EANN107.D100    | WH           | 45.67     | 45.67     | 45.67
4422026 | 2022/07/28 12:49:58.791000000 | 2022/07/28 03:49:26.414000000 | PLC01.State.KRCWO12EANN107.M35072 | S            | 정상      | 0         | 정상
```

**XSCADA_OPERATION 데이터 예시**:
```
TIME                           | NAME                                       | VALUE
2022/08/29 11:40:07.000000000 | PLC01.Operation.KRCWO12EBEM113.W0DDE     | 0
2022/08/29 11:40:07.000000000 | PLC01.Operation.KRCWO12EBEM113.W0DDF     | 0
2022/08/29 11:40:07.000000000 | PLC01.Operation.KRCWO12EANN212.W0CC0     | 1699
2022/08/29 11:40:07.000000000 | PLC01.Operation.KRCWO12EANN212.W0CC3     | 3305
2022/08/29 11:40:07.000000000 | PLC01.Operation.KRCWO12EANN212.W0CD0     | 90
2022/08/29 11:40:07.000000000 | PLC01.State.KRCWO12EANN212.M35070        | 정상
2022/08/29 11:40:08.000000000 | PLC01.State.KRCWO12EANN212.M35071        | 경고
2022/08/29 11:40:09.000000000 | PLC01.Operation.KRCWO12EANN212.W0CD2     | 1635
```

### 3. 에러 처리 및 복구

#### 재시도 로직 (지수 백오프)

Oracle 연결 실패 시 3회 자동 재시도:

```
시도 1 → [실패] → 1초 대기
시도 2 → [실패] → 2초 대기
시도 3 → [실패] → 4초 대기
결과: 실패 → CSV 백업
```

#### CSV 자동 백업

Oracle 저장 실패 시, 해당 배치 데이터는 CSV 파일로 자동 백업됩니다:

**XSCADA_DATATAG_LOG 백업**:
```
backend/logs/backup/xscada_datatag_log_20241204_120530_500.csv

otime,datatag_name,datatag_type,value_str,value_num,value_raw
2024-12-04 12:05:30.100000,PLC01.BIT.KRCWO12EANN107.M35073,B,1,1,1
2024-12-04 12:05:31.200000,PLC01.WORD.KRCWO12EANN107.D100,WH,45.67,45.67,45.67
2024-12-04 12:05:32.300000,PLC01.Alarm.KRCWO12EANN107.M35070,A,경고,1,경고
...
```

**XSCADA_OPERATION 백업**:
```
backend/logs/backup/xscada_operation_20220829_114007_500.csv

time,name,value
2022/08/29 11:40:07.000000000,PLC01.Operation.KRCWO12EBEM113.W0DDE,0
2022/08/29 11:40:07.000000000,PLC01.Operation.KRCWO12EBEM113.W0DDF,0
2022/08/29 11:40:07.000000000,PLC01.Operation.KRCWO12EANN212.W0CC0,1699
...
```

### 4. Connection Pool 활용

**OracleConnectionPool** (2-5개 연결 재사용):

- Min Connections: 2 (항상 유지)
- Max Connections: 5 (최대 동시 연결)
- Connection Timeout: 30초
- Session Timeout: 5초
- Max Lifetime: 1시간 (자동 재활용)

```python
# 스레드 안전 연결 획득
with connection_pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.executemany(insert_sql, parameters, batcherrors=True)
    conn.commit()
```

### 5. 모니터링 및 성능 추적

**RollingMetrics**를 통해 실시간 성능 지표 수집:

```json
{
  "total_batches": 1523,
  "successful_batches": 1510,
  "failed_batches": 13,
  "total_items_written": 751500,
  "total_items_failed": 7000,
  "avg_batch_latency_ms": 45.2,
  "max_batch_latency_ms": 892,
  "items_per_second": 1247
}
```

**모니터링 API**:

```bash
GET /api/buffer/stats - 버퍼 및 Writer 통계 조회
GET /api/logs?type=scada - 시스템 로그 (배치 쓰기 기록)
GET /api/oracle/datatag-log - 최근 태그 값 조회 (XSCADA_DATATAG_LOG)
GET /api/oracle/operations - 최근 동작 기록 조회 (XSCADA_OPERATION)
```

#### XSCADA_DATATAG_LOG 테이블 조회 예시

**최근 100개 데이터 조회**:
```sql
SELECT ID, OTIME, DATATAG_NAME, DATATAG_TYPE, VALUE_STR, VALUE_NUM
FROM XSCADA_DATATAG_LOG
ORDER BY OTIME DESC
FETCH FIRST 100 ROWS ONLY;
```

**특정 태그의 최근 데이터 (최근 50개)**:
```sql
SELECT ID, OTIME, DATATAG_NAME, DATATAG_TYPE, VALUE_STR, VALUE_NUM
FROM XSCADA_DATATAG_LOG
WHERE DATATAG_NAME = 'PLC01.BIT.KRCWO12EANN107.M35073'
ORDER BY OTIME DESC
FETCH FIRST 50 ROWS ONLY;
```

**특정 태그의 시계열 데이터 (최근 1시간)**:
```sql
SELECT ID, OTIME, DATATAG_NAME, DATATAG_TYPE, VALUE_STR, VALUE_NUM
FROM XSCADA_DATATAG_LOG
WHERE DATATAG_NAME = '센서A'
  AND OTIME >= SYSDATE - INTERVAL '1' HOUR
ORDER BY OTIME DESC;
```

**알람 데이터만 조회 (DATATAG_TYPE = 'A')**:
```sql
SELECT ID, OTIME, DATATAG_NAME, VALUE_STR, VALUE_NUM
FROM XSCADA_DATATAG_LOG
WHERE DATATAG_TYPE = 'A'
ORDER BY OTIME DESC
FETCH FIRST 100 ROWS ONLY;
```

**BIT/WORD 타입 태그만 조회 (DATATAG_TYPE IN ('B', 'H', 'WH'))**:
```sql
SELECT ID, OTIME, DATATAG_NAME, DATATAG_TYPE, VALUE_STR, VALUE_NUM
FROM XSCADA_DATATAG_LOG
WHERE DATATAG_TYPE IN ('B', 'H', 'WH')
ORDER BY OTIME DESC
FETCH FIRST 100 ROWS ONLY;
```

**배치 쓰기 성능 분석 (분당 저장된 행 수)**:
```sql
SELECT
    TRUNC(OTIME, 'MI') AS minute,
    COUNT(*) AS row_count,
    ROUND(COUNT(*) / 60, 2) AS rows_per_second
FROM XSCADA_DATATAG_LOG
WHERE OTIME >= SYSDATE - INTERVAL '1' HOUR
GROUP BY TRUNC(OTIME, 'MI')
ORDER BY minute DESC;
```

#### XSCADA_OPERATION 테이블 조회 예시

**최근 100개 Operation 태그 값**:
```sql
SELECT TIME, NAME, VALUE
FROM XSCADA_OPERATION
ORDER BY TIME DESC
FETCH FIRST 100 ROWS ONLY;
```

**특정 Operation 태그의 최근 데이터 (최근 50개)**:
```sql
SELECT TIME, NAME, VALUE
FROM XSCADA_OPERATION
WHERE NAME = 'PLC01.Operation.KRCWO12EANN212.W0CC0'
ORDER BY TIME DESC
FETCH FIRST 50 ROWS ONLY;
```

**특정 Operation 태그의 시계열 데이터 (최근 1시간)**:
```sql
SELECT TIME, NAME, VALUE
FROM XSCADA_OPERATION
WHERE NAME = 'PLC01.Operation.KRCWO12EANN212.W0CC0'
  AND TIME >= SYSDATE - INTERVAL '1' HOUR
ORDER BY TIME DESC;
```

**설비별 Operation 태그 통계**:
```sql
SELECT
    SUBSTR(NAME, 1, INSTR(NAME, '.W') - 1) AS equipment_code,
    COUNT(*) AS tag_count,
    COUNT(DISTINCT NAME) AS unique_tags
FROM XSCADA_OPERATION
WHERE TIME >= SYSDATE - INTERVAL '1' HOUR
GROUP BY SUBSTR(NAME, 1, INSTR(NAME, '.W') - 1)
ORDER BY tag_count DESC;
```

## 기술 스택

### Backend
- **Runtime**: Python 3.11+
- **Database**: SQLite 3.40+ (로컬 설정), Oracle DB (데이터 저장)
- **PLC 통신**: pymcprotocol (MC 3E ASCII 프로토콜)
- **API 서버**: FastAPI (REST API), uvicorn (ASGI)
- **실시간 통신**: websockets (WebSocket)
- **데이터 검증**: pydantic
- **Oracle 연동**: python-oracledb 2.0+ (⚠️ cx_Oracle 사용 금지)
- **멀티스레드**: threading, queue (스레드 안전 큐)

### Frontend
- **프레임워크**: Next.js 14+ (App Router)
- **UI 라이브러리**: React 18+, TypeScript 5.3+
- **스타일링**: Tailwind CSS + shadcn/ui
- **HTTP 클라이언트**: axios
- **상태관리**: React Hooks

## 라이선스

Proprietary

## 문의

프로젝트 관련 문의는 개발팀에게 연락하세요.

---

## Feature 7: Monitor Web UI (준비 중)

### 개요
실시간 설비 상태를 모니터링하고 알람 정보를 표시하는 웹 기반 대시보드입니다. WebSocket을 통해 백엔드 폴링 엔진과 실시간 통신합니다.

### 계획된 주요 기능
- **실시간 설비 상태 모니터링**: WebSocket 연결을 통해 1초 주기로 설비의 상태를 색상으로 표시
- **설비별 알람 통계**: Oracle DB에서 알람 합계 및 일반 건수 조회
- **최근 알람 목록**: 최근 알람을 시간 역순으로 표시
- **대시보드 레이아웃**: 그리드/테이블 뷰 선택 가능

### 기술 스택
- Next.js 14 App Router
- TypeScript
- Tailwind CSS + shadcn/ui
- axios (REST API)
- WebSocket (실시간 통신)

### 구현 상태
- [ ] 실시간 설비 상태 모니터링 UI
- [ ] 알람 통계 API 통합
- [ ] 알람 목록 표시
- [ ] 대시보드 레이아웃 구성

---

## Feature 8: 통합 테스트 및 배포 준비 (진행 중)

### 개요
End-to-End 테스트, 성능 테스트, Docker 컨테이너화, 배포 문서를 통해 프로덕션 준비를 완료합니다.

### 계획된 작업
- [ ] Backend End-to-End 테스트
- [ ] Frontend End-to-End 테스트 (Playwright)
- [ ] 성능 및 부하 테스트
- [ ] Docker 이미지 빌드
- [ ] docker-compose 설정
- [ ] 배포 가이드 문서
- [ ] 운영 모니터링 가이드

