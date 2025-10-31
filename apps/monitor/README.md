# JSScada Monitor Web Application

Next.js 기반 실시간 모니터링 대시보드입니다.

## 모노레포 구조

이 애플리케이션은 JSScada 모노레포의 일부입니다.

```
JSOPCUA/
├── apps/
│   ├── admin/
│   └── monitor/     # 이 앱
├── packages/
│   ├── ui/         # 공용 UI 컴포넌트 (@jsscada/ui)
│   └── utils/      # 공용 유틸리티 (@jsscada/utils)
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
# 루트에서 monitor만 실행
npm run dev:monitor

# 또는 monitor 디렉토리에서
cd apps/monitor
npm run dev
```

브라우저에서 [http://localhost:3001](http://localhost:3001)을 엽니다.

## 공용 패키지 사용

```typescript
// UI 컴포넌트 사용
import { Card, Table } from '@jsscada/ui';

// 유틸리티 함수 사용
import { formatValue, wsClient } from '@jsscada/utils';

export default function Dashboard() {
  return (
    <Card>
      <Table data={tagData} />
    </Card>
  );
}
```

## 빌드

```bash
# 루트에서 모든 앱 빌드
npm run build

# 또는 monitor만 빌드
npm run build:monitor
```

## 프로젝트 구조

```
apps/monitor/
├── app/             # Next.js App Router
│   ├── page.tsx     # 대시보드 페이지
│   └── layout.tsx   # 레이아웃
├── components/      # 앱 전용 React 컴포넌트
├── lib/             # 앱 전용 유틸리티 함수
├── public/          # 정적 파일
└── package.json
```

## 주요 기능 (향후 구현)

### Feature 7: 모니터링 웹 기능
- **실시간 대시보드**: WebSocket을 통한 실시간 태그 값 표시
- **라인별 뷰**: 생산 라인별 공정 및 태그 모니터링
- **알람 표시**: 태그 값 이상 시 알람 표시
- **트렌드 차트**: 태그 값의 시간별 변화 그래프

## 기술 스택

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript 5.3+
- **Styling**: Tailwind CSS (향후)
- **Charts**: Chart.js 또는 Recharts (향후)
- **Real-time**: WebSocket (향후)
- **Shared Packages**: @jsscada/ui, @jsscada/utils

## 환경 변수

`.env.local` 파일 생성:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

## 라이선스

Proprietary
