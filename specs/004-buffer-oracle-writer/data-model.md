# Data Model: Thread-Safe Buffer and Oracle DB Writer

**Date**: 2025-11-02
**Feature**: 004-buffer-oracle-writer

## Entities

### 1. BufferedTagValue (In-Memory Buffer Item)

Individual tag value extracted from Feature 3's PollingData and stored in circular buffer.

**Attributes**:
- `tag_name` (str): Tag name/identifier (e.g., "LINE1_TEMP_SENSOR_01")
- `tag_value` (float or str): Tag value (numeric or string)
- `timestamp` (datetime): Data collection time (from polling engine)
- `quality` (str): Data quality indicator ("GOOD", "BAD")

**Source**: Created by BufferConsumer thread from Feature 3's PollingData

**Relationships**:
- 1 PollingData (Feature 3) → N BufferedTagValue (one per tag in tag_values dict)
- N BufferedTagValue → 1 WriteBatch (grouped for Oracle insert)

**Format Example**:
```python
BufferedTagValue(
    tag_name="LINE1_TEMP_SENSOR_01",
    tag_value=1234.5,
    timestamp=datetime(2025, 11, 2, 14, 30, 45, 123456),
    quality="GOOD"
)
```

**Transformation from PollingData**:
```python
# Feature 3's PollingData
polling_data = PollingData(
    timestamp=datetime.now(),
    group_id=1,
    group_name="LINE1_PROCESS1",
    plc_code="PLC01",
    mode=PollingMode.FIXED,
    tag_values={"D100": 1234.5, "D101": 5678.9},  # Multiple tags
    poll_time_ms=45.2,
    error_tags={}
)

# Expanded to 2 BufferedTagValue items
buffer_items = [
    BufferedTagValue(
        timestamp=polling_data.timestamp,
        plc_code="PLC01",
        tag_address="D100",
        tag_value=1234.5,
        quality="GOOD"
    ),
    BufferedTagValue(
        timestamp=polling_data.timestamp,
        plc_code="PLC01",
        tag_address="D101",
        tag_value=5678.9,
        quality="GOOD"
    )
]
```

**Quality Mapping**:
- `"GOOD"`: Tag exists in `tag_values` (successful poll)
- `"BAD"`: Tag exists in `error_tags` (polling error)
- `"UNCERTAIN"`: Tag missing from both (timeout/partial failure)

---

### 2. WriteBatch (Oracle Insert Operation)

Collection of BufferedTagValue items grouped for single Oracle bulk insert.

**Attributes**:
- `batch_id` (str): Unique batch identifier (UUID or timestamp-based)
- `items` (List[BufferedTagValue]): Tag values to write (up to 500 items)
- `created_at` (datetime): When batch was created
- `retry_count` (int): Number of retry attempts (0-3)

**Validation**:
- Minimum batch size: 1 (can write partial batch on shutdown)
- Maximum batch size: 500 (per FR-008)
- Typical batch size: 100-500 items

**Batch Creation Triggers**:
1. Time-based: 0.5 seconds elapsed since last write (FR-009)
2. Size-based: Buffer contains ≥500 items (FR-009)
3. Shutdown: Flush remaining items regardless of size

**Format Example**:
```python
WriteBatch(
    batch_id="batch_20251102_143045_001",
    items=[
        BufferedTagValue(...),  # 500 items
        BufferedTagValue(...),
        # ...
    ],
    created_at=datetime(2025, 11, 2, 14, 30, 45),
    retry_count=0
)
```

**Lifecycle**:
```
[Created from buffer] → [Retry 0: Oracle write attempt]
                            ↓ success         ↓ failure
                         [Complete]      [Retry 1: wait 1s]
                                              ↓ success  ↓ failure
                                           [Complete] [Retry 2: wait 2s]
                                                         ↓ success  ↓ failure
                                                      [Complete] [Retry 3: wait 4s]
                                                                    ↓ success  ↓ failure
                                                                 [Complete] [CSV Backup]
```

---

### 3. WriterMetrics (Performance Statistics)

Real-time performance metrics for buffer and writer operations.

**Attributes**:
- `current_buffer_size` (int): Current items in circular buffer
- `total_inserted` (int): Total items inserted to buffer since startup
- `total_removed` (int): Total items removed from buffer (written to Oracle)
- `successful_writes` (int): Successful write batches
- `failed_writes` (int): Failed write batches (after all retries)

**Derived Metrics**:
- `buffer_utilization_pct` (float): (current_buffer_size / 10,000) × 100
- `overflow_count` (int): total_inserted - total_removed - current_buffer_size
- `success_rate_pct` (float): successful_writes / (successful_writes + failed_writes) × 100

**Update Frequency**:
- Real-time updates (thread-safe counters)
- Rolling averages updated per write operation
- Exposed via monitoring API (GET /api/buffer/metrics)

**Format Example**:
```python
WriterMetrics(
    buffer_current_size=12500,
    buffer_max_size=100000,
    buffer_utilization_pct=12.5,
    overflow_count=0,
    total_writes=1547,
    successful_writes=1545,
    failed_writes=2,
    success_rate_pct=99.87,
    avg_batch_size=487.3,
    avg_write_latency_ms=342.1,
    backup_file_count=2,
    last_write_time=datetime(2025, 11, 2, 14, 30, 45)
)
```

**API Response**:
```json
{
  "buffer": {
    "current_size": 12500,
    "max_size": 100000,
    "utilization_pct": 12.5,
    "overflow_count": 0
  },
  "writer": {
    "total_writes": 1547,
    "successful_writes": 1545,
    "failed_writes": 2,
    "success_rate_pct": 99.87,
    "avg_batch_size": 487.3,
    "avg_write_latency_ms": 342.1,
    "last_write_time": "2025-11-02T14:30:45.123456"
  },
  "backup": {
    "file_count": 2
  }
}
```

---

### 4. BackupRecord (CSV Backup Format)

Failed data saved to CSV file for manual recovery.

**CSV Columns**:
- `timestamp` (ISO 8601 string): Original data collection time
- `plc_code` (str): PLC identifier
- `tag_address` (str): Tag address
- `tag_value` (float): Tag value
- `quality` (str): Quality indicator
- `insertion_attempt_time` (ISO 8601 string): When Oracle write was attempted

**CSV File Naming**:
- Format: `backup_YYYYMMDD_HHMMSS.csv`
- Example: `backup_20251102_143045.csv`
- Location: Configured backup directory (default: `./backup/`)

**CSV Example**:
```csv
timestamp,plc_code,tag_address,tag_value,quality,insertion_attempt_time
2025-11-02T14:30:45.123456,PLC01,D100,1234.5,GOOD,2025-11-02T14:30:52.789012
2025-11-02T14:30:45.123456,PLC01,D101,5678.9,GOOD,2025-11-02T14:30:52.789012
2025-11-02T14:30:46.234567,PLC02,D200,9012.3,GOOD,2025-11-02T14:30:52.789012
```

**Manual Recovery Process** (Out of Scope for Feature 4):
```sql
-- Operator manually loads CSV into Oracle
-- Example using SQL*Loader or Oracle SQL Developer import
LOAD DATA
INFILE 'backup_20251102_143045.csv'
INTO TABLE tag_values
FIELDS TERMINATED BY ','
(timestamp, plc_code, tag_address, tag_value, quality, inserted_at EXPRESSION "CURRENT_TIMESTAMP")
```

---

### 5. Oracle TAG_DATA Table (Database Schema)

Target table for persistent storage of all tag values.

**Schema**:
```sql
CREATE TABLE TAG_DATA (
    tag_name        VARCHAR2(100) NOT NULL,
    tag_value       VARCHAR2(255) NOT NULL,  -- Supports both numeric and string values
    timestamp       TIMESTAMP(6) NOT NULL,
    quality         VARCHAR2(20) NOT NULL,
    CONSTRAINT pk_tag_data PRIMARY KEY (tag_name, timestamp)
);

-- Index for time-range queries
CREATE INDEX idx_tag_data_timestamp ON TAG_DATA(timestamp);

-- Optional: Index for tag name queries
CREATE INDEX idx_tag_data_tag_name ON TAG_DATA(tag_name);
```

**Column Details**:

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `tag_name` | VARCHAR2(100) | Tag identifier/name | NOT NULL, PK part 1 |
| `tag_value` | VARCHAR2(255) | Tag value (numeric or string) | NOT NULL |
| `timestamp` | TIMESTAMP(6) | Data collection time (microsecond precision) | NOT NULL, PK part 2 |
| `quality` | VARCHAR2(20) | Quality indicator (GOOD/BAD) | NOT NULL |

**Primary Key** (Composite):
- Prevents duplicate entries for same tag at same timestamp
- Natural key for time-series data: (tag_name, timestamp)
- Supports efficient tag-based and time-range queries

**Expected Data Volume**:
- At 1,000 values/second: ~86 million rows/day
- At 10,000 values/second: ~864 million rows/day
- Storage estimation: ~100 bytes/row → 8.6 GB/day (1k/s), 86 GB/day (10k/s)
- **Recommendation**: Implement partitioning by timestamp (monthly) for large deployments

**Duplicate Handling**:
```python
# executemany() with batcherrors=True
# Duplicate key violations are logged but don't stop batch
try:
    cursor.executemany(sql, rows, batcherrors=True)
    errors = cursor.getbatcherrors()
    for error in errors:
        if 'ORA-00001' in str(error.message):  # Unique constraint violation
            logger.warning(f"Duplicate key at offset {error.offset}, skipping")
except oracledb.Error as e:
    logger.error(f"Batch insert failed: {e}")
```

---

## Relationships Diagram

```
┌────────────────────────────────────────────────────┐
│          Feature 3: Polling Engine                 │
│                                                    │
│  PollingData {                                     │
│    timestamp, group_id, plc_code,                  │
│    tag_values: {"D100": 1234, "D101": 5678}  ←──┐ │
│  }                                              │ │
└──────────────────────────┬─────────────────────┘ │
                           │ 1:N expansion        │
                           ▼                      │
         ┌─────────────────────────────┐          │
         │  BufferedTagValue           │          │
         │  ├─ timestamp (from PD)     │          │
         │  ├─ plc_code (from PD)      │          │
         │  ├─ tag_address (from key)  │──────────┘
         │  ├─ tag_value (from value)  │
         │  └─ quality (derived)       │
         └──────────┬──────────────────┘
                    │ stored in
                    ▼
         ┌─────────────────────────────┐
         │  CircularBuffer (deque)     │
         │  └─ maxlen: 10,000          │
         └──────────┬──────────────────┘
                    │ batched (up to 500 items)
                    ▼
         ┌─────────────────────────────┐
         │  WriteBatch                 │
         │  ├─ batch_id                │
         │  ├─ items: [BTV, BTV, ...]  │
         │  └─ retry_count             │
         └──────────┬──────────────────┘
                    │
           ┌────────┴────────┐
           │ SUCCESS (write) │ FAILURE (after 3 retries)
           ▼                 ▼
  ┌────────────────┐  ┌──────────────────┐
  │ Oracle DB      │  │ BackupRecord     │
  │                │  │ (CSV file)       │
  │ TAG_DATA {     │  │                  │
  │   tag_name,    │  │ backup_*.csv {   │
  │   tag_value,   │  │   tag_name,      │
  │   timestamp,   │  │   tag_value,     │
  │   quality      │  │   timestamp,     │
  │ }              │  │   quality,       │
  └────────────────┘  │   attempt_time   │
                      │ }                │
                      └──────────────────┘
```

---

## Data Flow Sequence

### Normal Operation (Successful Write)

```
1. Polling Engine produces PollingData
   PollingData {
     timestamp: 2025-11-02T14:30:45,
     plc_code: "PLC01",
     tag_values: {"D100": 1234, "D101": 5678}
   }
   ↓
2. BufferConsumer thread reads from DataQueue
   ↓
3. Expand to BufferedTagValue items
   - BufferedTagValue(timestamp, "PLC01", "D100", 1234, "GOOD")
   - BufferedTagValue(timestamp, "PLC01", "D101", 5678, "GOOD")
   ↓
4. Append to CircularBuffer (deque)
   ↓
5. OracleWriter checks trigger conditions
   - 1 second elapsed? OR
   - Buffer size ≥ 500?
   ↓
6. Create WriteBatch (500 items)
   ↓
7. Execute Oracle bulk insert
   INSERT INTO tag_values VALUES
   (timestamp1, plc_code1, tag_addr1, value1, quality1, CURRENT_TIMESTAMP),
   (timestamp2, plc_code2, tag_addr2, value2, quality2, CURRENT_TIMESTAMP),
   ... (500 rows)
   ↓
8. Update WriterMetrics
   - successful_writes += 1
   - avg_batch_size rolling update
   - avg_write_latency_ms rolling update
```

### Failure Handling (Oracle Unavailable)

```
1. OracleWriter creates WriteBatch
   ↓
2. Attempt 1: Oracle write fails (network error)
   ↓ wait 1 second
3. Attempt 2: Oracle write fails (timeout)
   ↓ wait 2 seconds
4. Attempt 3: Oracle write fails (connection refused)
   ↓ wait 4 seconds
5. Attempt 4: Oracle write fails (still unavailable)
   ↓
6. Save to CSV backup
   - Create backup_20251102_143052.csv
   - Write 500 rows to CSV
   - Log backup file path
   ↓
7. Update WriterMetrics
   - failed_writes += 1
   - backup_file_count += 1
   ↓
8. Continue processing (don't crash)
```

### Buffer Overflow (CircularBuffer Full)

```
1. CircularBuffer at capacity (100,000 items)
   ↓
2. BufferConsumer tries to add item 100,001
   ↓
3. deque.append() auto-evicts oldest item (FIFO)
   ↓
4. Increment overflow_count metric
   ↓
5. Log warning: "Buffer overflow, discarded oldest data"
   ↓
6. Continue (system remains operational)
```

---

## Concurrency Model

### Thread-Safe Operations

| Operation | Thread Safety | Mechanism |
|-----------|---------------|-----------|
| deque.append() | Atomic | GIL (Global Interpreter Lock) |
| deque.popleft() | Atomic | GIL |
| deque length check | Not atomic | Requires Lock for len() |
| Metrics update | Atomic | threading.Lock on increment |
| CSV write | Single writer | Only OracleWriter writes to CSV |
| Oracle pool acquire | Thread-safe | oracledb.Pool internal locking |

### Lock Strategy

```python
# CircularBuffer
class CircularBuffer:
    def __init__(self):
        self._buffer = deque(maxlen=10000)  # Thread-safe for single ops, FR-002
        self._lock = Lock()  # For multi-step operations only

    def put(self, item):
        # Atomic operation, no lock needed
        self._buffer.append(item)

    def get_batch(self, max_items):
        # Multi-step operation, needs lock for consistency
        with self._lock:
            batch = []
            for _ in range(min(max_items, len(self._buffer))):
                if self._buffer:
                    batch.append(self._buffer.popleft())
            return batch

# WriterMetrics
class WriterMetrics:
    def __init__(self):
        self._lock = Lock()
        self.total_writes = 0
        # ...

    def increment_total_writes(self):
        with self._lock:
            self.total_writes += 1
```

---

## Performance Characteristics

### Memory Usage

| Component | Size Estimate | Notes |
|-----------|---------------|-------|
| BufferedTagValue | ~200 bytes | datetime (32B) + strings (100B) + value (8B) + overhead |
| CircularBuffer (10k items) | ~2 MB | 200 bytes × 10,000 |
| WriterMetrics | ~1 KB | Simple counters |
| **Total estimated** | **~5 MB** | Well under 50MB constraint (per Technical Context) |

### Throughput Estimates

Based on research.md findings:

- **Buffer throughput**: 10,000+ items/sec (deque append is O(1))
- **Oracle write throughput**: 500-1,000 items/sec (batch-dependent)
- **Bottleneck**: Oracle network + DB write (not buffer)
- **Sustainable rate**: 1,000 items/sec (meets SC-001)

### Latency Breakdown

Typical write cycle (500-item batch):

| Phase | Time | Notes |
|-------|------|-------|
| Buffer.get_batch() | 1-2 ms | In-memory deque operations |
| Pool.acquire() | 1-10 ms | Wait for connection (usually instant) |
| Network + INSERT | 100-300 ms | Batch of 500 rows |
| Commit | 50-100 ms | Oracle transaction commit |
| **Total** | **150-400 ms** | Well under 2-second target (SC-002) |

---

**Next Steps**: Proceed to quickstart.md for integration scenarios and testing.
