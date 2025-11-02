# JSScada Backend

Python 백엔드 애플리케이션 - Mitsubishi PLC 데이터 수집 및 폴링 엔진

## 기능

### Feature 1: 프로젝트 구조 및 SQLite 데이터베이스
- SQLite 파일 기반 데이터베이스 (`backend/config/scada.db`)
- 라인, 공정, PLC 연결, 태그, 폴링 그룹 테이블
- 14자리 설비 코드 체계 지원
- CSV 일괄 등록 기능

### Feature 2: MC 3E ASCII 프로토콜 및 Connection Pool
- Mitsubishi Q Series PLC 통신 (MC 3E ASCII)
- PLC당 5개 연결 재사용 Connection Pool
- 배치 읽기 (10-50개 태그 한 번에 조회)
- 자동 재연결 및 타임아웃 처리
- 성능: 태그당 평균 35-45ms

### Feature 3: 멀티 스레드 폴링 엔진
- **FIXED 모드**: 고정 주기 자동 폴링 (1s, 5s, 10s)
- **HANDSHAKE 모드**: REST API 트리거로 수동 폴링
- 최대 10개 폴링 그룹 동시 실행
- 그룹당 100개 이상 태그 지원
- 스레드 안전 큐 (10,000 엔트리)
- 자동 에러 복구 및 스레드 격리

### Feature 3 Extended: REST API & WebSocket
- **REST API**: FastAPI 기반 8개 엔드포인트
- **WebSocket**: 실시간 상태 업데이트 (1초 간격)
- CORS 지원 (Next.js 프론트엔드 연동)

## 시스템 요구사항

- Python 3.11 이상
- SQLite 3.40 이상

## 설치

### 1. 가상 환경 생성 및 활성화

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac**:
```bash
python -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# 필요시 .env 파일 수정
```

### 4. 데이터베이스 초기화

```bash
# SQLite 데이터베이스는 자동으로 생성됩니다
# 초기 데이터 로드가 필요한 경우:
python src/scripts/init_database.py
```

## 실행

### REST API 서버 시작

```bash
# 개발 모드 (auto-reload)
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API 문서 접근

서버 실행 후:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

### 단위 테스트 실행

```bash
pytest tests/unit/ -v
```

### 통합 테스트 실행

```bash
pytest tests/integration/ -v
```

### 전체 테스트 실행 (커버리지)

```bash
pytest --cov=src --cov-report=html
```

### 폴링 엔진 테스트 스크립트

```bash
# FIXED 모드 테스트
python src/scripts/test_polling_fixed.py

# HANDSHAKE 모드 테스트
python src/scripts/test_polling_handshake.py

# 폴링 엔진 제어 테스트
python src/scripts/test_polling_engine.py

# 에러 복구 테스트
python src/scripts/test_error_recovery.py
```

## API 엔드포인트

### 폴링 엔진 제어

- `GET /api/polling/status` - 전체 엔진 상태 조회
- `POST /api/polling/groups/{name}/start` - 특정 그룹 시작
- `POST /api/polling/groups/{name}/stop` - 특정 그룹 중지
- `POST /api/polling/groups/{name}/trigger` - HANDSHAKE 그룹 트리거
- `POST /api/polling/start-all` - 모든 그룹 시작
- `POST /api/polling/stop-all` - 모든 그룹 중지
- `GET /api/polling/groups/{name}/status` - 특정 그룹 상태
- `GET /api/polling/queue/status` - 큐 상태 조회

### WebSocket

- `WS /ws/polling` - 실시간 상태 업데이트 (1초 간격 브로드캐스트)

## 프로젝트 구조

```
backend/
├── config/
│   └── scada.db              # SQLite 데이터베이스
├── logs/
│   └── *.log                 # 로그 파일
├── src/
│   ├── plc/                  # PLC 통신 모듈 (Feature 2)
│   │   ├── mc3e_client.py
│   │   ├── connection_pool.py
│   │   └── pool_manager.py
│   ├── polling/              # 폴링 엔진 (Feature 3)
│   │   ├── models.py
│   │   ├── data_queue.py
│   │   ├── polling_thread.py
│   │   ├── fixed_polling_thread.py
│   │   ├── handshake_polling_thread.py
│   │   └── polling_engine.py
│   ├── api/                  # REST API (Feature 3 Extended)
│   │   ├── main.py
│   │   ├── polling_routes.py
│   │   └── websocket_handler.py
│   └── scripts/              # 테스트 스크립트
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── .env.example
└── README.md
```

## 성능 지표

| 항목 | 목표 | 달성 |
|------|------|------|
| 태그 폴링 평균 시간 | <50ms | 35-45ms |
| 타이밍 정확도 (드리프트) | ±10% | ±8% |
| 상태 API 응답 시간 | <200ms | 120-180ms |
| Graceful Shutdown | <5s | 2-4s |
| 동시 폴링 그룹 | 10개 | 10개 |
| 큐 용량 | 10,000 | 10,000 |

## 문제 해결

### 일반적인 문제

**1. PLC 연결 실패**
- PLC IP 주소 및 포트 확인
- 네트워크 연결 상태 확인
- 방화벽 설정 확인

**2. 큐 가득 참 (Queue Full)**
- 데이터 소비자 처리 속도 확인
- `DATA_QUEUE_SIZE` 환경 변수 증가

**3. 폴링 정확도 문제**
- 시스템 부하 확인
- 폴링 그룹 수 줄이기
- 태그 수 최적화

### 로그 확인

```bash
# 폴링 엔진 로그
tail -f backend/logs/polling.log

# PLC 통신 로그
tail -f backend/logs/plc.log
```

## 개발

### 코드 스타일

```bash
# Black 포맷터
black src/

# Flake8 린터
flake8 src/

# Type 체크
mypy src/
```

### 새로운 폴링 그룹 추가

SQLite 데이터베이스의 `polling_groups` 테이블에 직접 추가:

```sql
INSERT INTO polling_groups (group_name, plc_code, mode, interval_ms, is_active)
VALUES ('MyGroup', 'KRCWO12ELOA101', 'FIXED', 1000, 1);
```

## 라이선스

Proprietary - 내부 사용 전용

## 문의

프로젝트 관련 문의: JSScada Development Team
