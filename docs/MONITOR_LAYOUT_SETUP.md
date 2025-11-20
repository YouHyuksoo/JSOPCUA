# 모니터 레이아웃 편집 기능 실행 가이드

## 1단계: 데이터베이스 테이블 생성

먼저 `equipment_positions` 테이블을 생성해야 합니다.

### 방법 1: SQLite 명령어로 직접 실행

```bash
# 프로젝트 루트에서 실행
cd backend
sqlite3 data/scada.db < ../backend/data/add_equipment_positions.sql
```

### 방법 2: Python 스크립트로 실행

```bash
# 프로젝트 루트에서 실행
cd backend
python -c "
import sqlite3
conn = sqlite3.connect('data/scada.db')
with open('data/add_equipment_positions.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())
conn.close()
print('✅ equipment_positions 테이블 생성 완료')
"
```

### 방법 3: SQLite GUI 도구 사용

- DB Browser for SQLite 또는 다른 SQLite 도구를 사용하여
- `backend/data/add_equipment_positions.sql` 파일의 내용을 실행

## 2단계: 백엔드 서버 실행

### Windows 환경

```bash
# 프로젝트 루트에서 실행
start-backend.bat
```

또는 수동으로:

```bash
cd backend
.venv\Scripts\activate
uvicorn src.api.main:app --reload
```

### 확인 사항

- 서버가 `http://localhost:8000`에서 실행되는지 확인
- 브라우저에서 `http://localhost:8000/docs` 접속하여 API 문서 확인
- `/api/monitor/equipment-positions` 엔드포인트가 보이는지 확인

## 3단계: 프론트엔드 서버 실행

### 관리자 웹 (Admin) 실행

```bash
# 프로젝트 루트에서 실행
npm run dev:admin
```

또는:

```bash
cd apps/admin
npm run dev
```

- 관리자 웹: `http://localhost:3000`

### 모니터 웹 (Monitor) 실행 (선택사항)

```bash
# 프로젝트 루트에서 실행
npm run dev:monitor
```

또는:

```bash
cd apps/monitor
npm run dev
```

- 모니터 웹: `http://localhost:3001`

## 4단계: 테스트 방법

### 1. 관리자 페이지 접속

1. 브라우저에서 `http://localhost:3000` 접속
2. 왼쪽 사이드바에서 **"모니터 레이아웃"** 메뉴 클릭
3. 또는 직접 `http://localhost:3000/monitor-layout` 접속

### 2. 설비 위치 편집

#### 드래그 앤 드롭으로 위치 조정
1. 공정 목록이 자동으로 로드됩니다
2. 각 설비 박스를 **마우스로 드래그**하여 원하는 위치로 이동
3. 박스가 선택되면 노란색 테두리가 표시됩니다

#### 좌표 직접 입력
1. 박스를 **클릭**하여 선택
2. 우측 패널에서 X, Y 좌표 및 너비, 높이를 직접 입력
3. Enter 키를 누르면 즉시 반영됩니다

#### 배경 이미지 설정
1. 상단의 "배경 이미지 URL" 입력란에 이미지 경로 입력
   - 예: `/equipment-layout.png` (public 폴더 기준)
   - 또는 외부 URL: `https://example.com/image.png`

### 3. 위치 저장

1. 우측 상단의 **"저장"** 버튼 클릭
2. 성공 메시지가 표시되면 저장 완료
3. 저장된 위치는 모니터 페이지에서 자동으로 사용됩니다

### 4. 모니터 페이지에서 확인

1. `http://localhost:3001` 접속 (모니터 웹 실행 시)
2. 저장한 위치대로 설비 박스가 배치되어 있는지 확인
3. 배경 이미지 위에 반투명 박스로 표시됩니다

## 문제 해결

### 문제 1: "equipment_positions 테이블이 없습니다" 에러

**해결 방법:**
- 1단계를 다시 확인하고 테이블이 생성되었는지 확인
- SQLite에서 직접 확인:
  ```bash
  sqlite3 backend/data/scada.db
  .tables
  # equipment_positions가 보여야 함
  ```

### 문제 2: 공정 목록이 보이지 않음

**해결 방법:**
- 관리자 페이지에서 "공정 (Processes)" 메뉴로 이동하여 공정이 등록되어 있는지 확인
- 공정이 없으면 먼저 공정을 등록해야 합니다

### 문제 3: API 연결 오류

**해결 방법:**
- 백엔드 서버가 실행 중인지 확인 (`http://localhost:8000`)
- 브라우저 개발자 도구(F12)의 Network 탭에서 API 요청 확인
- CORS 오류가 있으면 백엔드의 CORS 설정 확인

### 문제 4: 드래그가 작동하지 않음

**해결 방법:**
- 브라우저 콘솔에서 에러 메시지 확인
- 페이지를 새로고침하고 다시 시도
- 다른 브라우저에서 테스트

## 빠른 테스트 체크리스트

- [ ] 데이터베이스 테이블 생성 완료
- [ ] 백엔드 서버 실행 중 (`http://localhost:8000`)
- [ ] 관리자 웹 실행 중 (`http://localhost:3000`)
- [ ] `/monitor-layout` 페이지 접속 가능
- [ ] 공정 목록이 표시됨
- [ ] 박스 드래그 가능
- [ ] 좌표 입력 가능
- [ ] 저장 기능 작동
- [ ] 모니터 페이지에서 위치 확인 가능

## 다음 단계

위치 편집이 완료되면:
1. 모니터 페이지에서 실시간으로 설비 상태 확인
2. WebSocket 연결을 통해 실시간 데이터 수신 확인
3. 배경 이미지를 실제 설비 배치도로 교체

