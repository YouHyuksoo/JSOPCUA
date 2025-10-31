# 01. 프로젝트 개요

## 1.1 프로젝트 소개

### 프로젝트명
**JSScada - Mitsubishi Q Series PLC SCADA System**

### 목적
미쯔비시 Q 시리즈 PLC와 MC 3E ASCII 프로토콜을 사용하여 실시간 데이터 수집, 모니터링, 저장을 수행하는 SCADA(Supervisory Control and Data Acquisition) 시스템 개발

### 주요 목표
- **실시간 데이터 수집**: 다중 PLC로부터 3,491개 이상의 태그 데이터 실시간 폴링
- **핸드셰이크 폴링**: PLC 트리거 비트 기반 효율적인 데이터 수집
- **고성능 처리**: 멀티 스레드 아키텍처로 폴링과 DB 저장 분리하여 병목 현상 제거
- **웹 기반 관리**: Next.js 기반의 직관적인 관리 인터페이스
- **실시간 모니터링**: WebSocket 기반 실시간 데이터 시각화
- **기존 시스템 연동**: Oracle DB에 폴링 결과 저장하여 기존 분석 시스템과 통합

---

## 1.2 시스템 범위

### 포함 사항 (개발 대상)
1. **Python SCADA 백엔드**
   - MC 3E ASCII 프로토콜 통신 엔진
   - 멀티 스레드 폴링 엔진
   - 핸드셰이크 폴링 메커니즘
   - 연결 풀 관리
   - 비동기 DB Writer
   - WebSocket 서버
   - REST API 서버
   - 로깅 시스템 (4개 로그 파일: general, error, communication, performance)

2. **Next.js 관리 웹 애플리케이션**
   - 폴링 제어 (시작/중지/재시작)
   - 라인/공정/PLC/태그 관리
   - 폴링 그룹 설정
   - 시스템 상태 모니터링
   - 로그 조회
   - shadcn/ui 기반 UI

3. **Next.js 모니터링 웹 애플리케이션**
   - 실시간 태그 값 대시보드
   - 설비 상태 시각화
   - 알람 표시
   - 차트 및 그래프
   - WebSocket 기반 실시간 업데이트

4. **SQLite 로컬 데이터베이스**
   - SCADA 설정 정보 저장
   - 라인/공정/PLC/태그 마스터 데이터
   - 폴링 그룹 설정

### 제외 사항 (기존 시스템)
1. **Oracle 기준 정보 관리 시스템** (이미 존재)
   - 설비 마스터 데이터 관리
   - 공정 코드 관리

2. **Oracle 데이터 분석 시스템** (이미 존재)
   - 폴링 결과 조회
   - 통계 및 리포트
   - 데이터 분석

> **중요**: SCADA는 자체 SQLite DB에서 설정을 읽어 동작하며, Oracle DB에는 **폴링 결과만 저장**합니다.

---

## 1.3 시스템 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                        전체 시스템 구성                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │   기존 Oracle    │      │   기존 Oracle    │                │
│  │  기준정보 관리    │      │   데이터 분석     │                │
│  │     시스템       │◄─────┤      시스템      │                │
│  │   (범위 외)      │      │    (범위 외)     │                │
│  └──────┬───────────┘      └────────▲─────────┘                │
│         │                           │                          │
│         │                           │ 조회                      │
│         │ (별도 관리)         ┌──────┴──────┐                   │
│         │                    │             │                   │
│         │                    │  Oracle DB  │                   │
│         │                    │ (폴링 결과)  │                   │
│         │                    └──────▲──────┘                   │
│         │                           │                          │
│         │                           │ INSERT                   │
│         │                           │                          │
│  ┌──────┴───────────────────────────┴──────┐                   │
│  │                                         │                   │
│  │       Python SCADA 백엔드               │ ◄─────┐           │
│  │                                         │       │           │
│  │  ┌─────────────────────────────────┐   │       │           │
│  │  │    멀티 스레드 폴링 엔진         │   │       │           │
│  │  │  ┌────────┐  ┌────────┐         │   │       │           │
│  │  │  │Worker 1│  │Worker 2│  ...    │   │       │           │
│  │  │  └───┬────┘  └───┬────┘         │   │       │           │
│  │  │      │           │              │   │       │           │
│  │  │      └───────┬───┘              │   │       │           │
│  │  │              ▼                  │   │       │ WebSocket  │
│  │  │    ┌──────────────────┐        │   │       │           │
│  │  │    │ Thread-Safe      │        │   │       │           │
│  │  │    │   Data Buffer    │        │   │       │           │
│  │  │    │    (Queue)       │        │   │       │           │
│  │  │    └─────────┬────────┘        │   │       │           │
│  │  │              │                 │   │       │           │
│  │  └──────────────┼─────────────────┘   │       │           │
│  │                 ▼                     │       │           │
│  │      ┌─────────────────────┐         │       │           │
│  │      │   DB Writer Thread  │         │       │           │
│  │      │   (비동기 저장)      │         │       │           │
│  │      └─────────────────────┘         │       │           │
│  │                                       │       │           │
│  │  ┌─────────────────────────────────┐ │       │           │
│  │  │    Connection Pool              │ │       │           │
│  │  │  (PLC별 5개 재사용 연결)         │ │       │           │
│  │  └─────────────────────────────────┘ │       │           │
│  │                                       │       │           │
│  │  ┌─────────────────────────────────┐ │       │           │
│  │  │    SQLite Config DB             │ │       │           │
│  │  │  (설정 정보 로컬 저장)           │ │       │           │
│  │  └─────────────────────────────────┘ │       │           │
│  │                                       │       │           │
│  │  ┌─────────────────────────────────┐ │       │           │
│  │  │    File Logger (4 logs)         │ │       │           │
│  │  │  - scada.log                    │ │       │           │
│  │  │  - error.log                    │ │       │           │
│  │  │  - communication.log            │ │       │           │
│  │  │  - performance.log              │ │       │           │
│  │  └─────────────────────────────────┘ │       │           │
│  │                                       │       │           │
│  │            REST API                   │       │           │
│  │       (FastAPI / Uvicorn)             │       │           │
│  └───────────────┬───────────────────────┘       │           │
│                  │                               │           │
│                  │ HTTP                          │           │
│                  ▼                               │           │
│  ┌──────────────────────────────────────────────┴────────┐  │
│  │                                                        │  │
│  │              Next.js 관리 웹 (개발 대상)               │  │
│  │                                                        │  │
│  │  - 폴링 제어 (시작/중지/재시작)                         │  │
│  │  - 라인/공정/PLC/태그 관리                             │  │
│  │  - 폴링 그룹 설정                                      │  │
│  │  - 시스템 상태 모니터링                                │  │
│  │  - shadcn/ui 기반 UI                                  │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │           Next.js 모니터링 웹 (개발 대상)              │   │
│  │                                                       │   │
│  │  - 실시간 태그 값 대시보드                             │   │
│  │  - 설비 상태 시각화                                   │   │
│  │  - 알람 표시                                          │   │
│  │  - 차트 및 그래프                                     │   │
│  │  - WebSocket 실시간 업데이트                          │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│                             ▲                                │
│                             │ MC 3E ASCII Protocol           │
│                             │ (TCP/IP)                       │
│                             │                                │
│  ┌──────────────────────────┴───────────────────────────┐   │
│  │                                                       │   │
│  │         Mitsubishi Q Series PLC (다중)                │   │
│  │                                                       │   │
│  │  - PLC01, PLC02, ... PLC_N                           │   │
│  │  - 각 PLC당 다수의 태그 (총 3,491+ 태그)              │   │
│  │  - 핸드셰이크 트리거 비트 제공                         │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 1.4 핵심 기술 스택

### Python SCADA 백엔드
| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 언어 | Python | 3.11+ | 백엔드 개발 언어 |
| 웹 프레임워크 | FastAPI | 0.110+ | REST API 서버 |
| ASGI 서버 | Uvicorn | 0.27+ | 비동기 서버 |
| PLC 통신 | pymcprotocol | 1.0+ | MC 3E ASCII 프로토콜 |
| 로컬 DB | SQLite3 | 3.40+ | 설정 정보 저장 |
| Oracle DB | cx_Oracle | 8.3+ | 폴링 결과 저장 |
| WebSocket | websockets | 12.0+ | 실시간 데이터 스트리밍 |
| 비동기 처리 | threading, queue | 표준 라이브러리 | 멀티 스레드 폴링 |
| 로깅 | logging | 표준 라이브러리 | 파일 로깅 |
| 환경 변수 | python-dotenv | 1.0+ | 설정 관리 |

### Next.js 프론트엔드 (관리 + 모니터링)
| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 프레임워크 | Next.js | 14+ | React 기반 프론트엔드 |
| 언어 | TypeScript | 5.3+ | 타입 안전성 |
| UI 라이브러리 | shadcn/ui | latest | UI 컴포넌트 |
| 스타일링 | Tailwind CSS | 3.4+ | CSS 프레임워크 |
| 상태 관리 | Zustand | 4.5+ | 클라이언트 상태 관리 |
| HTTP 클라이언트 | Axios | 1.6+ | REST API 호출 |
| WebSocket | Socket.io-client | 4.7+ | 실시간 데이터 수신 |
| 차트 | Recharts | 2.10+ | 데이터 시각화 |
| 폼 관리 | React Hook Form | 7.50+ | 폼 유효성 검사 |
| 테이블 | TanStack Table | 8.12+ | 데이터 테이블 |

### 데이터베이스
| 구분 | 기술 | 용도 |
|------|------|------|
| SQLite | 3.40+ | SCADA 로컬 설정 저장 (라인/공정/PLC/태그/폴링그룹) |
| Oracle DB | 19c+ | 폴링 결과 저장 (기존 시스템 연동) |

### 통신 프로토콜
| 프로토콜 | 용도 |
|---------|------|
| MC 3E ASCII | PLC 데이터 읽기/쓰기 (Read/Write) |
| TCP/IP | PLC 연결 (기본 포트: 5000) |
| HTTP/REST | 관리 웹 ↔ 백엔드 API 통신 |
| WebSocket | 백엔드 → 모니터링 웹 실시간 데이터 푸시 |

### 개발 도구
| 도구 | 용도 |
|------|------|
| Git | 버전 관리 |
| VS Code | 통합 개발 환경 |
| Postman | API 테스트 |
| MX Component | PLC 시뮬레이터 (테스트 환경) |

---

## 1.5 주요 기능 요구사항

### 1.5.1 폴링 엔진 기능

#### 폴링 모드
1. **고정 간격 폴링 (FIXED)**
   - 설정된 간격(ms)마다 자동으로 태그 데이터 읽기
   - 예: 1000ms마다 온도, 압력 등 연속 데이터 수집

2. **핸드셰이크 폴링 (HANDSHAKE)**
   - PLC가 트리거 비트를 1로 설정하면 데이터 읽기
   - 데이터 읽기 후 자동으로 트리거 비트를 0으로 리셋
   - 예: 작업 완료 시그널, 이벤트 기반 데이터 수집
   - 각 폴링 그룹마다 다른 트리거 비트 매핑 가능

#### 폴링 그룹
- **폴링 그룹**: 동일한 폴링 설정을 공유하는 태그들의 논리적 그룹
- 각 폴링 그룹은 독립된 워커 스레드에서 실행
- 폴링 그룹별 설정:
  - 폴링 모드 (FIXED / HANDSHAKE)
  - 폴링 간격 (ms)
  - 트리거 비트 주소 (HANDSHAKE 모드인 경우)
  - 트리거 비트 오프셋
  - 자동 리셋 여부
  - 우선순위

#### 멀티 스레딩
- **1개 폴링 그룹 = 1개 워커 스레드**
- 각 워커 스레드는 독립적으로 PLC 폴링 수행
- 배치 읽기: 하나의 폴링 그룹 내 여러 태그를 한 번의 MC 프로토콜 요청으로 읽기
- Connection Pool: PLC당 5개의 재사용 가능한 연결 유지

#### 비동기 DB 저장
- 폴링 스레드와 DB Writer 스레드 **완전 분리**
- Thread-Safe Queue 버퍼 사용 (최대 10,000 데이터 포인트)
- 폴링 스레드: 데이터를 큐에 푸시 (0.1ms, 빠름)
- DB Writer 스레드: 큐에서 배치로 데이터를 가져와 Oracle에 INSERT (500ms, 느림)
- 폴링 간격이 DB 저장 시간에 영향받지 않음

### 1.5.2 수동 폴링 제어
- 백엔드 시작 시 폴링 엔진은 **STOPPED 상태**
- 관리 웹에서 수동으로 폴링 시작/중지/재시작
- 상태: STOPPED, STARTING, RUNNING, STOPPING, ERROR

### 1.5.3 연결 관리
- **Connection Pool**: PLC당 5개의 TCP 연결 사전 생성 및 재사용
- 연결 실패 시 자동 재시도 (최대 3회, 5초 간격)
- 연결 상태 모니터링 및 관리 웹에서 실시간 표시

### 1.5.4 로깅
4개의 독립적인 로그 파일 (일별 로테이션, 30일 보관):

1. **scada.log**: 일반 애플리케이션 로그
   - 백엔드 시작/종료
   - 폴링 시작/중지
   - 설정 로드

2. **error.log**: 오류 로그
   - 예외 스택 트레이스
   - 시스템 오류

3. **communication.log**: PLC 통신 로그
   - PLC 연결/단절
   - 읽기/쓰기 요청
   - 통신 타임아웃

4. **performance.log**: 성능 메트릭
   - 폴링 소요 시간
   - DB 저장 소요 시간
   - 큐 크기

### 1.5.5 데이터 스케일링
- 원시 PLC 값에 스케일 팩터 적용
- 예: PLC에서 읽은 값 1234 × 스케일 0.1 = 123.4
- 단위 변환 자동 처리

### 1.5.6 알람 평가
- SCADA 내부에서 태그 값 기반 알람 조건 평가
- 알람 발생 시 Oracle DB에 알람 레코드 INSERT
- 알람 시작/종료 시간 추적

### 1.5.7 실시간 모니터링
- WebSocket을 통한 실시간 데이터 스트리밍
- 태그 값 변경 시 즉시 모니터링 웹으로 브로드캐스트
- 구독 기반: 클라이언트가 관심 있는 태그만 구독 가능

---

## 1.6 비기능 요구사항

### 성능
- **폴링 간격**: 최소 100ms ~ 최대 60,000ms (1분)
- **응답 시간**: 태그 읽기 요청 후 500ms 이내 응답
- **동시 처리**: 최대 100개 폴링 그룹 동시 실행
- **태그 용량**: 10,000개 이상 태그 지원
- **WebSocket 동시 연결**: 최대 50개 클라이언트

### 가용성
- **24/7 운영**: 중단 없이 연속 실행
- **자동 복구**: PLC 연결 실패 시 자동 재연결
- **오류 격리**: 한 PLC의 오류가 다른 PLC 폴링에 영향 없음

### 보안
- **인증**: 관리 웹 접근 시 로그인 필요 (향후 확장)
- **권한**: 폴링 제어는 관리자만 가능
- **통신 보안**: PLC 통신은 내부 네트워크에서만 허용

### 유지보수성
- **로그**: 상세한 파일 로그로 문제 추적 가능
- **설정**: 웹 UI를 통한 쉬운 설정 변경
- **모니터링**: 실시간 시스템 상태 확인

### 확장성
- **PLC 추가**: 새 PLC 추가 시 웹 UI에서 간단히 등록
- **태그 추가**: 대량 태그 일괄 등록 지원 (CSV 임포트)
- **폴링 그룹**: 필요에 따라 폴링 그룹 추가/수정

---

## 1.7 프로젝트 구조

```
JSScada/
├── backend/                    # Python SCADA 백엔드
│   ├── src/
│   │   ├── main.py            # 진입점
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── config_loader.py    # SQLite 설정 로더
│   │   │   └── settings.py          # 환경 변수 설정
│   │   ├── polling/
│   │   │   ├── __init__.py
│   │   │   ├── polling_engine.py    # 폴링 엔진 메인
│   │   │   ├── polling_worker.py    # 워커 스레드
│   │   │   ├── connection_pool.py   # PLC 연결 풀
│   │   │   └── data_buffer.py       # Thread-Safe 큐
│   │   ├── protocol/
│   │   │   ├── __init__.py
│   │   │   ├── mc_protocol.py       # MC 3E ASCII 래퍼
│   │   │   └── plc_client.py        # PLC 클라이언트
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── sqlite_manager.py    # SQLite 관리
│   │   │   ├── oracle_writer.py     # Oracle DB Writer 스레드
│   │   │   └── models.py            # 데이터 모델
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── app.py               # FastAPI 앱
│   │   │   ├── routes/
│   │   │   │   ├── polling_control.py   # 폴링 제어 API
│   │   │   │   ├── tags.py              # 태그 관리 API
│   │   │   │   ├── plc.py               # PLC 관리 API
│   │   │   │   └── system.py            # 시스템 API
│   │   │   └── websocket/
│   │   │       └── realtime.py          # WebSocket 서버
│   │   ├── logger/
│   │   │   ├── __init__.py
│   │   │   └── scada_logger.py      # 로깅 시스템
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── config/
│   │   └── scada.db               # SQLite 로컬 DB
│   ├── logs/                      # 로그 파일 디렉토리
│   │   ├── scada.log
│   │   ├── error.log
│   │   ├── communication.log
│   │   └── performance.log
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── frontend-admin/               # Next.js 관리 웹
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx              # 대시보드
│   │   ├── polling-control/
│   │   │   └── page.tsx          # 폴링 제어
│   │   ├── lines/
│   │   │   └── page.tsx          # 라인 관리
│   │   ├── processes/
│   │   │   └── page.tsx          # 공정 관리
│   │   ├── plcs/
│   │   │   └── page.tsx          # PLC 관리
│   │   ├── tags/
│   │   │   └── page.tsx          # 태그 관리
│   │   ├── polling-groups/
│   │   │   └── page.tsx          # 폴링 그룹 관리
│   │   ├── logs/
│   │   │   └── page.tsx          # 로그 조회
│   │   └── settings/
│   │       └── page.tsx          # 시스템 설정
│   ├── components/
│   │   ├── ui/                   # shadcn/ui 컴포넌트
│   │   ├── polling-status-badge.tsx
│   │   ├── plc-connection-indicator.tsx
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts                # API 클라이언트
│   │   └── utils.ts
│   ├── stores/
│   │   └── polling-store.ts      # Zustand 상태 관리
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── frontend-monitor/             # Next.js 모니터링 웹
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx              # 실시간 대시보드
│   │   ├── equipment/
│   │   │   └── [code]/page.tsx  # 설비별 모니터링
│   │   ├── alarms/
│   │   │   └── page.tsx          # 알람 모니터링
│   │   └── trends/
│   │       └── page.tsx          # 트렌드 차트
│   ├── components/
│   │   ├── ui/
│   │   ├── realtime-tag-card.tsx
│   │   ├── alarm-list.tsx
│   │   ├── trend-chart.tsx
│   │   └── ...
│   ├── lib/
│   │   ├── websocket.ts          # WebSocket 클라이언트
│   │   └── utils.ts
│   ├── stores/
│   │   └── realtime-store.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── docs/                         # 프로젝트 문서
│   ├── 01-PROJECT-OVERVIEW.md    # 이 문서
│   ├── 02-SYSTEM-ARCHITECTURE.md
│   ├── 03-DATABASE-SCHEMA.md
│   ├── 04-PYTHON-BACKEND-SPEC.md
│   ├── 05-NEXTJS-ADMIN-SPEC.md
│   └── 06-NEXTJS-MONITORING-SPEC.md
│
└── README.md                     # 프로젝트 루트 README
```

---

## 1.8 외부 시스템 연동

### Oracle 데이터베이스 (폴링 결과 저장)

SCADA는 폴링한 데이터를 기존 Oracle DB의 **2개 테이블**에 저장합니다.

#### 테이블 1: 알람/상태 데이터 (22 컬럼)
```sql
-- 테이블명: [사용자 제공 필요]
MACHINE_DIV          VARCHAR2(20)      -- 'PLC' 고정
MACHINE_CODE         VARCHAR2(20)      -- 설비코드 (KRCWO12ELOA101)
MACHINE_STATUS_DIV   VARCHAR2(20)      -- 'ALARM', 'QC' 등
MACHINE_STATUS_VALUE VARCHAR2(20)      -- 상태값
MACHINE_MESSAGE      VARCHAR2(1000)    -- 태그명 또는 메시지
MACHINE_DATETIME     VARCHAR2(30)      -- YYYYMMDDHH24MISS
COMMENTS             VARCHAR2(1000)
ENTER_DATE           DATE
ENTER_BY             VARCHAR2(20)      -- 'SCADA' 고정
ORGANIZATION_ID      NUMBER
PLC_CODE             VARCHAR2(20)      -- PLC 코드
TAG_ADDRESS          VARCHAR2(20)      -- TAG 주소 (W150, M100 등)
ALARM_START_DATETIME DATE
ALARM_END_DATETIME   DATE
ALARM_TIME_TERM      NUMBER
PLC_TIMESTAMP        TIMESTAMP(6)
TAG_TYPE             VARCHAR2(20)
IS_FIXED             VARCHAR2(20)
SCADA_ID             NUMBER
EQP_STATE            VARCHAR2(20)
CONTROL_STATE        VARCHAR2(20)      -- '수동', '자동'
TAG_ADDRESS_REASON   VARCHAR2(20)
```

**저장 시점**: 알람 조건 만족 시 또는 상태 변경 시

#### 테이블 2: 비트 폴링 결과 (10 컬럼)
```sql
-- 테이블명: [사용자 제공 필요]
PLC_CODE         VARCHAR2(20)      -- PLC 코드
MACHINE_CODE     VARCHAR2(20)      -- 설비코드
TAG_ADDRESS      VARCHAR2(20)      -- TAG 주소
TAG_VALUE        VARCHAR2(20)      -- 폴링 값 (스케일 적용 후)
MACHINE_DATETIME VARCHAR2(30)      -- YYYYMMDDHH24MISS
PLC_TIMESTAMP    TIMESTAMP(6)      -- 폴링 시각
COMMENTS         VARCHAR2(1000)
ENTER_DATE       DATE
ENTER_BY         VARCHAR2(20)      -- 'SCADA' 고정
ORGANIZATION_ID  NUMBER
```

**저장 시점**: 모든 폴링 결과 (FIXED 모드 또는 HANDSHAKE 모드)

### 데이터 흐름
```
PLC → Python SCADA 백엔드 (폴링) → Thread-Safe Buffer → DB Writer → Oracle DB
                                 ↘ WebSocket → 모니터링 웹
```

---

## 1.9 참고 문서

### PLC 메모리 맵
- 파일: `D:\Document\고객별프로젝트\엘지DX진행\220624_오성사 Tub EHM_메모리 맵(PLC_01).xlsx`
- 내용: PLC01의 비트 및 워드 주소 매핑, 트리거 비트 정의

### 태그 마스터 리스트
- 파일: `D:\Document\고객별프로젝트\엘지DX진행\태그리스트.xlsx`
- 내용: 3,491개 태그의 상세 정보 (TAG_ID, TAG_ADDRESS, TAG_NAME, SCALE, UNIT, MACHINE_CODE)

### 설비 코드 체계
- 파일: `D:\Document\고객별프로젝트\엘지DX진행\식세기 TUB 가공라인 34개 공정 ID 부여_220609 오성사 지성 공유.xlsx`
- 내용: 34개 공정의 14자리 설비 코드 (예: KRCWO12ELOA101)
- 코드 구조: `{국가(2)}{지역(2)}{회사(1)}{제품(2)}{타입(1)}{설비(3)}{시퀀스(3)}`

---

## 1.10 용어 정의

| 용어 | 정의 |
|------|------|
| **SCADA** | Supervisory Control and Data Acquisition - 산업 제어 시스템의 데이터 수집 및 모니터링 시스템 |
| **PLC** | Programmable Logic Controller - 프로그래머블 로직 컨트롤러 |
| **MC 3E ASCII** | 미쯔비시 MC 프로토콜 3E 프레임 ASCII 포맷 |
| **태그 (Tag)** | PLC 메모리 주소와 연결된 데이터 포인트 (예: W150, M100) |
| **폴링 (Polling)** | 주기적으로 PLC에서 데이터를 읽어오는 동작 |
| **폴링 그룹** | 동일한 폴링 설정을 공유하는 태그들의 논리적 그룹 |
| **핸드셰이크 폴링** | PLC 트리거 비트 기반으로 데이터를 읽는 폴링 방식 |
| **트리거 비트** | PLC가 데이터 준비 완료를 알리는 비트 (예: B0110+0) |
| **배치 읽기** | 여러 태그를 한 번의 MC 프로토콜 요청으로 읽는 방식 |
| **Connection Pool** | 재사용 가능한 PLC TCP 연결의 집합 |
| **스케일 팩터** | 원시 PLC 값을 실제 공학 단위로 변환하는 계수 |
| **워커 스레드** | 독립적으로 폴링을 수행하는 스레드 |
| **DB Writer** | 버퍼에서 데이터를 가져와 Oracle DB에 저장하는 스레드 |

---

## 1.11 개발 일정 (예상)

| 단계 | 작업 내용 | 예상 기간 |
|------|----------|----------|
| 1단계 | 프로젝트 설계 및 문서 작성 | 1주 |
| 2단계 | Python 백엔드 기본 구조 개발 (MC 프로토콜, 연결 풀) | 2주 |
| 3단계 | 폴링 엔진 개발 (멀티 스레드, 핸드셰이크) | 2주 |
| 4단계 | DB Writer 및 Oracle 연동 개발 | 1주 |
| 5단계 | REST API 및 WebSocket 서버 개발 | 1주 |
| 6단계 | Next.js 관리 웹 개발 | 2주 |
| 7단계 | Next.js 모니터링 웹 개발 | 2주 |
| 8단계 | 통합 테스트 및 버그 수정 | 2주 |
| 9단계 | 실제 환경 배포 및 튜닝 | 1주 |
| **총 예상 기간** | | **14주 (약 3.5개월)** |

---

## 1.12 리스크 및 대응 방안

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|----------|
| PLC 통신 불안정 | 높음 | Connection Pool, 자동 재연결, 통신 로그 상세 기록 |
| 폴링 성능 저하 | 중간 | 멀티 스레드, 배치 읽기, 성능 로그 모니터링 |
| DB 저장 지연 | 중간 | 비동기 DB Writer, Thread-Safe 버퍼, 배치 INSERT |
| 메모리 부족 | 낮음 | 버퍼 크기 제한 (10,000), 데이터 보관 기간 설정 |
| 태그 수 증가 | 중간 | 폴링 그룹 분할, 배치 읽기 최적화 |
| Oracle 연결 실패 | 중간 | 재시도 로직, 로컬 SQLite에 임시 저장 (향후 확장) |

---

## 1.13 제약 사항

1. **PLC 통신**
   - MC 3E ASCII 프로토콜만 지원 (Binary 포맷 미지원)
   - TCP/IP 연결만 지원 (UDP 미지원)

2. **데이터베이스**
   - Oracle DB는 폴링 결과 저장 전용 (설정 읽기 불가)
   - SQLite는 로컬 파일 DB (원격 접근 불가)

3. **실시간 모니터링**
   - WebSocket 클라이언트 최대 50개 동시 연결
   - 네트워크 대역폭에 따라 제한될 수 있음

4. **폴링 간격**
   - 최소 폴링 간격 100ms (더 짧으면 PLC 부하 증가)
   - 태그 수가 많을 경우 배치 읽기 시간 고려 필요

---

## 1.14 향후 확장 계획

1. **보안 강화**
   - 사용자 인증 (JWT)
   - 역할 기반 접근 제어 (RBAC)
   - HTTPS/WSS 지원

2. **고가용성**
   - 백엔드 이중화 (Active-Standby)
   - Oracle DB 장애 시 로컬 SQLite 임시 저장

3. **알람 고도화**
   - 알람 우선순위
   - 알람 필터링
   - 알람 통지 (이메일, SMS)

4. **데이터 분석**
   - 실시간 통계 (평균, 최소, 최대)
   - 히스토리 트렌드 비교

5. **PLC 제어**
   - 태그 쓰기 (Write) 기능
   - 원격 제어 명령

---

## 부록 A: 14자리 설비 코드 체계

```
KRCWO12ELOA101
│││││││││││││└─ 시퀀스 (3자리): 001~999
││││││││└└└──── 설비 타입 (3자리): LOA, WEM, MOM, DRY 등
│││││││└──────── 타입 구분 (1자리): E (전기), M (기계)
││││└└───────── 제품 코드 (2자리): 12 (TUB)
│││└──────────── 회사 코드 (1자리): O (오성사)
└└───────────── 지역 코드 (2자리): CW (창원)
 └────────────── 국가 코드 (2자리): KR (한국)
```

**설비 타입 예시**:
- LOA: Loader (로더)
- WEM: Welding Machine (용접기)
- MOM: Material Handling (자재 운반)
- DRY: Dryer (건조기)
- PRS: Press (프레스)

---

## 부록 B: 참고 자료

1. **Mitsubishi MC 프로토콜 매뉴얼**
   - MC Protocol Reference Manual
   - MELSEC Communication Protocol Reference Manual

2. **pymcprotocol 라이브러리**
   - GitHub: https://github.com/ftkghost/pymcprotocol
   - 문서: https://pymcprotocol.readthedocs.io/

3. **FastAPI 공식 문서**
   - https://fastapi.tiangolo.com/

4. **Next.js 공식 문서**
   - https://nextjs.org/docs

5. **shadcn/ui 컴포넌트**
   - https://ui.shadcn.com/

---

## 문서 이력

| 버전 | 일자 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | 2025-10-30 | Claude | 최초 작성 |

---

**문서 작성자**: Claude
**문서 승인자**: [사용자명]
**다음 문서**: [02-SYSTEM-ARCHITECTURE.md](./02-SYSTEM-ARCHITECTURE.md)
