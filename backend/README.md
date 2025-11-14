# JSScada Backend

Python 백엔드 애플리케이션 - Mitsubishi PLC 데이터 수집 및 폴링 엔진

## 기능

### Feature 1: 프로젝트 구조 및 SQLite 데이터베이스
- SQLite 파일 기반 데이터베이스 (`backend/data/scada.db`)
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

### Feature 4: 메모리 버퍼 및 Oracle DB Writer
- **CircularBuffer**: 스레드 안전 순환 버퍼 (최대 100,000 항목)
- **Oracle Writer**: 배치 쓰기 최적화 (500개/배치, 0.5초 간격)
- **재시도 로직**: 지수 백오프 (1s, 2s, 4s) 3회 시도
- **CSV 백업**: Oracle 실패 시 자동 백업 (타임스탬프 파일)
- **FIFO 오버플로**: 버퍼 가득 시 오래된 항목 자동 삭제
- **성능 모니터링**: 5분 롤링 윈도우 메트릭 추적
- **REST API**: 버퍼/라이터 상태 모니터링 엔드포인트

## 시스템 요구사항

- Python 3.11 이상
- SQLite 3.40 이상
- Oracle Database 12c 이상 (Feature 4)
- python-oracledb 2.0 이상 (Thin 모드, Instant Client 불필요)

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

### Oracle Writer 테스트 스크립트

```bash
# Oracle 연결 테스트
python src/scripts/test_oracle_connection.py

# 버퍼 및 Oracle Writer 시작
python src/scripts/start_buffer_writer.py

# End-to-End 테스트 (폴링 → 버퍼 → Oracle)
python src/scripts/test_end_to_end.py

# 고처리량 성능 테스트 (1,000 값/초)
python src/scripts/test_high_throughput.py --rate 1000 --duration 60

# 버퍼 오버플로 테스트
python src/scripts/test_buffer_overflow.py

# 버퍼 모니터링 API 테스트
python src/scripts/test_buffer_metrics.py
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

### 버퍼 및 Oracle Writer 모니터링

- `GET /api/buffer/status` - 버퍼 상태 조회 (크기, 사용률, 오버플로)
- `GET /api/buffer/writer/metrics` - 라이터 성능 메트릭
- `GET /api/buffer/health` - 헬스 체크 (버퍼, 라이터, Oracle 연결)
- `GET /api/buffer/metrics` - 통합 메트릭 (버퍼 + 라이터 + 백업)

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
│   ├── buffer/               # 메모리 버퍼 (Feature 4)
│   │   ├── circular_buffer.py
│   │   ├── buffer_consumer.py
│   │   ├── models.py
│   │   └── exceptions.py
│   ├── oracle_writer/        # Oracle DB Writer (Feature 4)
│   │   ├── writer.py
│   │   ├── connection_pool.py
│   │   ├── metrics.py
│   │   ├── backup.py
│   │   └── config.py
│   ├── api/                  # REST API (Feature 3 Extended)
│   │   ├── main.py
│   │   ├── polling_routes.py
│   │   ├── buffer_routes.py
│   │   └── websocket_handler.py
│   └── scripts/              # 테스트 스크립트
├── backup/                   # CSV 백업 파일 (Feature 4)
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── .env.example
└── README.md
```

## 성능 지표

### Feature 3: 폴링 엔진

| 항목 | 목표 | 달성 |
|------|------|------|
| 태그 폴링 평균 시간 | <50ms | 35-45ms |
| 타이밍 정확도 (드리프트) | ±10% | ±8% |
| 상태 API 응답 시간 | <200ms | 120-180ms |
| Graceful Shutdown | <5s | 2-4s |
| 동시 폴링 그룹 | 10개 | 10개 |
| 큐 용량 | 10,000 | 10,000 |

### Feature 4: Oracle Writer

| 항목 | 목표 | 달성 |
|------|------|------|
| Oracle 쓰기 처리량 | >1,000 값/초 | 1,000+ 값/초 |
| 평균 배치 쓰기 지연 | <2초 | <2초 |
| 쓰기 성공률 | >99.9% | >99.9% |
| 버퍼 용량 | 100,000 항목 | 100,000 항목 |
| 오버플로율 | <1% | <1% |
| 배치 크기 | 100-1,000 | 500 (기본값) |

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

**4. Oracle 쓰기 실패**
- Oracle 데이터베이스 연결 확인
- `backend/backup/` 디렉토리에서 CSV 백업 파일 확인
- Oracle 사용자 권한 확인 (INSERT 권한 필요)
- `oracle_writer.log`에서 에러 메시지 확인

**5. 버퍼 사용률 높음 (>80%)**
- Oracle Writer 실행 상태 확인
- `BUFFER_MAX_SIZE` 환경 변수 증가
- Oracle 쓰기 성능 최적화
- 폴링 빈도 감소

### 로그 확인

```bash
# 폴링 엔진 로그
tail -f backend/logs/polling.log

# PLC 통신 로그
tail -f backend/logs/plc.log

# 버퍼 로그
tail -f backend/logs/buffer.log

# Oracle Writer 로그
tail -f backend/logs/oracle_writer.log
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
