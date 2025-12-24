# Quickstart: 실시간 설비 모니터링 웹 UI

## 개요

이 문서는 Feature 7 (실시간 설비 모니터링 웹 UI)를 로컬 환경에서 실행하고 테스트하는 방법을 안내합니다.

---

## 사전 요구사항

### 1. 완료된 Feature
- ✅ Feature 1: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정
- ✅ Feature 2: MC 3E ASCII 프로토콜 통신 및 Connection Pool
- ✅ Feature 3: 멀티 스레드 폴링 엔진
- ✅ Feature 4: 메모리 버퍼 및 Oracle DB Writer
- ✅ Feature 5: 데이터베이스 관리 REST API
- ✅ Feature 6: Admin 웹 UI (시스템 관리)

### 2. 환경 설정
- Node.js 18+ 설치
- Python 3.11+ 설치
- Oracle DB 접속 가능 (python-oracledb 설정 완료)
- PLC 연결 (선택사항, 시뮬레이션 모드 가능)

### 3. 설치 확인
```bash
# Node.js 버전 확인
node --version  # v18 이상

# Python 버전 확인
python --version  # 3.11 이상

# 모노레포 의존성 설치 확인
npm list  # apps/admin, apps/monitor 확인
```

---

## 1. 프로젝트 설치

### 1.1 루트 디렉토리에서 전체 설치
```bash
cd D:/Project/JSOPCUA

# 모노레포 의존성 설치 (admin + monitor)
npm install
```

### 1.2 백엔드 의존성 설치
```bash
cd backend

# 가상 환경 활성화 (이미 생성되어 있다고 가정)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 의존성 설치 (python-oracledb 포함)
pip install -r requirements.txt
```

---

## 2. Oracle DB 설정

### 2.1 환경 변수 설정
```bash
cd backend

# .env 파일 확인 및 수정
# ORACLE_USER=your_username
# ORACLE_PASSWORD=your_password
# ORACLE_DSN=localhost:1521/ORCLPDB
```

### 2.2 알람 테이블 생성 (선택사항)
Oracle DB에 `ALARMS` 테이블이 없는 경우 생성합니다.

```sql
-- Oracle SQL*Plus 또는 SQL Developer에서 실행
CREATE TABLE ALARMS (
    ALARM_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    EQUIPMENT_CODE VARCHAR2(50) NOT NULL,
    ALARM_TYPE VARCHAR2(20) NOT NULL,
    ALARM_MESSAGE VARCHAR2(500),
    OCCURRED_AT TIMESTAMP NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IDX_ALARMS_OCCURRED ON ALARMS(OCCURRED_AT DESC);
CREATE INDEX IDX_ALARMS_EQUIPMENT ON ALARMS(EQUIPMENT_CODE, OCCURRED_AT DESC);

-- 테스트 데이터 삽입 (선택사항)
INSERT INTO ALARMS (EQUIPMENT_CODE, ALARM_TYPE, ALARM_MESSAGE, OCCURRED_AT)
VALUES ('KRCWO12ELOA101', '알람', '온도 과열 경고', CURRENT_TIMESTAMP);

INSERT INTO ALARMS (EQUIPMENT_CODE, ALARM_TYPE, ALARM_MESSAGE, OCCURRED_AT)
VALUES ('KRCWO12ELOA102', '일반', '용접 전류 이상', CURRENT_TIMESTAMP - INTERVAL '1' MINUTE);

COMMIT;
```

---

## 3. 백엔드 실행

### 3.1 FastAPI 서버 시작
```bash
cd D:/Project/JSOPCUA/backend

# 가상 환경 활성화
venv\Scripts\activate

# FastAPI 서버 실행
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**확인**:
- 브라우저에서 `http://localhost:8000/docs` 접속
- `/api/alarms/statistics`, `/api/alarms/recent` 엔드포인트 확인

### 3.2 폴링 엔진 시작 (선택사항)
WebSocket 실시간 설비 상태 업데이트를 위해 폴링 그룹을 시작합니다.

```bash
# Admin UI (http://localhost:3000)에서 폴링 그룹 시작
# 또는 REST API 호출:
curl -X POST http://localhost:8000/api/polling-groups/1/start
```

---

## 4. Monitor 웹 UI 실행

### 4.1 개발 서버 시작
```bash
cd D:/Project/JSOPCUA

# Monitor UI 개발 서버 실행
npm run dev:monitor
```

**확인**:
- 브라우저에서 `http://localhost:3001` 접속
- 17개 설비 상태 박스가 표시되는지 확인

### 4.2 전체 환경 실행 (Admin + Monitor)
```bash
# 루트 디렉토리에서 모든 웹 UI 실행
npm run dev

# 결과:
# - Admin UI: http://localhost:3000
# - Monitor UI: http://localhost:3001
```

---

## 5. 기능 테스트

### 5.1 WebSocket 연결 테스트
1. Monitor UI (`http://localhost:3001`) 접속
2. 브라우저 개발자 도구 (F12) → Console 탭 열기
3. 콘솔에서 WebSocket 연결 로그 확인:
   ```
   WebSocket connected
   ```
4. 1초마다 설비 상태 메시지 수신 확인

### 5.2 알람 통계 테스트
1. Monitor UI 상단에 17개 설비 그리드 표시 확인
2. 각 설비의 "알람 합계"와 "일반" 건수 확인
3. 우측 하단 "C/Time: 10초" 텍스트 확인
4. 10초 후 그리드가 자동 갱신되는지 확인

### 5.3 최근 알람 목록 테스트
1. Monitor UI 하단 우측에 최근 5개 알람 목록 확인
2. 각 알람의 시간(HH:MM) 형식과 메시지 표시 확인
3. 10초 후 목록이 자동 갱신되는지 확인

### 5.4 설비 상태 색상 테스트
1. 설비 상태 박스가 5가지 색상으로 표시되는지 확인:
   - **Green**: 가동 (status='running', error_tag=0, connection=true)
   - **Yellow**: 비가동 (status='idle')
   - **Red**: 정지 (status='stopped')
   - **Purple**: 설비이상 (error_tag=1)
   - **Gray**: 접속이상 (connection=false)

2. PLC 연결을 끊어서 Gray 상태로 변경되는지 테스트 (선택사항)

### 5.5 WebSocket 재연결 테스트
1. 백엔드 FastAPI 서버 중지 (`Ctrl+C`)
2. Monitor UI에서 "WebSocket 연결 실패" 경고 메시지 확인
3. 모든 설비가 Gray(접속이상)로 변경되는지 확인
4. 백엔드 서버 재시작
5. 3초 이내에 자동 재연결되고 설비 상태가 복구되는지 확인

---

## 6. API 엔드포인트 테스트

### 6.1 알람 통계 API
```bash
curl http://localhost:8000/api/alarms/statistics
```

**예상 응답**:
```json
{
  "equipment": [
    {
      "equipment_code": "KRCWO12ELOA101",
      "equipment_name": "Upper 로봇 용접",
      "alarm_count": 5,
      "general_count": 3
    },
    ...
  ],
  "last_updated": "2025-11-03T10:30:45.123Z"
}
```

### 6.2 최근 알람 목록 API
```bash
curl http://localhost:8000/api/alarms/recent?limit=5
```

**예상 응답**:
```json
{
  "alarms": [
    {
      "alarm_id": 12345,
      "equipment_code": "KRCWO12ELOA101",
      "equipment_name": "Upper 로봇 용접",
      "alarm_type": "알람",
      "alarm_message": "온도 과열 경고",
      "occurred_at": "2025-11-03T10:28:15.000Z"
    },
    ...
  ]
}
```

### 6.3 WebSocket 연결 테스트 (websocat)
```bash
# websocat 설치 (Windows)
scoop install websocat

# WebSocket 연결 테스트
websocat ws://localhost:8000/ws/monitor

# 예상 출력 (1초마다):
# {"type":"equipment_status","timestamp":"2025-11-03T10:30:45.123Z","equipment":[...]}
```

---

## 7. 문제 해결 (Troubleshooting)

### 7.1 WebSocket 연결 실패
**증상**: "WebSocket 연결 실패" 메시지, 모든 설비 Gray

**해결 방법**:
1. 백엔드 FastAPI 서버가 실행 중인지 확인:
   ```bash
   curl http://localhost:8000/docs
   ```
2. 폴링 그룹이 시작되었는지 확인 (Admin UI에서 확인)
3. 방화벽 또는 CORS 설정 확인

### 7.2 Oracle DB 연결 실패
**증상**: 알람 통계/최근 알람 목록에 에러 메시지 표시

**해결 방법**:
1. Oracle DB 접속 정보 확인 (`backend/.env`)
2. python-oracledb 설치 확인:
   ```bash
   pip show python-oracledb
   ```
3. Oracle DB 연결 테스트:
   ```bash
   python backend/src/scripts/test_oracle_connection.py
   ```

### 7.3 설비 상태가 업데이트되지 않음
**증상**: 설비 상태 박스가 Gray에서 변경되지 않음

**해결 방법**:
1. 폴링 그룹이 시작되었는지 확인
2. PLC 연결 상태 확인 (Admin UI → PLC 관리 → 연결 테스트)
3. 백엔드 로그 확인:
   ```bash
   tail -f backend/logs/scada.log
   ```

### 7.4 알람 데이터가 표시되지 않음
**증상**: 상단 그리드 및 하단 알람 목록이 비어 있음

**해결 방법**:
1. Oracle DB `ALARMS` 테이블에 데이터가 있는지 확인:
   ```sql
   SELECT COUNT(*) FROM ALARMS;
   ```
2. 테스트 데이터 삽입 (Section 2.2 참조)
3. API 엔드포인트 직접 호출하여 응답 확인 (Section 6.1, 6.2)

---

## 8. 추가 리소스

### 8.1 관련 문서
- [spec.md](./spec.md) - Feature 7 명세서
- [plan.md](./plan.md) - 구현 계획
- [data-model.md](./data-model.md) - 데이터 모델
- [contracts/websocket.md](./contracts/websocket.md) - WebSocket 계약
- [contracts/openapi.yaml](./contracts/openapi.yaml) - REST API 계약

### 8.2 API 문서
- FastAPI Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 8.3 로그 파일
- SCADA 로그: `backend/logs/scada.log`
- 에러 로그: `backend/logs/error.log`
- 통신 로그: `backend/logs/communication.log`
- 성능 로그: `backend/logs/performance.log`

---

## 9. 다음 단계

Feature 7 구현이 완료되면:
1. `/speckit.tasks` 명령으로 작업 분할 생성
2. `/speckit.implement` 명령으로 자동 구현 실행
3. 모든 요구사항 검증 ([checklists/requirements.md](./checklists/requirements.md))
4. Feature 8 (통합 테스트 및 배포 준비)로 진행

---

## 10. 지원

문제 발생 시:
1. 이 문서의 "문제 해결" 섹션 참조
2. 백엔드 로그 파일 확인
3. 브라우저 개발자 도구 콘솔 확인
4. 개발팀에 문의
