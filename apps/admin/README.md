# JSScada Admin Frontend

Next.js 기반 관리자 웹 애플리케이션 - 폴링 엔진 모니터링 및 제어

## 기능

### 폴링 엔진 관리
- 실시간 폴링 그룹 상태 모니터링
- 개별 그룹 시작/중지 제어
- 전체 그룹 일괄 제어
- HANDSHAKE 모드 수동 트리거
- 데이터 큐 상태 모니터링
- 성능 통계 시각화

### UI 페이지
- **HTTP Polling UI** (`/polling`): 2초 간격 HTTP 폴링
- **WebSocket UI** (`/polling-ws`): 실시간 WebSocket 업데이트

## 시스템 요구사항

- Node.js 18 이상
- npm 또는 yarn

## 설치

### 1. 의존성 설치

**프로젝트 루트에서** (monorepo):
```bash
npm install
```

**또는 apps/admin에서 직접**:
```bash
cd apps/admin
npm install
```

### 2. 환경 설정

```bash
# .env.local.example을 .env.local로 복사
cp .env.local.example .env.local

# 필요시 .env.local 파일 수정
```

`.env.local` 내용:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/polling
NEXT_PUBLIC_POLLING_INTERVAL=2000
```

## 실행

### 개발 모드

**프로젝트 루트에서** (권장):
```bash
npm run dev
```

**또는 apps/admin에서 직접**:
```bash
cd apps/admin
npm run dev
```

접속: http://localhost:3000

### 프로덕션 빌드

```bash
# 빌드
npm run build

# 실행
npm run start
```

## 사용 방법

### HTTP Polling 페이지 (`/polling`)

1. 브라우저에서 http://localhost:3000/polling 접속
2. 전체 엔진 상태가 2초마다 자동 갱신됩니다
3. 데이터 큐 상태 및 성능 차트 확인
4. 개별 그룹 또는 전체 그룹 제어

**기능**:
- 자동 새로고침 (2초 간격)
- Start All / Stop All 버튼
- 개별 그룹 Start / Stop
- HANDSHAKE 모드 Trigger Poll 버튼
- 실시간 통계 표시

### WebSocket 페이지 (`/polling-ws`)

1. 브라우저에서 http://localhost:3000/polling-ws 접속
2. WebSocket 연결로 실시간 업데이트 (1초 간격)
3. 연결 상태 표시 (초록색 점: 연결됨, 빨간색 점: 연결 끊김)
4. 연결 끊김 시 자동 재연결 (최대 10회 시도)

**기능**:
- 실시간 업데이트 (WebSocket, 1초 간격)
- 자동 재연결 (exponential backoff)
- 연결 상태 표시
- HTTP Polling 페이지와 동일한 제어 기능

## 컴포넌트

### QueueMonitor
데이터 큐 상태 시각화 컴포넌트

**기능**:
- 큐 사용률 프로그레스 바
- 경고 표시 (70% 이상, 90% 이상)
- 현재 크기, 최대 크기, 사용 가능 공간 표시

### PollingChart
폴링 성능 차트 컴포넌트

**기능**:
- 성공률 바 차트 (그룹별)
- 평균 폴링 시간 비교
- 색상 코딩 (성공률에 따라)
- Canvas 기반 렌더링

## API 클라이언트

TypeScript API 클라이언트 (`lib/api/pollingApi.ts`):

```typescript
import { pollingApi } from '@/lib/api/pollingApi';

// 엔진 상태 조회
const status = await pollingApi.getEngineStatus();

// 그룹 시작
await pollingApi.startGroup('MyGroup');

// 그룹 중지
await pollingApi.stopGroup('MyGroup');

// HANDSHAKE 트리거
const result = await pollingApi.triggerHandshake('MyGroup');
```

## WebSocket Hook

React Hook (`lib/hooks/usePollingWebSocket.ts`):

```typescript
import { usePollingWebSocket } from '@/lib/hooks/usePollingWebSocket';

function MyComponent() {
  const { status, isConnected, error, reconnect } = usePollingWebSocket();
  
  // status: 현재 엔진 상태
  // isConnected: WebSocket 연결 상태
  // error: 에러 메시지
  // reconnect: 수동 재연결 함수
}
```

## 프로젝트 구조

```
apps/admin/
├── app/
│   ├── polling/              # HTTP Polling UI
│   │   ├── page.tsx
│   │   └── components/
│   │       ├── QueueMonitor.tsx
│   │       └── PollingChart.tsx
│   └── polling-ws/           # WebSocket UI
│       └── page.tsx
├── lib/
│   ├── api/
│   │   └── pollingApi.ts     # API 클라이언트
│   └── hooks/
│       └── usePollingWebSocket.ts  # WebSocket Hook
├── public/
├── package.json
├── .env.local.example
└── README.md
```

## 스타일링

- **프레임워크**: Tailwind CSS
- **색상 팔레트**:
  - 성공: Green (bg-green-600)
  - 에러: Red (bg-red-600)
  - 경고: Yellow (bg-yellow-500)
  - FIXED 모드: Blue (bg-blue-100)
  - HANDSHAKE 모드: Purple (bg-purple-100)

## 문제 해결

### 백엔드 연결 실패

**증상**: "Failed to fetch status" 에러

**해결**:
1. 백엔드 서버가 실행 중인지 확인: http://localhost:8000/health
2. `.env.local`의 `NEXT_PUBLIC_API_URL` 확인
3. CORS 설정 확인 (백엔드 `main.py`)

### WebSocket 연결 실패

**증상**: "Disconnected" 상태 유지

**해결**:
1. 백엔드 WebSocket 엔드포인트 확인: ws://localhost:8000/ws/polling
2. `.env.local`의 `NEXT_PUBLIC_WS_URL` 확인
3. 방화벽/프록시 설정 확인

### 자동 새로고침이 작동하지 않음

**증상**: 데이터가 업데이트되지 않음

**해결**:
1. 브라우저 콘솔에서 에러 확인
2. 네트워크 탭에서 API 요청 확인
3. 페이지 새로고침 시도

## 개발

### 코드 스타일

```bash
# Lint 실행
npm run lint

# Lint 자동 수정
npm run lint -- --fix
```

### 타입 체크

```bash
# TypeScript 컴파일 확인
npx tsc --noEmit
```

### 새로운 페이지 추가

1. `app/` 디렉토리에 새 폴더 생성
2. `page.tsx` 파일 작성
3. 필요시 `components/` 하위 디렉토리 생성

## 라이선스

Proprietary - 내부 사용 전용

## 문의

프로젝트 관련 문의: JSScada Development Team
