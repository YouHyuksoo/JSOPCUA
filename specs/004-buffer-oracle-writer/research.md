# Technical Research: Thread-Safe Buffer and Oracle DB Writer

**Date**: 2025-11-02
**Feature**: 004-buffer-oracle-writer

## Research Questions

### 1. python-oracledb: Thin Mode vs Thick Mode

**Question**: Should we use Thin mode or Thick mode for Oracle connectivity?

**Research Findings**:

- **python-oracledb** (successor to cx_Oracle):
  - Official Oracle-supported driver (cx_Oracle is now deprecated)
  - Two modes: Thin (pure Python) and Thick (requires Instant Client)

- **Thin Mode**:
  - Pure Python implementation, **no Oracle Instant Client required**
  - Zero external dependencies (just `pip install python-oracledb`)
  - Fully functional for most use cases (SQL, PL/SQL, connection pooling, batch operations)
  - Simpler deployment (no native library management)
  - Sufficient performance for most workloads

- **Thick Mode**:
  - Requires Oracle Instant Client installation
  - Higher performance for very large data transfers
  - Required for advanced features (Oracle Advanced Queuing, LDAP, external authentication)
  - More complex deployment

**Decision**: **Use python-oracledb Thin Mode**

**Rationale**:
- **No Instant Client dependency** - much simpler deployment
- Sufficient performance for our scale (1,000 values/second, 500-row batches)
- Feature requirements don't need Thick mode capabilities
- Easier testing and CI/CD
- Production-ready and officially supported by Oracle

**Implementation**:
```python
import oracledb

# Thin mode is the default - no init_oracle_client() call needed
pool = oracledb.create_pool(
    user="scada_user",
    password="password",
    dsn="oracle.example.com:1521/XEPDB1",
    min=2,
    max=5,
    increment=1
)
```

**Note**: No Oracle Instant Client installation required for Thin mode!

---

### 2. Circular Buffer Implementation with collections.deque

**Question**: How to implement thread-safe circular buffer with automatic FIFO overflow?

**Research Findings**:

- **collections.deque** with maxlen:
  - Thread-safe for atomic operations (append, popleft)
  - Automatic FIFO eviction when full (oldest data discarded)
  - O(1) complexity for append and popleft
  - Built-in, no external dependencies

- **queue.Queue**:
  - Thread-safe but blocks when full (not suitable for overflow case)
  - No automatic eviction
  - Would require manual overflow handling

- **List + Lock**:
  - Requires manual synchronization
  - O(n) complexity for removing oldest item
  - More error-prone

**Decision**: **Use collections.deque with maxlen=10000**

**Rationale**:
- Built-in automatic FIFO eviction (perfect for overflow handling per FR-004)
- Thread-safe for single-producer-single-consumer pattern
- Simpler code than manual lock management
- Zero overhead for overflow protection
- User specification requires 10,000 item capacity

**Implementation**:
```python
from collections import deque
from threading import Lock

class CircularBuffer:
    def __init__(self, maxsize: int = 10000):
        self._buffer = deque(maxlen=maxsize)
        self._lock = Lock()  # For len() and copy operations
        self._overflow_count = 0
        self.maxsize = maxsize

    def put(self, item):
        """Add item, auto-evict oldest if full"""
        was_full = len(self._buffer) == self.maxsize
        self._buffer.append(item)  # Thread-safe atomic operation
        if was_full:
            with self._lock:
                self._overflow_count += 1

    def get_batch(self, max_items: int):
        """Get and remove up to max_items from left"""
        batch = []
        for _ in range(min(max_items, len(self._buffer))):
            if self._buffer:
                batch.append(self._buffer.popleft())  # Thread-safe
        return batch
```

**Note**: While deque operations are atomic, we still use Lock for statistics to avoid race conditions on overflow counter.

---

### 3. Oracle Bulk Insert Best Practices

**Question**: What is the optimal batch size and method for bulk inserts?

**Research Findings**:

- **executemany() with batch sizes**:
  - Oracle recommends 100-1,000 rows per batch
  - Larger batches reduce round-trips but increase memory
  - python-oracledb automatically uses array binding
  - Performance sweet spot: 500-1,000 rows

- **Batch size considerations**:
  - Small batches (10-50): Too many round-trips, low throughput
  - Medium batches (100-500): Good balance
  - Large batches (1,000-5,000): Best throughput, higher memory
  - Very large batches (5,000+): Diminishing returns, timeout risk

- **Error handling**:
  - executemany() stops on first error by default
  - Use batcherrors=True to collect all errors and continue
  - Allows partial batch success

**Decision**: **Use executemany() with batch size up to 500**

**Rationale**:
- Optimal balance of throughput and memory
- Aligns with requirement FR-008 (up to 500 items per batch)
- User specification explicitly requires max 500 rows per batch
- cx_Oracle handles parameter binding automatically

**Implementation**:
```python
def write_batch(connection, batch_data):
    """Write batch to Oracle using executemany"""
    sql = """
        INSERT INTO TAG_DATA
        (tag_name, tag_value, timestamp, quality)
        VALUES (:1, :2, :3, :4)
    """

    # Prepare batch as list of tuples
    rows = [(d.tag_name, d.tag_value, d.timestamp, d.quality)
            for d in batch_data]

    cursor = connection.cursor()
    cursor.executemany(sql, rows)

    connection.commit()
    return len(rows), 0
```

---

### 4. Thread Synchronization: Producer-Consumer Pattern

**Question**: How to coordinate buffer consumer (DataQueue reader) and writer (Oracle writer)?

**Research Findings**:

- **Pattern Options**:
  1. **Threading + Queue**: Standard library, simple
  2. **Threading + Condition Variable**: More control over timing
  3. **asyncio**: Event loop based, different paradigm
  4. **multiprocessing**: Separate processes, overhead

- **threading.Lock + threading.Condition**:
  - Condition allows "notify when data available or time elapsed"
  - More efficient than polling
  - Can wait with timeout (supports "1 second OR 500 items" trigger)

- **Two-Stage Queue Design**:
  - Stage 1: Feature 3's DataQueue (producer: polling threads)
  - Stage 2: Circular Buffer (consumer: buffer thread, producer: writer thread)
  - Writer thread waits on condition variable

**Decision**: **Single consumer thread + Condition variable for timed writes**

**Rationale**:
- Single thread simplifies synchronization (no thread pool needed)
- Condition.wait(timeout) naturally implements "0.5 second OR buffer threshold" per FR-009
- Feature 3's DataQueue already handles multi-producer safely
- Clean separation: consumer thread moves data to buffer, writer thread batches to Oracle

**Implementation**:
```python
from threading import Thread, Lock, Condition
import queue

class BufferConsumer(Thread):
    """Consume from DataQueue, feed to CircularBuffer"""
    def __init__(self, data_queue, circular_buffer):
        super().__init__(daemon=True)
        self.data_queue = data_queue
        self.buffer = circular_buffer
        self.running = True

    def run(self):
        while self.running:
            try:
                # Block up to 1 second waiting for data
                polling_data = self.data_queue.get(timeout=1.0)

                # Expand PollingData into individual BufferedTagValue items
                for tag_addr, tag_val in polling_data.tag_values.items():
                    buffered_item = BufferedTagValue(
                        timestamp=polling_data.timestamp,
                        plc_code=polling_data.plc_code,
                        tag_address=tag_addr,
                        tag_value=tag_val,
                        quality='GOOD'  # From successful poll
                    )
                    self.buffer.put(buffered_item)

            except queue.Empty:
                continue  # No data, retry

class OracleWriter(Thread):
    """Write batches from CircularBuffer to Oracle"""
    def __init__(self, buffer, oracle_pool, write_interval=0.5, batch_threshold=500):
        super().__init__(daemon=True)
        self.buffer = buffer
        self.pool = oracle_pool
        self.interval = write_interval  # 0.5 seconds per FR-009
        self.threshold = batch_threshold  # 500 items per FR-008
        self.condition = Condition()
        self.running = True

    def run(self):
        while self.running:
            # Wait for interval (0.5s) OR notification from consumer
            with self.condition:
                self.condition.wait(timeout=self.interval)

            # Check if batch threshold met
            if len(self.buffer) >= self.threshold or len(self.buffer) > 0:
                batch = self.buffer.get_batch(max_items=500)  # Max 500 per FR-008
                if batch:
                    self._write_batch_to_oracle(batch)
```

---

### 5. CSV Backup Strategy

**Question**: How to efficiently write failed batches to CSV for recovery?

**Research Findings**:

- **csv.DictWriter**:
  - Clean API for writing dict-like objects
  - Automatic header generation
  - Buffer control via file buffering parameter

- **File naming**:
  - Timestamp-based: `backup_20251102_143025.csv`
  - Unique per failure (avoids overwrite)
  - Sortable by filename

- **Buffering**:
  - Default buffering (8KB) sufficient for backup (not performance-critical)
  - Flush after each write for safety (data integrity > performance)

**Decision**: **Use csv.DictWriter with timestamp-based filenames**

**Implementation**:
```python
import csv
from datetime import datetime
from pathlib import Path

def save_to_csv_backup(batch_data, backup_dir='./backup'):
    """Save failed batch to timestamped CSV file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = Path(backup_dir) / f'backup_{timestamp}.csv'

    # Ensure backup directory exists
    backup_file.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV with headers
    with open(backup_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['tag_name', 'tag_value', 'timestamp',
                      'quality', 'insertion_attempt_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in batch_data:
            writer.writerow({
                'tag_name': item.tag_name,
                'tag_value': item.tag_value,
                'timestamp': item.timestamp.isoformat(),
                'quality': item.quality,
                'insertion_attempt_time': datetime.now().isoformat()
            })

    logger.info(f"Saved {len(batch_data)} items to {backup_file}")
    return backup_file
```

---

### 6. Connection Pool Management

**Question**: How to manage Oracle connection pool lifecycle?

**Research Findings**:

- **oracledb.create_pool()**:
  - min: Minimum connections (keep-alive)
  - max: Maximum connections (hard limit)
  - increment: How many to create when pool grows
  - Automatically thread-safe in python-oracledb

- **Recommended settings for our use case**:
  - min=2: Keep 2 connections warm for fast writes
  - max=5: Limit to 5 per FR-007 (1 writer thread + extras for retry)
  - increment=1: Grow gradually

- **Pool lifecycle**:
  - Create pool once at startup
  - Reuse connections via `pool.acquire()`
  - Release back to pool automatically (context manager)
  - Close pool on shutdown

**Decision**: **create_pool with min=2, max=5**

**Implementation**:
```python
import oracledb

class OracleConnectionPool:
    def __init__(self, dsn, user, password):
        self.pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=dsn,
            min=2,
            max=5,
            increment=1
        )
        logger.info(f"Oracle connection pool created (min=2, max=5) - Thin mode")

    def acquire(self):
        """Get connection from pool (use with context manager)"""
        return self.pool.acquire()

    def close(self):
        """Close all connections in pool"""
        self.pool.close()
        logger.info("Oracle connection pool closed")

# Usage
pool = OracleConnectionPool(
    dsn="oracle.example.com:1521/XEPDB1",
    user="scada_user",
    password="password"
)

# Write batch
with pool.acquire() as connection:
    write_batch(connection, batch_data)
```

---

### 7. Exponential Backoff Retry Strategy

**Question**: How to implement retry with exponential backoff for Oracle failures?

**Research Findings**:

- **Retry patterns**:
  - Fixed delay: Simple but can overload recovering system
  - Exponential backoff: 1s → 2s → 4s → 8s (doubles each retry)
  - Exponential backoff with jitter: Adds randomness to avoid thundering herd

- **python-oracledb transient errors**:
  - Connection timeout (oracledb.DatabaseError)
  - Network errors
  - Database unavailable
  - Pool exhaustion

- **Retry limits**:
  - Max retries: 3 (per requirement FR-010)
  - Backoff delays: 1s, 2s, 4s (per requirement FR-010)
  - Give up after 3 attempts, save to CSV per FR-011

**Decision**: **Exponential backoff with 3 retries (1s, 2s, 4s)**

**Implementation**:
```python
import time
import oracledb

def write_with_retry(pool, batch_data, max_retries=3):
    """Write batch with exponential backoff retry per FR-010"""
    attempt = 0
    delay = 1.0  # Start with 1 second

    while attempt < max_retries:
        try:
            with pool.acquire() as connection:
                success_count, error_count = write_batch(connection, batch_data)
                logger.info(f"Batch written: {success_count} success, {error_count} errors")
                return True

        except oracledb.DatabaseError as e:
            attempt += 1
            logger.warning(f"Oracle write failed (attempt {attempt}/{max_retries}): {e}")

            if attempt < max_retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff: 1s, 2s, 4s
            else:
                logger.error(f"All {max_retries} retries exhausted, saving to CSV backup")
                backup_file = save_to_csv_backup(batch_data)
                return False

    return False
```

---

### 8. Rolling Average Calculation for Metrics

**Question**: How to efficiently calculate rolling average for batch size and latency?

**Research Findings**:

- **Options**:
  1. **collections.deque with fixed size**: Keep last N samples, calculate mean
  2. **Running average formula**: `new_avg = old_avg + (new_value - old_avg) / count`
  3. **Time-windowed (5 minutes)**: Store timestamps, filter old samples

- **Requirement**: "Rolling 5-minute window" for avg_batch_size and avg_write_latency

- **Trade-offs**:
  - Deque: Simple, accurate, memory proportional to window size
  - Running average: Constant memory, but no time window
  - Time-windowed: Most accurate, requires timestamp tracking

**Decision**: **Use collections.deque with time-based filtering**

**Rationale**:
- Accurately represents "last 5 minutes"
- Reasonable memory (5 min at 1 write/sec = 300 samples max)
- Simple implementation with deque

**Implementation**:
```python
from collections import deque
from datetime import datetime, timedelta

class RollingMetrics:
    """Track rolling average over time window"""
    def __init__(self, window_seconds=300):  # 5 minutes default
        self.window = timedelta(seconds=window_seconds)
        self.samples = deque()  # (timestamp, value) tuples

    def add(self, value):
        """Add new sample with current timestamp"""
        now = datetime.now()
        self.samples.append((now, value))
        self._cleanup_old_samples(now)

    def _cleanup_old_samples(self, now):
        """Remove samples outside window"""
        cutoff = now - self.window
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()

    def average(self):
        """Calculate average of samples in window"""
        now = datetime.now()
        self._cleanup_old_samples(now)

        if not self.samples:
            return 0.0

        total = sum(value for _, value in self.samples)
        return total / len(self.samples)

# Usage
batch_size_metrics = RollingMetrics(window_seconds=300)
latency_metrics = RollingMetrics(window_seconds=300)

# After each write
batch_size_metrics.add(len(batch))
latency_metrics.add(write_time_ms)

# Query
avg_batch_size = batch_size_metrics.average()
avg_latency = latency_metrics.average()
```

---

## Implementation Summary

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Oracle Driver | python-oracledb (Thin mode) | Zero dependencies, simpler deployment |
| Circular Buffer | collections.deque(maxlen) | Built-in FIFO overflow, thread-safe atomic ops |
| Thread Sync | threading.Lock + Condition | Standard library, efficient timed waits |
| Batch Insert | cursor.executemany() | Oracle best practice, up to 500 rows per FR-008 |
| CSV Backup | csv.DictWriter | Standard library, clean API |
| Connection Pool | oracledb.create_pool() | Efficient connection reuse |
| Retry Logic | Exponential backoff | Industry standard, avoids overload |
| Metrics | collections.deque (time-filtered) | Accurate rolling window |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature 3: Polling Engine                │
│                     DataQueue (queue.Queue)                 │
└────────────────────────────┬────────────────────────────────┘
                             │ PollingData objects
                             ▼
                  ┌─────────────────────┐
                  │  BufferConsumer     │ (Thread 1)
                  │  - Reads DataQueue  │
                  │  - Expands to items │
                  └──────────┬──────────┘
                             │ BufferedTagValue objects
                             ▼
                  ┌─────────────────────┐
                  │  CircularBuffer     │ (deque, maxlen=100k)
                  │  - FIFO overflow    │
                  │  - Thread-safe      │
                  └──────────┬──────────┘
                             │ get_batch(1000)
                             ▼
                  ┌─────────────────────┐
                  │  OracleWriter       │ (Thread 2)
                  │  - Batch 100-1k     │
                  │  - Retry 3x         │
                  │  - CSV backup       │
                  └──────────┬──────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
           ┌────────────────┐  ┌──────────────┐
           │ Oracle DB      │  │ CSV Backup   │
           │ tag_values tbl │  │ backup_*.csv │
           └────────────────┘  └──────────────┘
```

### Performance Estimates

Based on research findings:

- **Buffer throughput**: 1,000+ items/sec (deque append is O(1))
- **Oracle write throughput**: 500-1,000 rows/sec (batch size dependent)
- **Memory usage**: ~500MB for 100,000 items (5KB per item average)
- **Write latency**: 200-500ms for 500-item batch (network + DB)
- **CSV backup**: 100-200 rows/sec (I/O bound, not performance critical)

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Oracle prolonged outage | Circular buffer holds 100k items (~1-2 minutes at 1k/s), CSV backup for overflow |
| Memory exhaustion | Buffer maxlen prevents unlimited growth, oldest data discarded |
| Write bottleneck | Batch writing (100-1k) reduces DB round-trips by 100-1000x |
| Connection pool starvation | Pool max=5 with timeout=10s, writer thread logs and retries |
| Data loss on crash | CSV backup provides recovery path, buffer is in-memory (trade-off for speed) |

---

**Next Steps**: Proceed to data-model.md to define entities and Oracle schema.
