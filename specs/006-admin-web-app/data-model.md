# Data Model: Next.js Admin Web Application

**Feature**: 006-admin-web-app | **Date**: 2025-11-02

## TypeScript Interfaces (Frontend)

### Line
```typescript
interface Line {
  id: number;
  name: string;
  code: string;
  created_at: string;
  updated_at: string;
}

interface CreateLineRequest {
  name: string;
  code: string;
}
```

### Process
```typescript
interface Process {
  id: number;
  name: string;
  code: string;
  line_id: number;
  line_name?: string; // Joined from Line
  created_at: string;
  updated_at: string;
}

interface CreateProcessRequest {
  name: string;
  code: string;
  line_id: number;
}
```

### PLC
```typescript
interface PLC {
  id: number;
  name: string;
  ip_address: string;
  port: number;
  plc_type: string; // "MC-3E"
  protocol: string; // "ASCII" | "Binary"
  process_id: number;
  process_name?: string;
  is_connected: boolean;
  created_at: string;
  updated_at: string;
}

interface CreatePLCRequest {
  name: string;
  ip_address: string;
  port: number;
  plc_type: string;
  protocol: string;
  process_id: number;
}

interface PLCTestResponse {
  success: boolean;
  message: string;
  response_time_ms?: number;
}
```

### Tag
```typescript
interface Tag {
  id: number;
  name: string;
  device_address: string; // "D100"
  data_type: string; // "INT" | "FLOAT" | "BOOL"
  polling_interval: number; // seconds
  unit?: string;
  description?: string;
  plc_id: number;
  plc_name?: string;
  created_at: string;
  updated_at: string;
}

interface CreateTagRequest {
  name: string;
  device_address: string;
  data_type: string;
  polling_interval: number;
  unit?: string;
  description?: string;
  plc_id: number;
}

interface CSVUploadResponse {
  success_count: number;
  fail_count: number;
  errors: Array<{
    row: number;
    field: string;
    message: string;
  }>;
}
```

### Polling Group
```typescript
interface PollingGroup {
  id: number;
  name: string;
  polling_interval: number; // 0.5-60 seconds
  is_active: boolean;
  status: "stopped" | "running" | "error";
  last_poll_time?: string;
  success_rate?: number; // 0-100
  tag_count: number;
  created_at: string;
  updated_at: string;
}

interface CreatePollingGroupRequest {
  name: string;
  polling_interval: number;
  is_active: boolean;
  tag_ids: number[];
}

interface PollingControlResponse {
  success: boolean;
  message: string;
  new_status: string;
}
```

### System Status
```typescript
interface SystemStatus {
  cpu_percent: number; // 0-100
  memory_used_gb: number;
  memory_total_gb: number;
  memory_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  disk_percent: number;
  timestamp: string;
}

interface PLCStatus {
  plc_id: number;
  plc_name: string;
  is_online: boolean;
  last_seen?: string;
}

interface BufferStatus {
  current_size: number;
  max_size: number;
  utilization_percent: number;
  overflow_count: number;
  last_overflow_time?: string;
}

interface OracleWriterStatus {
  success_count: number;
  fail_count: number;
  success_rate_percent: number;
  backup_file_count: number;
}

interface DashboardData {
  system: SystemStatus;
  plc_status: PLCStatus[];
  active_polling_groups: number;
  total_polling_groups: number;
  buffer: BufferStatus;
  oracle_writer: OracleWriterStatus;
}
```

### Log Entry
```typescript
interface LogEntry {
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  stack_trace?: string;
}

interface LogQueryParams {
  log_type: "scada" | "error" | "communication" | "performance";
  start_time?: string;
  end_time?: string;
  levels?: string[]; // ["ERROR", "CRITICAL"]
  search?: string;
  page: number;
  limit: number; // default 50
}

interface LogQueryResponse {
  items: LogEntry[];
  total: number;
  page: number;
  limit: number;
}
```

## Pagination Response Pattern

```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number; // total / limit rounded up
}
```

## Validation Rules

### Line
- name: 1-100 characters, required
- code: 1-20 characters, uppercase letters/numbers, required, unique

### Process
- name: 1-100 characters, required
- code: 14 characters, pattern [A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}, required, unique
- line_id: must exist in Lines table

### PLC
- name: 1-100 characters, required
- ip_address: valid IPv4 format, required
- port: 1-65535, required
- plc_type: enum ["MC-3E"], required
- protocol: enum ["ASCII", "Binary"], required
- process_id: must exist in Processes table

### Tag
- name: 1-100 characters, required
- device_address: 1-20 characters, required
- data_type: enum ["INT", "FLOAT", "BOOL"], required
- polling_interval: 0.5-60 seconds, required
- plc_id: must exist in PLCs table

### Polling Group
- name: 1-100 characters, required
- polling_interval: 0.5-60 seconds, required
- tag_ids: non-empty array, each ID must exist in Tags table

## State Transitions

### Polling Group Status
```
stopped -> running (via /start)
running -> stopped (via /stop)
running -> error (on polling failure)
error -> running (via /restart)
stopped -> running (via /restart)
```
