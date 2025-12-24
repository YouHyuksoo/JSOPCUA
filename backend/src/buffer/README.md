# Buffer Module

Thread-safe circular buffer for temporary data storage between polling engine and Oracle writer.

## Overview

The buffer module provides a memory-based circular buffer with automatic FIFO overflow handling. It sits between Feature 3's polling engine and Feature 4's Oracle writer, buffering tag values in memory before batch writing to Oracle.

## Architecture

```
┌─────────────────┐
│ CircularBuffer  │
│  ├─ deque       │──────> collections.deque(maxlen=10000)
│  ├─ Metrics     │──────> Overflow tracking
│  └─ Alerts      │──────> Logging warnings
└────────┬────────┘
         │
         ├──> BufferConsumer (Thread)
         │      └─> Reads from DataQueue
         │
         └──> OracleWriter (Thread)
                └─> Writes batches to Oracle
```

## Components

- **circular_buffer.py**: Thread-safe deque-based buffer with FIFO overflow
- **buffer_consumer.py**: Consumer thread that reads from Feature 3's DataQueue
- **models.py**: BufferedTagValue data class
- **exceptions.py**: BufferEmptyError, BufferOverflowError

## Usage

### Initialize Buffer

```python
from buffer.circular_buffer import CircularBuffer

# Create buffer with 10,000 capacity
buffer = CircularBuffer(maxsize=10000, overflow_alert_threshold=80.0)
```

### Add Items

```python
from buffer.models import BufferedTagValue
from datetime import datetime

tag_value = BufferedTagValue(
    timestamp=datetime.now(),
    plc_code="PLC01",
    tag_address="D100",
    tag_value=1234.5,
    quality="GOOD"
)

success = buffer.put(tag_value)
if not success:
    print("Buffer overflow occurred")
```

### Retrieve Items

```python
# Get batch of items (FIFO order)
items = buffer.get(count=500)

# Peek without removing
items = buffer.peek(count=10)
```

### Monitor Status

```python
stats = buffer.stats()
print(f"Buffer size: {stats['current_size']}/{stats['max_size']}")
print(f"Utilization: {stats['utilization_pct']}%")
print(f"Overflow count: {stats['overflow_count']}")
print(f"Overflow rate: {stats['overflow_rate_pct']}%")
```

## Features

### FIFO Overflow Handling

When buffer reaches maximum capacity (10,000 items), oldest items are automatically discarded:

```python
# Buffer at capacity (10,000 items)
buffer.put(new_item)  # Returns False, oldest item is discarded
```

### Overflow Alerts

Warnings are logged when:
- Buffer utilization reaches 80% threshold
- Overflow events occur

```
WARNING: Buffer utilization high: 85.2% (8520/10000 items). Approaching capacity!
WARNING: Buffer overflow #1: Discarded oldest item (FIFO). Total added: 10001, Overflow rate: 0.010%
```

### Thread Safety

All operations are thread-safe using `threading.Lock`:
- Multiple threads can safely call `put()` and `get()`
- BufferConsumer and OracleWriter access the same buffer concurrently

## Performance

- **Capacity**: 10,000 items (configurable)
- **Memory usage**: ~1-2 MB for 10,000 items
- **Put/Get operations**: O(1) time complexity
- **Overflow handling**: Automatic FIFO eviction
- **Thread overhead**: Minimal (single lock per operation)

## Configuration

Environment variables (optional):
```bash
BUFFER_MAX_SIZE=10000          # Maximum buffer capacity
BUFFER_ALERT_THRESHOLD=80.0    # Overflow warning threshold (%)
```

## Error Handling

### BufferEmptyError

Raised when attempting to get from empty buffer:
```python
try:
    items = buffer.get(count=100)
except BufferEmptyError:
    print("Buffer is empty")
```

### Overflow Protection

Buffer automatically handles overflow without raising exceptions:
- Returns `False` from `put()` when overflow occurs
- Logs warning messages
- Continues operating normally

## Testing

```bash
# Test FIFO overflow behavior
python backend/src/scripts/test_buffer_overflow.py

# Test with custom size
python backend/src/scripts/test_buffer_overflow.py --buffer-size 1000 --overflow-count 500
```

## Integration

### With Polling Engine (Feature 3)

BufferConsumer reads from DataQueue:
```python
from buffer.buffer_consumer import BufferConsumer
from polling.data_queue import DataQueue

data_queue = DataQueue(maxsize=10000)
circular_buffer = CircularBuffer(maxsize=10000)

consumer = BufferConsumer(data_queue, circular_buffer)
consumer.start()
```

### With Oracle Writer (Feature 4)

OracleWriter reads batches from buffer:
```python
from oracle_writer.writer import OracleWriter

writer = OracleWriter(
    circular_buffer=circular_buffer,
    connection_pool=connection_pool,
    metrics=metrics,
    csv_backup=csv_backup,
    batch_size=500,
    write_interval=0.5
)
writer.start()
```

## Monitoring

Buffer metrics are exposed via REST API:

```bash
# Get buffer status
curl http://localhost:8000/api/buffer/status
```

Response:
```json
{
  "current_size": 247,
  "max_size": 10000,
  "utilization_pct": 2.5,
  "overflow_count": 0,
  "overflow_rate_pct": 0.0
}
```

## Troubleshooting

### High Buffer Utilization

If utilization consistently > 80%:
1. Increase `BUFFER_MAX_SIZE`
2. Decrease polling frequency
3. Optimize Oracle write performance
4. Check for Oracle connectivity issues

### Frequent Overflows

If overflow rate > 1%:
1. Check Oracle writer is running
2. Verify Oracle database connectivity
3. Increase buffer capacity
4. Reduce data generation rate

### Memory Usage

Buffer memory usage = (item_size × capacity):
- Item size: ~100-200 bytes per BufferedTagValue
- 10,000 capacity = ~1-2 MB
- 100,000 capacity = ~10-20 MB

## See Also

- [Oracle Writer Module](../oracle_writer/README.md)
- [Polling Engine](../polling/README.md)
- [Quickstart Guide](../../../specs/004-buffer-oracle-writer/quickstart.md)
