# Research: 실시간 설비 모니터링 웹 UI

## 1. Oracle DB 알람 테이블 스키마

### Decision
Oracle DB에 `ALARMS` 테이블이 이미 존재하거나 Feature 4에서 생성되었다고 가정합니다. 알람 데이터는 PLC 태그 값에서 이상 감지 시 Feature 4의 Oracle Writer가 저장합니다.

### Rationale
- Feature 4 (Buffer & Oracle Writer)에서 PLC 태그 값을 Oracle DB에 저장하는 기능이 구현되었습니다.
- 알람은 특정 태그 값이 임계값을 초과하거나 이상 상태일 때 발생하므로, 알람 감지 로직은 폴링 엔진 또는 Oracle Writer에서 처리됩니다.
- Monitor UI는 Oracle DB에서 알람 데이터를 **조회만** 수행합니다.

### Assumed Schema
```sql
CREATE TABLE ALARMS (
    ALARM_ID NUMBER PRIMARY KEY,
    EQUIPMENT_CODE VARCHAR2(50) NOT NULL,  -- 설비 코드 (17개 설비 중 하나)
    ALARM_TYPE VARCHAR2(20) NOT NULL,      -- '알람' 또는 '일반'
    ALARM_MESSAGE VARCHAR2(500),           -- 알람 메시지
    OCCURRED_AT TIMESTAMP NOT NULL,        -- 발생 시간
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IDX_ALARMS_OCCURRED ON ALARMS(OCCURRED_AT DESC);
CREATE INDEX IDX_ALARMS_EQUIPMENT ON ALARMS(EQUIPMENT_CODE, OCCURRED_AT DESC);
```

### Alternatives Considered
- **별도 알람 테이블 생성 없이 TAG_VALUES 테이블에서 조건부 조회**: 알람 데이터를 명시적으로 분리하지 않으면 쿼리 성능이 저하되고 알람 통계 집계가 복잡해집니다.
- **Redis 캐싱**: 10초 주기 갱신이므로 Redis 캐싱의 이점이 크지 않으며, Oracle DB 직접 조회로도 성능 목표(<2초)를 달성할 수 있습니다.

---

## 2. WebSocket 메시지 구조

### Decision
WebSocket 메시지는 JSON 형식으로 설비별 태그 값을 포함하며, 클라이언트는 이를 파싱하여 설비 상태를 5가지 색상으로 매핑합니다.

### Rationale
- Feature 3 (폴링 엔진)에서 WebSocket 서버(`/ws/polling`)가 이미 구현되어 폴링 결과를 전송합니다.
- Monitor UI는 기존 WebSocket 서버를 확장하거나 별도 엔드포인트(`/ws/monitor`)를 추가하여 설비 상태 데이터를 수신합니다.
- 설비 상태 판단 로직(5가지 색상 매핑)은 프론트엔드에서 처리하여 백엔드 부하를 줄입니다.

### Message Format
```json
{
  "type": "equipment_status",
  "timestamp": "2025-11-03T10:30:45.123Z",
  "equipment": [
    {
      "equipment_code": "KRCWO12ELOA101",
      "equipment_name": "Upper 로봇 용접",
      "status": "running",
      "tags": {
        "status_tag": 1,
        "error_tag": 0,
        "connection": true
      },
      "last_updated": "2025-11-03T10:30:45.000Z"
    }
  ]
}
```

### Status Mapping Logic (Frontend)
```typescript
function getEquipmentColor(equipment: Equipment): string {
  if (!equipment.tags.connection) return 'gray';
  if (equipment.tags.error_tag === 1) return 'purple';
  if (equipment.status === 'stopped') return 'red';
  if (equipment.status === 'idle') return 'yellow';
  if (equipment.status === 'running') return 'green';
  return 'gray';
}
```

### Alternatives Considered
- **백엔드에서 색상 정보 전송**: 프론트엔드가 색상 매핑 로직을 처리하면 유연성이 높아지고, 추후 색상 기준 변경 시 프론트엔드만 수정하면 됩니다.
- **Server-Sent Events (SSE)**: WebSocket이 양방향 통신을 지원하므로 추후 클라이언트에서 백엔드로 제어 명령을 보낼 수 있는 확장성을 제공합니다.

---

## 3. Next.js 14 App Router 구조

### Decision
Next.js 14 App Router를 사용하며, `apps/monitor/app/page.tsx`에 모든 UI 컴포넌트를 배치합니다. shadcn/ui 컴포넌트 라이브러리를 사용하여 Feature 6 (Admin UI)와 일관된 디자인을 유지합니다.

### Rationale
- Feature 6에서 이미 shadcn/ui 설정이 완료되었으므로 동일한 컴포넌트를 재사용할 수 있습니다.
- 모니터링 UI는 단일 페이지 대시보드이므로 복잡한 라우팅이 필요하지 않습니다.
- Server Components와 Client Components를 혼합하여 초기 로드 성능을 최적화합니다.

### Component Architecture
```
apps/monitor/app/page.tsx (Server Component)
├── EquipmentGrid (Client Component)
├── EquipmentLayout (Client Component)
│   └── EquipmentStatusBox × 17
└── AlarmList (Client Component)
```

### Alternatives Considered
- **Pages Router**: App Router가 더 나은 성능과 서버 컴포넌트 지원을 제공하며, Feature 6와의 일관성을 유지합니다.
- **별도 라우팅 페이지**: 모니터링 UI는 단일 대시보드이므로 별도 라우팅이 불필요합니다.

---

## 4. WebSocket 재연결 전략

### Decision
WebSocket 연결이 끊어지면 3초 간격으로 최대 5회 자동 재연결을 시도하며, 모두 실패 시 사용자에게 경고 메시지를 표시하고 모든 설비 상태를 Gray(접속이상)로 변경합니다.

### Rationale
- 네트워크 일시적 장애나 백엔드 재시작 시 자동 복구를 통해 운영자의 수동 개입을 최소화합니다.
- 5회 재시도는 총 15초의 재연결 시도 시간을 제공하며, 이는 대부분의 일시적 장애를 복구하기에 충분합니다.
- 재연결 실패 시 명확한 시각적 피드백(경고 메시지 + 모든 설비 Gray)을 제공합니다.

### Alternatives Considered
- **무한 재연결**: 무한 재연결은 백엔드 장애 시 불필요한 트래픽을 발생시키고 사용자에게 문제 상황을 명확히 전달하지 못합니다.
- **즉시 재연결 (0초 간격)**: 0초 간격 재연결은 백엔드에 과부하를 유발할 수 있습니다.

---

## 5. Oracle DB API 엔드포인트 설계

### Decision
백엔드에 2개의 REST API 엔드포인트를 추가합니다:
1. `GET /api/alarms/statistics` - 17개 설비별 알람 통계
2. `GET /api/alarms/recent` - 최근 5개 알람 목록

### Rationale
- Oracle DB 쿼리 로직을 백엔드에서 처리하여 프론트엔드의 복잡도를 줄이고 보안을 강화합니다.
- FastAPI를 사용하여 Pydantic 모델 기반 응답 검증 및 자동 문서 생성을 지원합니다.
- 10초 주기 갱신이므로 캐싱 없이 실시간 조회로 충분합니다.

### API Contracts

#### 1. GET /api/alarms/statistics
**Response 200 OK**:
```json
{
  "equipment": [
    {
      "equipment_code": "KRCWO12ELOA101",
      "equipment_name": "Upper 로봇 용접",
      "alarm_count": 5,
      "general_count": 3
    }
  ],
  "last_updated": "2025-11-03T10:30:45.123Z"
}
```

#### 2. GET /api/alarms/recent?limit=5
**Response 200 OK**:
```json
{
  "alarms": [
    {
      "alarm_id": 12345,
      "equipment_name": "Upper 로봇 용접",
      "alarm_message": "온도 과열 경고",
      "occurred_at": "2025-11-03T10:28:15.000Z"
    }
  ]
}
```

### Alternatives Considered
- **GraphQL**: REST API가 요구사항을 충분히 만족하며, 기존 FastAPI 구조와 일관성을 유지합니다.
- **WebSocket으로 알람 데이터 전송**: 10초 주기 HTTP 폴링이 더 간단하고 안정적이며, WebSocket 연결 실패 시에도 알람 데이터를 조회할 수 있습니다.

---

## 6. 반응형 디자인 전략

### Decision
Tailwind CSS 반응형 유틸리티를 사용하여 1280px를 기준으로 3단 레이아웃과 세로 스택 레이아웃을 전환합니다.

### Rationale
- 1280px 이상 해상도는 대부분의 모니터링 환경(데스크톱, 대형 모니터)을 커버합니다.
- Tailwind CSS의 반응형 유틸리티를 활용하여 간단하게 구현할 수 있습니다.

### Layout Breakpoints
```tsx
<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
  <div className="lg:col-span-3">
    <EquipmentGrid />
  </div>
  <div className="lg:col-span-2">
    <EquipmentLayout />
  </div>
  <div className="lg:col-span-1">
    <AlarmList />
  </div>
</div>
```

### Alternatives Considered
- **고정 레이아웃 (반응형 없음)**: 모바일 접근 시나리오를 고려하여 반응형 디자인을 적용합니다.
- **CSS Grid Auto-Fit**: Tailwind CSS가 더 명시적이고 유지보수가 쉽습니다.

---

## Summary

모든 NEEDS CLARIFICATION이 해결되었습니다:
1. ✅ Oracle DB 알람 테이블 스키마 정의
2. ✅ WebSocket 메시지 구조 및 상태 매핑 로직
3. ✅ Next.js 14 App Router 컴포넌트 아키텍처
4. ✅ WebSocket 재연결 전략 (3초 간격, 5회 시도)
5. ✅ Oracle DB API 엔드포인트 설계 (2개 REST API)
6. ✅ 반응형 디자인 전략 (1280px 기준)

다음 단계: Phase 1 (data-model.md, contracts/, quickstart.md 생성)
