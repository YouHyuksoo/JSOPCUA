# Implementation Plan: Memory Buffer and Oracle DB Writer

**Branch**: `004-buffer-oracle-writer` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-buffer-oracle-writer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a thread-safe memory buffer and Oracle database writer that consumes tag data from Feature 3's polling engine, buffers data in memory (max 10,000 items using collections.deque), and periodically writes to Oracle DB in batches (up to 500 rows every 0.5 seconds). System includes automatic retry logic (up to 3 attempts), CSV backup for failed writes, FIFO overflow handling, and REST API for monitoring buffer status and writer metrics.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- python-oracledb (Oracle database connectivity - Thin mode, no Instant Client)
- collections.deque (thread-safe circular buffer)
- threading (concurrent writer thread)
- FastAPI (monitoring REST API - from Feature 3)
- python-dotenv (environment variable management)
**Storage**: Oracle Database 12c+ (TAG_DATA table), Local CSV files (backup)
**Testing**: pytest, pytest-cov
**Target Platform**: Linux/Windows server (same as polling engine)
**Project Type**: Web application (backend extends existing backend/)
**Performance Goals**:
- 1,000+ tag values per second throughput
- <2 seconds average write latency
- 0.5 second write interval
- Up to 500 rows per batch insert
**Constraints**:
- <50MB memory for 10,000 item buffer
- <1% buffer overflow rate during normal operation
- 99.9% write success rate
- Thread-safe concurrent operations
**Scale/Scope**:
- 10,000 buffer capacity
- 3,491 tags maximum (from Feature 1)
- 5 concurrent Oracle connections (connection pool)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS - No project-specific constitution defined yet. Using general software engineering best practices.

**Initial Evaluation** (before Phase 0):
- Code organization: Follows existing backend/ structure from Features 1-3
- Testing approach: pytest with contract/integration/unit tests (consistent with project)
- Dependency management: Minimal new dependencies (python-oracledb only major addition)
- Thread safety: Required for concurrent buffer access - justified by functional requirements
- Simplicity: Straightforward buffer + writer pattern, no over-engineering

**Re-evaluation** (after Phase 1 design):
- ✅ **Architecture**: Modular design with clear separation (buffer/, oracle_writer/)
- ✅ **Technology choices**: python-oracledb Thin mode (no Instant Client dependency - simpler deployment)
- ✅ **Data model**: Clean entity relationships, appropriate Oracle schema design
- ✅ **API contracts**: RESTful monitoring endpoints, well-documented OpenAPI spec
- ✅ **Integration**: Seamless integration with Feature 3 via shared DataQueue
- ✅ **Error handling**: Comprehensive retry logic and CSV backup strategy
- ✅ **Testing strategy**: Contract/integration/unit test structure defined

**No constitution violations identified.** All design decisions align with simplicity, maintainability, and project consistency.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── buffer/                    # NEW: Memory buffer module
│   │   ├── __init__.py
│   │   ├── models.py             # BufferedTagValue, BufferMetrics
│   │   ├── exceptions.py         # BufferOverflowError, BufferError
│   │   ├── circular_buffer.py    # Thread-safe deque-based buffer
│   │   └── buffer_consumer.py    # Consumer from Feature 3's DataQueue
│   ├── oracle_writer/            # NEW: Oracle DB writer module
│   │   ├── __init__.py
│   │   ├── config.py             # Oracle connection config from .env
│   │   ├── connection_pool.py    # cx_Oracle connection pool (5 connections)
│   │   ├── writer.py             # Batch writer with retry logic
│   │   ├── backup.py             # CSV backup for failed writes
│   │   └── metrics.py            # WriterMetrics tracking
│   ├── api/                      # EXTEND: Add monitoring endpoints
│   │   ├── main.py              # Add buffer/writer status routes
│   │   └── buffer_routes.py     # NEW: Buffer monitoring API
│   ├── polling/                  # FROM FEATURE 3: Provides DataQueue
│   │   └── data_queue.py        # Shared queue between polling and buffer
│   └── scripts/
│       ├── test_oracle_connection.py  # NEW: Oracle connectivity test
│       ├── test_end_to_end.py        # NEW: Full pipeline test
│       └── start_buffer_writer.py    # NEW: Main entry point
├── tests/
│   ├── contract/
│   │   └── test_oracle_schema.py     # NEW: TAG_DATA table contract
│   ├── integration/
│   │   ├── test_buffer_writer_integration.py  # NEW
│   │   └── test_backup_recovery.py           # NEW
│   └── unit/
│       ├── test_circular_buffer.py           # NEW
│       ├── test_connection_pool.py           # NEW
│       └── test_csv_backup.py                # NEW
├── config/
│   └── scada.db                  # FROM FEATURE 1: SQLite database
├── .env.example                  # EXTEND: Add Oracle connection vars
└── requirements.txt              # EXTEND: Add python-oracledb

frontend-admin/                    # FROM FEATURE 3: Admin UI
└── [monitoring dashboard will be extended in future feature]
```

**Structure Decision**: Web application structure (Option 2). This feature extends the existing `backend/` directory with two new modules (`buffer/` and `oracle_writer/`) and adds monitoring endpoints to the existing FastAPI app. Frontend monitoring UI integration is out of scope (manual API access only).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations. All design decisions align with best practices:
- Thread-safe buffer required by concurrent access (polling engine writes, writer thread reads)
- Connection pooling is standard practice for database performance
- Retry logic and backup are reliability requirements from spec
- Modular structure (buffer/, oracle_writer/) follows separation of concerns
