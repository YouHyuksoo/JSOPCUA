# Feature Specification: Thread-Safe Buffer and Oracle DB Writer

**Feature Branch**: `004-buffer-oracle-writer`
**Created**: 2025-11-02
**Status**: Draft
**Input**: User description: "Python 백엔드 - 메모리 버퍼 및 Oracle DB Writer: Feature 3의 폴링 엔진에서 받은 태그 데이터를 메모리 버퍼(큐)에 저장하고, 독립적인 Writer 스레드가 Oracle DB에 일괄 삽입. 버퍼는 collections.deque로 구현 (최대 10,000개 항목). Writer는 0.5초마다 버퍼에서 데이터를 가져와 Oracle DB의 TAG_DATA 테이블에 INSERT (cx_Oracle 사용). 배치 삽입으로 성능 최적화 (한 번에 최대 500개 행). 버퍼 오버플로우 시 오래된 데이터 자동 삭제. Oracle 연결 실패 시 재시도 로직 (최대 3회). 데이터 형식: 태그명, 값, 타임스탬프, 품질(GOOD/BAD). 버퍼 상태 모니터링 API (현재 크기, 삽입/삭제 횟수). Oracle 연결 정보는 환경변수(.env)로 관리."

## User Scenarios & Testing

### User Story 1 - Reliable Data Persistence to Oracle (Priority: P1) 🎯 MVP

The system operations team needs all PLC data collected by the polling engine to be reliably stored in Oracle Database for long-term analysis, reporting, and compliance. Data must not be lost even during temporary database outages.

**Why this priority**: Core value delivery - without persistent storage, the polling engine data is ephemeral and useless for historical analysis, reporting, or compliance requirements.

**Independent Test**: Configure buffer and Oracle writer, start polling engine with 1 group, verify data appears in Oracle `tag_values` table within 2 seconds, stop Oracle temporarily and verify backup CSV files are created.

**Acceptance Scenarios**:

1. **Given** polling engine is collecting data, **When** buffer and Oracle writer are started, **Then** data appears in Oracle `tag_values` table within 2 seconds
2. **Given** Oracle writer is running, **When** 1,000 tag values are collected, **Then** all 1,000 values are successfully written to Oracle with zero data loss
3. **Given** Oracle database is temporarily unavailable, **When** data continues to be collected, **Then** failed writes are saved to backup CSV files and no data is lost
4. **Given** backup CSV files exist from previous failures, **When** Oracle database becomes available again, **Then** operator can manually recover data from CSV files

---

### User Story 2 - High-Throughput Batch Writing (Priority: P2)

The system must handle high data volumes (1,000+ tag values per second) without performance degradation or memory issues, using efficient batch writing to minimize database load.

**Why this priority**: Performance enabler - ensures system can scale to handle multiple polling groups (10 groups × 100 tags each = 1,000 values/second at 1-second intervals).

**Independent Test**: Configure 10 polling groups with 100 tags each polling at 1-second intervals, verify Oracle writer maintains average write latency under 2 seconds and buffer never exceeds 80% capacity.

**Acceptance Scenarios**:

1. **Given** system is receiving 1,000 tag values per second, **When** Oracle writer operates normally, **Then** average write latency remains under 2 seconds
2. **Given** multiple batches are queued for writing, **When** writer processes batches, **Then** batch sizes range between 100-1,000 items for optimal performance
3. **Given** buffer contains data, **When** 1 second elapses OR buffer reaches 500 items, **Then** writer triggers batch write to Oracle
4. **Given** sustained high load for 1 hour, **When** monitoring buffer utilization, **Then** buffer never exceeds 80% capacity

---

### User Story 3 - Buffer Overflow Protection (Priority: P2)

During extreme load or prolonged Oracle outages, the buffer must gracefully handle overflow by discarding oldest data (FIFO) to prevent memory exhaustion, while clearly alerting operators.

**Why this priority**: System stability - prevents out-of-memory crashes during abnormal conditions while maintaining operation for recent data.

**Independent Test**: Fill buffer to capacity (10,000 items), continue adding data, verify oldest items are discarded (FIFO), buffer size remains at max capacity, and overflow alerts are logged.

**Acceptance Scenarios**:

1. **Given** buffer is at maximum capacity (10,000 items), **When** new data arrives, **Then** oldest data is automatically discarded (FIFO) and buffer size remains constant
2. **Given** buffer overflow occurs, **When** data is discarded, **Then** system logs clear warning messages with overflow statistics
3. **Given** buffer overflow rate is tracked, **When** system operates normally, **Then** overflow rate remains under 1% over any 1-hour period
4. **Given** buffer is full and Oracle is unavailable, **When** operator checks monitoring dashboard, **Then** buffer status shows critical alert with overflow count

---

### User Story 4 - Real-Time Monitoring and Observability (Priority: P3)

Operations team needs real-time visibility into buffer health and Oracle writer performance through monitoring dashboard and metrics.

**Why this priority**: Operational excellence - enables proactive issue detection and troubleshooting, but system can function without it.

**Independent Test**: Access monitoring API endpoints and Admin UI dashboard, verify display of buffer utilization, write success/failure counts, average batch size, average latency, and backup file counts.

**Acceptance Scenarios**:

1. **Given** buffer and writer are operating, **When** operator accesses monitoring dashboard, **Then** display shows current buffer utilization percentage
2. **Given** writer has processed multiple batches, **When** operator checks metrics, **Then** display shows total successful writes, failed writes, and success rate percentage
3. **Given** writer is actively writing, **When** monitoring is queried, **Then** display shows rolling average batch size and average write latency over last 5 minutes
4. **Given** backup CSV files have been created, **When** operator checks monitoring, **Then** display shows count and total size of backup files

---

### Edge Cases

- What happens when buffer is full and Oracle is unavailable for extended period (>1 hour)?
- How does system handle Oracle connection pool exhaustion (all 5 connections in use)?
- What happens if Oracle write succeeds but acknowledgment is lost?
- How does system recover from partial batch write failure (e.g., 500 of 1,000 items written)?
- What happens when backup CSV file cannot be created (disk full, permission denied)?
- How does system handle very large tag values that exceed Oracle NUMBER precision?
- What happens during graceful shutdown when buffer still contains unwritten data?
- How does system handle Oracle schema changes (missing columns, renamed tables)?

## Requirements

### Functional Requirements

#### Thread-Safe Buffer

- **FR-001**: System MUST consume data from Feature 3's DataQueue continuously without blocking polling engine
- **FR-002**: System MUST store data in memory-based circular buffer with maximum capacity of 10,000 data points
- **FR-003**: System MUST support concurrent read (writer thread) and write (consumer thread) operations without data corruption
- **FR-004**: System MUST automatically discard oldest data (FIFO) when buffer reaches maximum capacity
- **FR-005**: System MUST track buffer utilization metrics (current size, max size, overflow count)

#### Oracle DB Writer

- **FR-006**: System MUST use python-oracledb library for Oracle database connectivity
- **FR-007**: System MUST maintain connection pool of 5 Oracle database connections
- **FR-008**: System MUST batch write up to 500 data points per INSERT operation using bulk insert
- **FR-009**: System MUST trigger batch write every 0.5 seconds OR when buffer reaches batch size limit (whichever occurs first)
- **FR-010**: System MUST retry failed INSERT operations up to 3 times with exponential backoff (1s, 2s, 4s)
- **FR-011**: System MUST save failed data to local CSV backup file after exhausting all retries
- **FR-012**: System MUST create timestamped CSV backup files in configured backup directory (format: `backup_YYYYMMDD_HHMMSS.csv`)

#### Oracle Database Schema

- **FR-013**: System MUST write data to Oracle table `TAG_DATA` with columns: `tag_name` (VARCHAR2(100)), `tag_value` (NUMBER or VARCHAR2), `timestamp` (TIMESTAMP), `quality` (VARCHAR2(20))
- **FR-014**: System MUST use composite primary key on (`tag_name`, `timestamp`) for duplicate prevention
- **FR-015**: System MUST leverage index on `timestamp` column for efficient time-range queries
- **FR-016**: System MUST handle duplicate key violations gracefully by logging and continuing with next batch

#### Data Quality

- **FR-017**: System MUST set `quality` field to 'GOOD' for successfully polled data or 'BAD' for polling errors
- **FR-018**: System MUST preserve original `timestamp` field from polling engine (data collection time)

#### Configuration

- **FR-020**: System MUST support configuration via environment variables or config file for: Oracle connection info (host, port, service_name, username, password), buffer max size, batch size range, write interval, retry count, backup file path

#### Monitoring & Observability

- **FR-021**: System MUST expose REST API endpoints for buffer status and writer metrics
- **FR-022**: System MUST track and report: current buffer size, total items inserted to buffer, total items removed from buffer, successful write count, failed write count
- **FR-023**: System MUST log all significant events: buffer overflow, Oracle connection failures, retry attempts, backup file creation, graceful shutdown with pending data count

### Key Entities

- **BufferedTagValue**: Represents a single tag value in buffer with fields: tag_name (tag identifier), tag_value (numeric or string value), timestamp (collection time), quality (GOOD/BAD), consumed from Feature 3's polling engine
- **WriteBatch**: Collection of BufferedTagValue items grouped for single Oracle INSERT operation, up to 500 items
- **BackupRecord**: Failed data saved to CSV with same fields as BufferedTagValue plus insertion_attempt_time
- **WriterMetrics**: Performance statistics including current_buffer_size, total_inserted, total_removed, successful_writes, failed_writes

## Success Criteria

### Measurable Outcomes

- **SC-001**: System successfully persists at least 1,000 tag values per second to Oracle Database with zero data loss
- **SC-002**: Average Oracle write latency remains under 2 seconds during normal operation (non-peak load)
- **SC-003**: Buffer overflow rate remains under 1% over any 1-hour observation period during normal operation
- **SC-004**: During Oracle outage, 100% of failed data is saved to backup CSV files with correct format for manual recovery
- **SC-005**: System handles sustained load of up to 3,491 tags with 1-second polling intervals for 24 hours without memory growth or performance degradation
- **SC-006**: Monitoring API responds within 500ms with current buffer and writer statistics
- **SC-007**: System achieves 99.9% write success rate under normal Oracle database availability (excluding planned outages)

## Out of Scope

- Automatic replay of backup CSV files to Oracle (manual recovery only)
- Data transformation or aggregation (raw tag values only)
- Real-time data streaming to external systems
- Multi-region or distributed Oracle write replication
- Historical data archival or partitioning strategies
- Oracle database schema creation or migration (assumes schema exists)
- Authentication and authorization for monitoring APIs (covered in future security feature)

## Assumptions

- Oracle Database is version 12c or higher with python-oracledb compatibility
- Oracle table `tag_values` exists with correct schema before feature deployment
- Network latency between application and Oracle database is under 50ms
- Feature 3 (Polling Engine) is operational and DataQueue is populated with PollingData objects
- Disk space for backup CSV files is adequate (estimated 1GB per day at 1,000 values/second)
- System clock is synchronized via NTP for accurate timestamps
- Python 3.11+ environment with sufficient memory for buffer (estimated 50MB for 10,000 items)

## Dependencies

- **Feature 3**: Polling Engine with DataQueue - must be implemented and operational
- **Oracle Database**: Production Oracle instance with `TAG_DATA` table created
- **python-oracledb**: Library availability and compatibility with target Oracle version (Thin mode, no Instant Client required)
- **Network**: Reliable connectivity between application server and Oracle database
