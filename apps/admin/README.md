# JSScada Admin Web Application

Next.js 기반 관리 웹 애플리케이션입니다. 시스템 관리 및 폴링 제어 기능을 제공합니다.

## 모노레포 구조

이 애플리케이션은 JSScada 모노레포의 일부입니다.

```
JSOPCUA/
├── apps/
│   ├── admin/        # 이 앱
│   └── monitor/
├── packages/
│   ├── ui/          # 공용 UI 컴포넌트 (@jsscada/ui)
│   └── utils/       # 공용 유틸리티 (@jsscada/utils)
└── backend/
```

## 요구사항

- Node.js 20 이상
- npm 또는 yarn

## 설치 (모노레포 루트에서)

```bash
# 루트에서 모든 워크스페이스 설치
npm install
```

## 개발 서버 실행

```bash
# 루트에서 admin만 실행
npm run dev:admin

# 또는 admin 디렉토리에서
cd apps/admin
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 엽니다.

## 공용 패키지 사용

```typescript
// UI 컴포넌트 사용
import { Button, Card } from '@jsscada/ui';

// 유틸리티 함수 사용
import { formatDate, apiClient } from '@jsscada/utils';

export default function Page() {
  return (
    <Card>
      <Button>클릭</Button>
    </Card>
  );
}
```

## 빌드

```bash
# 루트에서 모든 앱 빌드
npm run build

# 또는 admin만 빌드
npm run build:admin
```

## 프로젝트 구조

```
apps/admin/
├── app/             # Next.js App Router
│   ├── page.tsx     # 홈페이지
│   └── layout.tsx   # 레이아웃
├── components/      # 앱 전용 React 컴포넌트
├── lib/             # 앱 전용 유틸리티 함수
├── public/          # 정적 파일
└── package.json
```

## 주요 기능 (향후 구현)

### Feature 6: 관리 웹 기능
- **폴링 제어**: PLC 폴링 시작/중지
- **시스템 관리**: 라인, 공정, PLC, 태그 관리
- **실시간 상태**: WebSocket을 통한 실시간 시스템 상태 모니터링
- **설정 관리**: 폴링 그룹, 연결 설정 관리

## 기술 스택

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript 5.3+
- **Styling**: Tailwind CSS (향후)
- **State Management**: React Context (향후)
- **API Communication**: REST API, WebSocket (향후)
- **Shared Packages**: @jsscada/ui, @jsscada/utils

## 환경 변수

`.env.local` 파일 생성:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

## 라이선스

Proprietary
