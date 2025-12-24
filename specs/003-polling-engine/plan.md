# Implementation Plan: Multi-threaded Polling Engine

**Branch**: `003-polling-engine` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-polling-engine/spec.md`

## Summary

Multi-threaded polling engine that periodically reads PLC tags using Feature 2's PoolManager. Supports two modes: FIXED (automatic polling at fixed intervals) and HANDSHAKE (manual trigger via API). Each polling group runs in an independent thread, storing collected data in a thread-safe queue for downstream processing. Includes polling control APIs (start/stop/status) and error recovery with automatic retry. Performance target: 10 concurrent polling groups, 100+ tags per group.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- threading (Python stdlib - multi-threading support)
- queue (Python stdlib - thread-safe queue)
- Feature 2's PoolManager (PLC connection pooling and batch read)
- time (Python stdlib - timing and intervals)

**Storage**: SQLite (Feature 1's polling_groups and tags tables)

**Testing**: pytest, pytest-timeout, threading.Event for thread testing, unittest.mock

**Target Platform**: Linux/Windows server

**Project Type**: Web application (backend only for this feature)

**Performance Goals**:
- FIXED mode interval accuracy: ±10% of configured interval
- HANDSHAKE mode trigger response: <500ms API response, <1s polling start
- Polling cycle completion: <2s for 100 tags (including PLC communication)
- Status API response: <200ms

**Constraints**:
- Maximum 10 concurrent polling groups
- Thread-safe queue operations (no data loss/corruption)
- Graceful thread termination: <5s after stop command
- Queue capacity: default 10,000 items (configurable)

**Scale/Scope**:
- Support 10 concurrent polling groups
- Each group: 100+ tags
- Continuous operation: 24 hours without memory leaks
- Error rate: <0.1% during normal operation

## Constitution Check

*Constitution file is in template state, therefore no project-specific principles exist. Skipping constitution validation.*

**Status**: ✅ PASS - No constitution constraints defined

## Project Structure

### Documentation (this feature)

```text
specs/003-polling-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── polling/                    # NEW (Feature 3)
│   │   ├── __init__.py
│   │   ├── models.py               # Polling data models (PollingGroup, PollingData, PollingStatus)
│   │   ├── polling_thread.py       # PollingThread class (base thread implementation)
│   │   ├── fixed_polling_thread.py # FIXED mode thread (automatic intervals)
│   │   ├── handshake_polling_thread.py # HANDSHAKE mode thread (manual trigger)
│   │   ├── polling_engine.py       # PollingEngine orchestrator (manages all threads)
│   │   ├── data_queue.py           # Thread-safe queue wrapper with monitoring
│   │   └── exceptions.py           # Polling-specific exceptions
│   ├── plc/                        # EXISTING (Feature 2)
│   │   ├── pool_manager.py         # Used by polling threads
│   │   └── ...
│   ├── database/                   # EXISTING (Feature 1)
│   │   ├── sqlite_manager.py       # Used to load polling group configs
│   │   └── ...
│   └── scripts/
│       ├── test_polling_fixed.py   # NEW: Test FIXED mode polling
│       ├── test_polling_handshake.py # NEW: Test HANDSHAKE mode polling
│       └── test_polling_engine.py  # NEW: Test engine control
├── tests/
│   ├── unit/
│   │   ├── test_polling_thread.py
│   │   ├── test_fixed_polling_thread.py
│   │   ├── test_handshake_polling_thread.py
│   │   ├── test_polling_engine.py
│   │   └── test_data_queue.py
│   └── integration/
│       ├── test_polling_integration.py  # Multi-group concurrent test
│       └── test_polling_resilience.py   # Error recovery test
├── config/                         # EXISTING (Feature 1)
│   └── scada.db                    # polling_groups and tags tables
└── requirements.txt                # No new dependencies (using stdlib)
```

**Structure Decision**: Continues web application structure from Features 1 & 2. Adds new `backend/src/polling/` package to encapsulate polling engine logic. Reuses Feature 2's PoolManager for PLC communication and Feature 1's SQLite database for configuration. All dependencies are Python stdlib except for existing dependencies.

## Complexity Tracking

*No constitution constraints defined, therefore no violations to track.*

