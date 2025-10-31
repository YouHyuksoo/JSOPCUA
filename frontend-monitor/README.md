# JSScada Monitor Web Application

Next.js 기반 실시간 모니터링 대시보드입니다.

## 요구사항

- Node.js 20 이상
- npm 또는 yarn

## 설치

```bash
npm install
# 또는
yarn install
```

## 개발 서버 실행

```bash
npm run dev
# 또는
yarn dev
```

브라우저에서 [http://localhost:3001](http://localhost:3001)을 엽니다.

## 빌드

```bash
npm run build
# 또는
yarn build
```

## 프로덕션 실행

```bash
npm run start
# 또는
yarn start
```

## 프로젝트 구조

```
frontend-monitor/
├── app/             # Next.js App Router
│   ├── page.tsx     # 대시보드 페이지
│   └── layout.tsx   # 레이아웃
├── components/      # React 컴포넌트
│   └── ui/          # UI 컴포넌트
├── lib/             # 유틸리티 함수
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

## 환경 변수

`.env.local` 파일 생성:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

## 개발 가이드

### 실시간 데이터 처리

```tsx
// WebSocket 연결 예시 (향후)
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [tags, setTags] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTags(data.tags);
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      {tags.map(tag => (
        <div key={tag.id}>
          {tag.name}: {tag.value} {tag.unit}
        </div>
      ))}
    </div>
  );
}
```

## 배포

### Vercel 배포

```bash
npm install -g vercel
vercel
```

### Docker 배포

```bash
docker build -t jsscada-monitor .
docker run -p 3001:3001 jsscada-monitor
```

## 성능 최적화

- React.memo를 사용한 컴포넌트 메모이제이션
- WebSocket 재연결 로직
- 태그 값 업데이트 시 필요한 컴포넌트만 리렌더링

## 라이선스

Proprietary
