# WebSocket Contract: 실시간 설비 모니터링

## Endpoint
```
ws://localhost:8000/ws/monitor
```

## Connection

### Client → Server (Connection Request)
```
WebSocket Upgrade Request
GET /ws/monitor HTTP/1.1
Host: localhost:8000
Upgrade: websocket
Connection: Upgrade
```

### Server → Client (Connection Response)
```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
```

---

## Message Types

### 1. equipment_status (Server → Client)

**Description**: 17개 설비의 실시간 상태 업데이트 (1초 주기)

**Message Format**:
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
    },
    {
      "equipment_code": "KRCWO12ELOA102",
      "equipment_name": "Lower 로봇 용접",
      "status": "idle",
      "tags": {
        "status_tag": 0,
        "error_tag": 0,
        "connection": true
      },
      "last_updated": "2025-11-03T10:30:45.000Z"
    }
  ]
}
```

**Field Definitions**:

| Field | Type | Required | Description | Possible Values |
|-------|------|----------|-------------|-----------------|
| type | string | Yes | 메시지 타입 | "equipment_status" |
| timestamp | string | Yes | 메시지 생성 시간 (ISO 8601) | - |
| equipment | array | Yes | 설비 상태 배열 | 17개 객체 |
| equipment[].equipment_code | string | Yes | 설비 코드 (14자리) | - |
| equipment[].equipment_name | string | Yes | 설비 이름 | - |
| equipment[].status | string | Yes | 설비 상태 | "running", "idle", "stopped", "error", "disconnected" |
| equipment[].tags | object | Yes | 태그 값 | - |
| equipment[].tags.status_tag | number | Yes | 상태 태그 값 | 1 (가동), 0 (정지) |
| equipment[].tags.error_tag | number | Yes | 에러 태그 값 | 1 (이상), 0 (정상) |
| equipment[].tags.connection | boolean | Yes | PLC 연결 상태 | true (정상), false (끊김) |
| equipment[].last_updated | string | Yes | 마지막 업데이트 시간 | ISO 8601 timestamp |

**Client Behavior**:
- 메시지를 수신하면 `equipment` 배열을 파싱하여 각 설비의 상태를 업데이트합니다.
- `getEquipmentColor()` 함수를 사용하여 상태를 색상으로 매핑합니다.
  - `!connection` → Gray (접속이상)
  - `error_tag === 1` → Purple (설비이상)
  - `status === 'stopped'` → Red (정지)
  - `status === 'idle'` → Yellow (비가동)
  - `status === 'running'` → Green (가동)
- UI 컴포넌트(`EquipmentStatusBox`)를 리렌더링합니다.

---

### 2. connection_status (Server → Client)

**Description**: WebSocket 연결 상태 알림 메시지

**Message Format**:
```json
{
  "type": "connection_status",
  "timestamp": "2025-11-03T10:30:45.123Z",
  "status": "connected",
  "message": "WebSocket connected successfully"
}
```

**Field Definitions**:

| Field | Type | Required | Description | Possible Values |
|-------|------|----------|-------------|-----------------|
| type | string | Yes | 메시지 타입 | "connection_status" |
| timestamp | string | Yes | 메시지 생성 시간 (ISO 8601) | - |
| status | string | Yes | 연결 상태 | "connected", "disconnected", "error" |
| message | string | Yes | 상태 메시지 | - |

**Client Behavior**:
- `status === 'connected'`: 연결 성공 상태로 설정
- `status === 'disconnected'`: 재연결 로직 시작 (3초 간격, 최대 5회)
- `status === 'error'`: 에러 메시지 표시

---

### 3. ping (Client → Server, Optional)

**Description**: Keep-alive ping 메시지 (선택사항)

**Message Format**:
```json
{
  "type": "ping",
  "timestamp": "2025-11-03T10:30:45.123Z"
}
```

**Server Behavior**:
- `pong` 메시지로 응답

---

### 4. pong (Server → Client, Optional)

**Description**: Ping에 대한 응답 메시지

**Message Format**:
```json
{
  "type": "pong",
  "timestamp": "2025-11-03T10:30:45.123Z"
}
```

---

## Error Handling

### Client-Side Errors

#### 1. Connection Failed (초기 연결 실패)
```typescript
ws.onerror = (error) => {
  console.error('WebSocket connection failed:', error);
  // 3초 후 재연결 시도
  setTimeout(() => connect(), 3000);
};
```

#### 2. Connection Closed (연결 끊김)
```typescript
ws.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason);
  setStatus('reconnecting');

  if (reconnectAttempts < maxReconnectAttempts) {
    reconnectAttempts++;
    setTimeout(() => connect(), 3000);
  } else {
    setStatus('failed');
    // 모든 설비를 Gray(접속이상)로 설정
    setEquipmentData(prev => prev.map(e => ({
      ...e,
      tags: { ...e.tags, connection: false }
    })));
  }
};
```

#### 3. Invalid Message Format (잘못된 메시지 형식)
```typescript
ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    if (data.type === 'equipment_status') {
      // 메시지 처리
    }
  } catch (error) {
    console.error('Invalid message format:', error);
    // 무시하고 다음 메시지 대기
  }
};
```

### Server-Side Errors

#### 1. Client Disconnected
- 서버는 클라이언트 연결 끊김을 감지하고 해당 WebSocket 객체를 정리합니다.

#### 2. Broadcast Failure
- 특정 클라이언트로의 브로드캐스트 실패 시 해당 클라이언트만 연결 목록에서 제거하고 다른 클라이언트는 정상 동작합니다.

---

## Performance Requirements

- **메시지 송신 주기**: 1초
- **메시지 크기**: 평균 5KB (17개 설비 × ~300 bytes)
- **지연 시간**: <100ms (서버 → 클라이언트)
- **동시 연결**: 최소 50개 클라이언트 지원
- **재연결 시간**: 최대 15초 (3초 × 5회)

---

## Security Considerations

- **Authentication**: 현재 구현에서는 인증 없음 (추후 JWT 토큰 추가 가능)
- **CORS**: localhost:3001 허용
- **Rate Limiting**: 클라이언트당 1초 1회 메시지 수신 (서버 측 제어)

---

## Example Client Implementation (TypeScript)

```typescript
// apps/monitor/lib/hooks/useWebSocket.ts
import { useEffect, useState, useRef } from 'react';
import { Equipment } from '@/lib/types/equipment';

type ConnectionStatus = 'connected' | 'reconnecting' | 'failed';

export const useWebSocket = (url: string) => {
  const [status, setStatus] = useState<ConnectionStatus>('reconnecting');
  const [equipmentData, setEquipmentData] = useState<Equipment[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000;

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'equipment_status') {
            setEquipmentData(data.equipment);
          } else if (data.type === 'connection_status') {
            console.log('Connection status:', data.status, data.message);
          }
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setStatus('reconnecting');

        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          setTimeout(connect, reconnectDelay);
        } else {
          setStatus('failed');
          setEquipmentData(prev => prev.map(e => ({
            ...e,
            tags: { ...e.tags, connection: false }
          })));
        }
      };
    };

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, [url]);

  return { status, equipmentData };
};
```

---

## Testing

### Manual Testing Script

```bash
# Install websocat (WebSocket client)
# Windows: scoop install websocat
# Linux: sudo apt install websocat

# Connect to WebSocket server
websocat ws://localhost:8000/ws/monitor

# Expected output (every 1 second):
# {"type":"equipment_status","timestamp":"2025-11-03T10:30:45.123Z","equipment":[...]}
```

### Integration Testing

```typescript
// backend/src/scripts/test_websocket_monitor.py
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/monitor"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server")

        # Receive 10 messages (10 seconds)
        for i in range(10):
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Message {i+1}: {data['type']}, Equipment count: {len(data['equipment'])}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
```
