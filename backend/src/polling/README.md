# Polling Engine Module

Multi-threaded polling engine for PLC tag data collection.

## Overview

The polling engine provides automatic and on-demand data collection from PLCs using connection pooling. It supports two polling modes:

- **FIXED**: Automatic polling at fixed intervals (e.g., 1s, 5s, 10s)
- **HANDSHAKE**: Manual trigger via API for on-demand polling

## Architecture

```
┌─────────────────┐
│ PollingEngine   │
│  ├─ DataQueue   │──────> Thread-safe queue
│  └─ Threads     │
└────────┬────────┘
         │
         ├──> FixedPollingThread (FIXED mode)
         │      └─> Polls at fixed intervals
         │
         └──> HandshakePollingThread (HANDSHAKE mode)
                └─> Waits for manual trigger
```

## Usage

### Initialization

```python
from polling.polling_engine import PollingEngine
from plc.pool_manager import PoolManager

# Initialize
pool_manager = PoolManager("backend/config/scada.db")
engine = PollingEngine("backend/config/scada.db", pool_manager)
engine.initialize()
```

### Start/Stop Polling

```python
# Start all groups
engine.start_all()

# Start specific group
engine.start_group("LINE1_PROCESS1")

# Stop specific group
engine.stop_group("LINE1_PROCESS1")

# Stop all groups
engine.stop_all()
```

### Manual Trigger (HANDSHAKE mode)

```python
result = engine.trigger_handshake("ORDER_START")
if result['success']:
    print(f"Poll triggered: {result['tag_count']} tags")
```

### Status Monitoring

```python
status = engine.get_status_all()
for s in status:
    print(f"{s['group_name']}: {s['state']} - {s['total_polls']} polls")

queue_size = engine.get_queue_size()
```

## Components

- **polling_engine.py**: Main orchestrator
- **polling_thread.py**: Base thread class
- **fixed_polling_thread.py**: FIXED mode implementation
- **handshake_polling_thread.py**: HANDSHAKE mode implementation
- **data_queue.py**: Thread-safe queue wrapper
- **models.py**: Data models
- **exceptions.py**: Custom exceptions

## Performance

- Supports 10 concurrent polling groups
- Each group supports 100+ tags
- FIXED mode interval accuracy: ±10%
- Status API response: <200ms
- Graceful shutdown: <5s

## Error Handling

- Automatic retry on PLC errors
- Detailed error logging
- Thread isolation (one group's errors don't affect others)
- Resource leak prevention

## Testing

```bash
# Test FIXED mode
python backend/src/scripts/test_polling_fixed.py

# Test HANDSHAKE mode
python backend/src/scripts/test_polling_handshake.py

# Test engine control
python backend/src/scripts/test_polling_engine.py

# Test error recovery
python backend/src/scripts/test_error_recovery.py
```
