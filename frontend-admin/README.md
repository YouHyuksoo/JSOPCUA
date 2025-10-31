# JSScada Admin Web Application

Next.js 기반 관리 웹 애플리케이션입니다. 시스템 관리 및 폴링 제어 기능을 제공합니다.

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

브라우저에서 [http://localhost:3000](http://localhost:3000)을 엽니다.

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
frontend-admin/
├── app/             # Next.js App Router
│   ├── page.tsx     # 홈페이지
│   └── layout.tsx   # 레이아웃
├── components/      # React 컴포넌트
│   └── ui/          # UI 컴포넌트
├── lib/             # 유틸리티 함수
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

## 환경 변수

`.env.local` 파일 생성:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

## 개발 가이드

### 코드 스타일

- ESLint 설정 준수
- TypeScript strict 모드 사용
- 컴포넌트는 함수형 컴포넌트로 작성
- React Hooks 사용

### 컴포넌트 작성

```tsx
// components/ui/Button.tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export default function Button({ label, onClick }: ButtonProps) {
  return (
    <button onClick={onClick}>
      {label}
    </button>
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
docker build -t jsscada-admin .
docker run -p 3000:3000 jsscada-admin
```

## 라이선스

Proprietary
