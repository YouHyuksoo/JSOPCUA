# JSScada Admin Web Application

Next.js 기반 SCADA 시스템 관리 웹 애플리케이션

## 기능

### 1. 마스터 데이터 관리
- **라인 관리**: 생산 라인 CRUD
- **공정 관리**: 공정 CRUD 및 라인 연결
- **PLC 관리**: PLC 연결 정보 관리 및 연결 테스트
- **태그 관리**: 태그 CRUD 및 CSV 일괄 업로드

### 2. 폴링 제어
- **폴링 그룹 관리**: 폴링 그룹 생성 및 설정
- **폴링 제어**: 시작/중지/재시작 기능
- **태그 그룹화**: 폴링 주기별 태그 그룹 설정

### 3. 시스템 모니터링
- **실시간 대시보드**: CPU, 메모리, 디스크 사용률
- **PLC 연결 상태**: 연결된 PLC 수 및 상태
- **폴링 그룹 상태**: 실행 중인 그룹 수
- **버퍼 상태**: 버퍼 크기 및 사용률

### 4. 로그 조회
- **4종 로그 파일**: scada.log, error.log, communication.log, performance.log
- **로그 필터링**: 로그 타입별 조회
- **실시간 조회**: 최신 로그 100개 조회

## 기술 스택

- **Framework**: Next.js 14.2.33 (App Router)
- **Language**: TypeScript 5.3+
- **UI Library**: shadcn/ui
- **Styling**: Tailwind CSS
- **Form Management**: React Hook Form + Zod
- **HTTP Client**: Axios
- **CSV Processing**: Papa Parse
- **Toast Notifications**: Sonner

## 설치 및 실행

### 설치
```bash
npm install
```

### 개발 서버 실행
```bash
npm run dev
```

애플리케이션이 http://localhost:3000 에서 실행됩니다.

### 빌드
```bash
npm run build
```

### 프로덕션 실행
```bash
npm start
```

## 환경 변수

`.env.local` 파일을 생성하고 다음 변수를 설정하세요:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## 프로젝트 구조

```
apps/admin/
├── app/                      # Next.js App Router 페이지
│   ├── dashboard/           # 시스템 대시보드
│   ├── lines/               # 라인 관리
│   ├── logs/                # 로그 조회
│   ├── plcs/                # PLC 관리
│   ├── polling-groups/      # 폴링 그룹 관리
│   ├── processes/           # 공정 관리
│   ├── tags/                # 태그 관리
│   ├── layout.tsx           # 루트 레이아웃
│   └── page.tsx             # 홈페이지
├── components/              # React 컴포넌트
│   ├── forms/              # 폼 컴포넌트
│   ├── ui/                 # shadcn/ui 컴포넌트
│   ├── DeleteDialog.tsx    # 삭제 확인 다이얼로그
│   ├── Loading.tsx         # 로딩 스피너
│   └── nav.tsx             # 네비게이션 바
├── lib/                     # 유틸리티 및 API
│   ├── api/                # API 클라이언트 모듈
│   ├── types/              # TypeScript 타입 정의
│   ├── validators/         # Zod 스키마
│   └── utils.ts            # 유틸리티 함수
└── README.md
```

## 사용자 시나리오

### 1. 신규 생산 라인 설정
1. 라인 관리 페이지에서 새 라인 생성
2. 공정 관리 페이지에서 해당 라인에 공정 추가
3. PLC 관리 페이지에서 PLC 연결 정보 입력 및 테스트
4. 태그 관리 페이지에서 CSV로 태그 일괄 업로드
5. 폴링 그룹 생성 후 태그 선택 및 폴링 주기 설정
6. 폴링 그룹 시작

### 2. 시스템 모니터링
1. 대시보드 페이지에서 실시간 시스템 상태 확인
2. CPU/메모리/디스크 사용률 모니터링
3. PLC 연결 상태 확인
4. 로그 조회 페이지에서 오류 로그 분석

## 라이선스

MIT
