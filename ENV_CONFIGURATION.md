# 환경설정 파일 시스템 (.env)

## 개요

SCADA 시스템의 모든 설정을 `.env` 파일로 관리합니다. 외부 환경변수 설정 없이 파일 하나로 모든 설정을 제어할 수 있습니다.

---

## 설정 파일 위치

```
backend/.env         # 실제 설정 파일 (Git 무시됨)
backend/.env.example # 설정 예시 파일 (Git 추적됨)
```

---

## 초기 설정

### 1. .env 파일 생성

```bash
# .env.example을 복사하여 .env 파일 생성
cd backend
copy .env.example .env  # Windows
# 또는
cp .env.example .env    # Linux/Mac
```

### 2. 설정 수정

`.env` 파일을 열어서 필요한 설정을 수정합니다:

```bash
# backend/.env
LOG_LEVEL=DEBUG        # 개발 환경에서는 DEBUG
LOG_COLORS=true        # 컬러풀한 터미널 출력
LOG_DIR=logs           # 로그 저장 디렉토리

API_HOST=0.0.0.0
API_PORT=8000

ORACLE_HOST=192.168.1.100
ORACLE_USERNAME=my_user
ORACLE_PASSWORD=my_password
```

---

## 주요 설정 항목

### 로깅 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `LOG_LEVEL` | `INFO` | 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_COLORS` | `true` | 터미널 컬러 사용 여부 (true/false) |
| `LOG_DIR` | `logs` | 로그 파일 저장 디렉토리 |
| `LOG_MAX_BYTES` | `10485760` | 로그 파일 최대 크기 (10MB) |
| `LOG_BACKUP_COUNT` | `10` | 로그 파일 백업 개수 |

**예시:**
```bash
# 개발 환경 (모든 로그 출력)
LOG_LEVEL=DEBUG
LOG_COLORS=true

# 운영 환경 (에러만 출력, 컬러 비활성화)
LOG_LEVEL=ERROR
LOG_COLORS=false
```

### 서버 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `API_HOST` | `0.0.0.0` | API 서버 호스트 |
| `API_PORT` | `8000` | API 서버 포트 |
| `API_RELOAD` | `true` | 개발 모드 자동 리로드 |
| `ENVIRONMENT` | `development` | 환경 (development, production) |

### 데이터베이스 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `DATABASE_PATH` | `config/scada.db` | SQLite DB 경로 |
| `ORACLE_HOST` | `localhost` | Oracle DB 호스트 |
| `ORACLE_PORT` | `1521` | Oracle DB 포트 |
| `ORACLE_SERVICE_NAME` | `ORCL` | Oracle 서비스명 |
| `ORACLE_USERNAME` | `scada_user` | Oracle 사용자명 |
| `ORACLE_PASSWORD` | `scada_password` | Oracle 비밀번호 |

### PLC 통신 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `CONNECTION_TIMEOUT` | `5` | PLC 연결 타임아웃 (초) |
| `READ_TIMEOUT` | `3` | PLC 읽기 타임아웃 (초) |
| `POOL_SIZE_PER_PLC` | `5` | PLC당 커넥션 풀 크기 |
| `IDLE_TIMEOUT` | `600` | 유휴 커넥션 타임아웃 (초) |

### 폴링 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `MAX_POLLING_GROUPS` | `10` | 최대 폴링 그룹 수 |
| `DATA_QUEUE_SIZE` | `10000` | 데이터 큐 크기 |
| `WEBSOCKET_BROADCAST_INTERVAL` | `1.0` | WebSocket 브로드캐스트 간격 (초) |

### 버퍼 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `BUFFER_MAX_SIZE` | `100000` | 버퍼 최대 크기 |
| `BUFFER_BATCH_SIZE` | `500` | 배치 쓰기 크기 |
| `BUFFER_WRITE_INTERVAL` | `1.0` | 버퍼 쓰기 간격 (초) |
| `BUFFER_RETRY_COUNT` | `3` | 쓰기 재시도 횟수 |
| `BACKUP_FILE_PATH` | `backup` | 백업 파일 경로 |

---

## 코드에서 사용하기

### 1. Settings 객체 사용

```python
from src.config.settings import settings

# 로그 레벨 가져오기
log_level = settings.LOG_LEVEL
log_level_int = settings.LOG_LEVEL_INT

# 데이터베이스 연결 정보
db_path = settings.DATABASE_PATH
oracle_host = settings.ORACLE_HOST
oracle_user = settings.ORACLE_USERNAME

# 서버 설정
api_host = settings.API_HOST
api_port = settings.API_PORT
```

### 2. 로깅 초기화

```python
from src.config.logging_config import initialize_logging

# .env 파일의 설정 사용
initialize_logging()

# 특정 설정으로 오버라이드
initialize_logging(console_level=logging.DEBUG)

# 컬러 비활성화
initialize_logging(use_colors=False)
```

### 3. 전체 설정 출력

```python
from src.config.settings import settings

# 모든 설정 출력
settings.display_config()
```

---

## 환경별 설정 예시

### 개발 환경 (backend/.env)

```bash
# Logging - 상세한 디버그 로그
LOG_LEVEL=DEBUG
LOG_COLORS=true
LOG_DIR=logs

# Server - 로컬 개발
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true
ENVIRONMENT=development

# Database - 로컬 테스트 DB
ORACLE_HOST=localhost
ORACLE_USERNAME=dev_user
ORACLE_PASSWORD=dev_password

# PLC - 짧은 타임아웃 (빠른 피드백)
CONNECTION_TIMEOUT=3
READ_TIMEOUT=2
```

### 운영 환경 (backend/.env)

```bash
# Logging - 에러만 기록
LOG_LEVEL=ERROR
LOG_COLORS=false
LOG_DIR=/var/log/scada

# Server - 프로덕션 서버
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
ENVIRONMENT=production

# Database - 실제 운영 DB
ORACLE_HOST=192.168.100.10
ORACLE_USERNAME=scada_prod
ORACLE_PASSWORD=secure_password_here

# PLC - 안정적인 타임아웃
CONNECTION_TIMEOUT=5
READ_TIMEOUT=3

# Buffer - 대용량 처리
BUFFER_MAX_SIZE=500000
BUFFER_BATCH_SIZE=1000
```

---

## 백엔드 실행 방법

### 기본 실행 (.env 파일 사용)

```bash
cd d:\Project\JSOPCUA\backend

# 1. .env 파일 확인 및 수정
notepad .env

# 2. 백엔드 실행
.venv\Scripts\python.exe src\api\main.py
```

**외부 환경변수 설정 불필요!** `.env` 파일만 수정하면 됩니다.

### 개발 모드 (자동 리로드)

```bash
# .env에서 API_RELOAD=true로 설정하거나
.venv\Scripts\uvicorn src.api.main:app --reload
```

### 설정 확인

```bash
# 현재 설정 출력
.venv\Scripts\python.exe -c "from src.config.settings import settings; settings.display_config()"
```

---

## 테스트

### 설정 테스트 스크립트

```bash
cd backend
.venv\Scripts\python.exe src\scripts\test_env_config.py
```

**테스트 내용:**
- ✅ .env 파일 로딩 확인
- ✅ 모든 설정값 읽기 확인
- ✅ 로깅 초기화 확인
- ✅ 파라미터 오버라이드 확인
- ✅ 전체 설정 출력 확인

---

## 설정 변경 워크플로우

### 1. 로그 레벨 변경

```bash
# 1. .env 파일 수정
notepad backend\.env

# 변경 전:
LOG_LEVEL=INFO

# 변경 후:
LOG_LEVEL=DEBUG

# 2. 애플리케이션 재시작
# (재시작 시 자동으로 새 설정 적용)
```

### 2. Oracle DB 연결 정보 변경

```bash
# 1. .env 파일 수정
notepad backend\.env

# 변경:
ORACLE_HOST=192.168.1.100
ORACLE_USERNAME=new_user
ORACLE_PASSWORD=new_password

# 2. 애플리케이션 재시작
```

### 3. 여러 환경 관리

```bash
# 개발 환경 설정
cp backend/.env.dev backend/.env

# 운영 환경 설정
cp backend/.env.prod backend/.env

# 테스트 환경 설정
cp backend/.env.test backend/.env
```

---

## 보안 고려사항

### .gitignore 설정

`.env` 파일은 **절대 Git에 커밋하지 않습니다**:

```bash
# .gitignore (이미 설정되어 있음)
backend/.env
*.env
```

### 민감한 정보 관리

```bash
# ❌ 잘못된 예 - .env 파일을 Git에 커밋
git add backend/.env

# ✅ 올바른 예 - .env.example만 커밋
git add backend/.env.example
```

### .env.example 업데이트

새로운 설정을 추가할 때는 `.env.example`도 함께 업데이트:

```bash
# 1. 새 설정 추가
echo "NEW_SETTING=default_value" >> backend/.env

# 2. .env.example에도 추가
echo "NEW_SETTING=default_value" >> backend/.env.example

# 3. .env.example만 커밋
git add backend/.env.example
git commit -m "Add NEW_SETTING configuration"
```

---

## 문제 해결

### Q: .env 파일이 로드되지 않아요

```bash
# 1. .env 파일 존재 확인
dir backend\.env

# 2. 파일이 없으면 .env.example 복사
copy backend\.env.example backend\.env

# 3. python-dotenv 패키지 확인
.venv\Scripts\pip.exe show python-dotenv
```

### Q: 설정이 적용되지 않아요

```bash
# 1. 애플리케이션 재시작 필요
# .env 파일은 시작 시에만 로드됩니다

# 2. 현재 설정 확인
.venv\Scripts\python.exe -c "from src.config.settings import settings; print(settings.LOG_LEVEL)"

# 3. .env 파일 문법 확인
# 주석은 #으로 시작
# 공백 없이 KEY=VALUE 형식
```

### Q: 환경변수와 .env 파일 중 어느 것이 우선인가요?

**우선순위:**
1. 함수 파라미터 (가장 높음)
2. .env 파일
3. 기본값 (가장 낮음)

```python
# 예시:
# .env 파일: LOG_LEVEL=INFO
initialize_logging(console_level=logging.DEBUG)  # DEBUG 적용 (파라미터 우선)
```

---

## 이전 방식과의 비교

### 이전 (환경변수 방식) ❌

```bash
# Windows
set LOG_LEVEL=DEBUG
set ORACLE_HOST=localhost
set ORACLE_USERNAME=user
set ORACLE_PASSWORD=password
python.exe src\api\main.py

# 단점:
# - 매번 환경변수 설정 필요
# - 환경변수가 세션에만 유효
# - 관리가 어려움
```

### 현재 (.env 파일 방식) ✅

```bash
# 1. 한 번만 설정 (backend/.env)
LOG_LEVEL=DEBUG
ORACLE_HOST=localhost
ORACLE_USERNAME=user
ORACLE_PASSWORD=password

# 2. 실행 (설정 자동 로드)
python.exe src\api\main.py

# 장점:
# - 파일 하나로 모든 설정 관리
# - 버전 관리 가능 (.env.example)
# - 환경별 설정 파일 분리 가능
# - 외부 환경변수 설정 불필요
```

---

## 관련 파일

- **설정 파일**: `backend/.env` (실제 설정)
- **예시 파일**: `backend/.env.example` (Git 추적)
- **설정 모듈**: `backend/src/config/settings.py`
- **로깅 모듈**: `backend/src/config/logging_config.py`
- **테스트 스크립트**: `backend/src/scripts/test_env_config.py`

---

**Status:** ✅ 구현 완료

**최종 업데이트:** 2025-11-05
