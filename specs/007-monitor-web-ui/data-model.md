# Data Model: 실시간 설비 모니터링 웹 UI

## 1. Equipment Status (설비 상태)

### Description
17개 설비 각각의 실시간 상태를 나타내는 클라이언트 측 데이터 모델입니다. WebSocket으로 수신한 데이터를 파싱하여 생성됩니다.

### Attributes

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| equipment_code | string | Yes | 설비 코드 (14자리) | 14-character process code format |
| equipment_name | string | Yes | 설비 이름 (예: "Upper 로봇 용접") | 1-100 characters |
| status | EquipmentStatusType | Yes | 설비 상태 | "running" \| "idle" \| "stopped" \| "error" \| "disconnected" |
| color | EquipmentColorType | Yes | 상태 색상 (UI 표시용) | "green" \| "yellow" \| "red" \| "purple" \| "gray" |
| tags | TagValues | Yes | 관련 태그 값 | - |
| last_updated | Date | Yes | 마지막 업데이트 시간 | ISO 8601 timestamp |

### Nested Object: TagValues

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| status_tag | number | Yes | 설비 상태 태그 값 (1=가동, 0=정지) |
| error_tag | number | Yes | 에러 태그 값 (1=이상, 0=정상) |
| connection | boolean | Yes | PLC 연결 상태 (true=정상, false=끊김) |

### State Transitions

```
Initial State: disconnected (Gray)
  ↓
connection: true → Check status_tag and error_tag
  ↓
error_tag === 1 → error (Purple)
  ↓
status === 'stopped' → stopped (Red)
  ↓
status === 'idle' → idle (Yellow)
  ↓
status === 'running' → running (Green)
```

### Relationships
- **1:N with Tag Values**: 각 설비는 여러 태그 값을 가질 수 있습니다 (status_tag, error_tag 등).
- **1:1 with Alarm Statistics**: 각 설비는 하나의 알람 통계 레코드를 가질 수 있습니다.

---

## 2. Alarm (알람)

### Description
Oracle DB에 저장된 설비 이상 알람 엔티티입니다. 백엔드 API를 통해 조회되며 프론트엔드에서 표시됩니다.

### Attributes

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| alarm_id | number | Yes | 알람 고유 ID (PK) | Positive integer |
| equipment_code | string | Yes | 설비 코드 (FK) | 14-character process code format |
| equipment_name | string | Yes | 설비 이름 (조인 결과) | 1-100 characters |
| alarm_type | AlarmType | Yes | 알람 유형 | "알람" \| "일반" |
| alarm_message | string | Yes | 알람 메시지 | 1-500 characters |
| occurred_at | Date | Yes | 발생 시간 | ISO 8601 timestamp |
| created_at | Date | Yes | 레코드 생성 시간 | ISO 8601 timestamp |

### Validation Rules
- `alarm_message`는 빈 문자열이 아니어야 합니다.
- `occurred_at`는 `created_at`보다 이전이거나 같아야 합니다.
- `equipment_code`는 SQLite의 `processes` 테이블에 존재하는 유효한 설비 코드여야 합니다.

### Relationships
- **N:1 with Equipment**: 여러 알람은 하나의 설비에 속합니다 (equipment_code FK).

---

## 3. Alarm Statistics (알람 통계)

### Description
설비별 알람 발생 건수를 집계한 데이터입니다. Oracle DB에서 SQL 집계 쿼리로 생성되며 프론트엔드에서 상단 그리드에 표시됩니다.

### Attributes

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| equipment_code | string | Yes | 설비 코드 | 14-character process code format |
| equipment_name | string | Yes | 설비 이름 | 1-100 characters |
| alarm_count | number | Yes | 알람 합계 건수 (alarm_type='알람') | Non-negative integer |
| general_count | number | Yes | 일반 건수 (alarm_type='일반') | Non-negative integer |

### Aggregation Rules
- 최근 24시간 동안 발생한 알람만 집계합니다.
- 알람이 없는 설비는 `alarm_count=0`, `general_count=0`으로 표시됩니다.

### Relationships
- **1:1 with Equipment**: 각 설비는 하나의 알람 통계 레코드를 가집니다.

---

## 4. WebSocket Message (WebSocket 메시지)

### Description
백엔드에서 프론트엔드로 전송되는 실시간 폴링 결과 메시지입니다.

### Attributes

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| type | string | Yes | 메시지 타입 | "equipment_status" \| "connection_status" |
| timestamp | Date | Yes | 메시지 생성 시간 | ISO 8601 timestamp |
| equipment | Equipment[] | Yes | 설비 상태 배열 (17개) | Array length must be 17 |

### Message Types

#### 1. equipment_status
실시간 설비 상태 업데이트 메시지 (1초 주기)

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

#### 2. connection_status
WebSocket 연결 상태 알림 메시지

```json
{
  "type": "connection_status",
  "timestamp": "2025-11-03T10:30:45.123Z",
  "status": "connected",
  "message": "WebSocket connected successfully"
}
```

---

## Entity Relationships Diagram

```
┌─────────────────────┐
│   Equipment (설비)   │
│                     │
│ - equipment_code PK │
│ - equipment_name    │
│ - status            │
│ - color             │
│ - tags              │
│ - last_updated      │
└──────────┬──────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────┐         ┌──────────────────────┐
│    Alarm (알람)      │         │ Alarm Statistics      │
│                     │         │ (알람 통계)            │
│ - alarm_id PK       │         │                       │
│ - equipment_code FK │◄────────┤ - equipment_code      │
│ - equipment_name    │   1:1   │ - equipment_name      │
│ - alarm_type        │         │ - alarm_count         │
│ - alarm_message     │         │ - general_count       │
│ - occurred_at       │         │                       │
│ - created_at        │         │                       │
└─────────────────────┘         └──────────────────────┘
           ▲
           │
           │ Source
           │
┌─────────────────────┐
│ WebSocket Message   │
│                     │
│ - type              │
│ - timestamp         │
│ - equipment[]       │
└─────────────────────┘
```

---

## Data Flow

### 1. Real-time Equipment Status (WebSocket)
```
PLC → Polling Engine → WebSocket Server → Frontend (1초 주기)
                                         ↓
                                    Equipment State Update
                                         ↓
                                    Color Mapping (getEquipmentColor)
                                         ↓
                                    UI Render (EquipmentStatusBox)
```

### 2. Alarm Statistics (HTTP Polling)
```
Oracle DB (ALARMS table) → Backend API (GET /api/alarms/statistics)
                                         ↓
                                    Frontend (10초 주기)
                                         ↓
                                    EquipmentGrid Component
                                         ↓
                                    UI Render (17 columns × 2 rows)
```

### 3. Recent Alarms (HTTP Polling)
```
Oracle DB (ALARMS table) → Backend API (GET /api/alarms/recent?limit=5)
                                         ↓
                                    Frontend (10초 주기)
                                         ↓
                                    AlarmList Component
                                         ↓
                                    UI Render (Recent 5 alarms)
```

---

## TypeScript Type Definitions

```typescript
// apps/monitor/lib/types/equipment.ts
export type EquipmentStatusType = 'running' | 'idle' | 'stopped' | 'error' | 'disconnected';
export type EquipmentColorType = 'green' | 'yellow' | 'red' | 'purple' | 'gray';

export interface TagValues {
  status_tag: number;
  error_tag: number;
  connection: boolean;
}

export interface Equipment {
  equipment_code: string;
  equipment_name: string;
  status: EquipmentStatusType;
  color: EquipmentColorType;
  tags: TagValues;
  last_updated: Date;
}

export interface WebSocketMessage {
  type: 'equipment_status' | 'connection_status';
  timestamp: Date;
  equipment: Equipment[];
}

// apps/monitor/lib/types/alarm.ts
export type AlarmType = '알람' | '일반';

export interface Alarm {
  alarm_id: number;
  equipment_code: string;
  equipment_name: string;
  alarm_type: AlarmType;
  alarm_message: string;
  occurred_at: Date;
  created_at: Date;
}

export interface AlarmStatistics {
  equipment_code: string;
  equipment_name: string;
  alarm_count: number;
  general_count: number;
}
```

---

## Summary

4개의 핵심 엔티티가 정의되었습니다:
1. **Equipment Status**: WebSocket으로 수신하는 실시간 설비 상태 (17개)
2. **Alarm**: Oracle DB에 저장된 설비 이상 알람 (최근 5개 표시)
3. **Alarm Statistics**: 설비별 알람 발생 건수 집계 (17개 설비 × 2개 행)
4. **WebSocket Message**: 백엔드와 프론트엔드 간 실시간 통신 메시지

다음 단계: Phase 1 (contracts/, quickstart.md 생성)
