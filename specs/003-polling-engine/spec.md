# Feature Specification: Multi-threaded Polling Engine

**Feature Branch**: `003-polling-engine`
**Created**: 2025-11-01
**Status**: Draft
**Input**: User description: "Python 백엔드 - 멀티 스레드 폴링 엔진 (FIXED/HANDSHAKE 모드): Feature 2의 PoolManager를 사용하여 PLC 태그를 주기적으로 읽는 멀티 스레드 폴링 엔진 구현. FIXED 모드는 고정 주기(예: 1초, 5초)로 자동 폴링. HANDSHAKE 모드는 외부 트리거(REST API 호출)로 수동 폴링. SQLite의 polling_groups 테이블에서 폴링 설정 로드(그룹명, 모드, 주기, 태그 목록). 각 폴링 그룹은 독립적인 스레드에서 실행. 스레드 안전한 큐에 읽은 데이터 저장(Feature 4로 전달). 폴링 시작/중지/상태 조회 API. 에러 발생 시 로깅 및 재시도. 성능: 최대 10개 폴링 그룹 동시 실행, 그룹당 최소 100개 태그 지원."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Fixed-Interval Data Collection (Priority: P1)

System operators need PLC tag data to be collected automatically at regular intervals without manual intervention, ensuring continuous monitoring of production equipment.

**Why this priority**: This is the core MVP functionality. Without automatic data collection, the SCADA system cannot provide real-time monitoring. This story delivers immediate value by enabling continuous equipment monitoring.

**Independent Test**: Can be fully tested by configuring one polling group in FIXED mode, starting the engine, and verifying that tag values are collected at the specified interval (e.g., every 1 second). Success is confirmed when data appears in the queue at consistent intervals.

**Acceptance Scenarios**:

1. **Given** a polling group configured with FIXED mode and 1-second interval, **When** the polling engine starts, **Then** the system reads all tags in that group every 1 second and stores results in the queue
2. **Given** multiple polling groups with different intervals (1s, 5s, 10s), **When** the engine runs, **Then** each group polls independently at its configured interval without interference
3. **Given** a polling group with 100 tags, **When** polling executes, **Then** all 100 tag values are read in a single polling cycle using batch operations
4. **Given** the engine is running, **When** a polling cycle completes, **Then** the timestamp, group name, and all tag values are stored in the thread-safe queue

---

### User Story 2 - Manual On-Demand Data Collection (Priority: P2)

System operators need to trigger data collection on-demand for specific polling groups when performing equipment diagnostics or responding to alarms, without waiting for the next fixed interval.

**Why this priority**: Enhances operational flexibility by allowing manual data collection during critical situations. While not essential for basic monitoring (P1 provides this), it significantly improves troubleshooting capabilities.

**Independent Test**: Can be tested independently by configuring a polling group in HANDSHAKE mode, calling the trigger API endpoint for that group, and verifying that data collection occurs immediately regardless of any fixed schedule. No FIXED mode groups are required for this test.

**Acceptance Scenarios**:

1. **Given** a polling group configured in HANDSHAKE mode, **When** an operator calls the trigger API for that group, **Then** the system immediately reads all tags in that group once and stores results in the queue
2. **Given** multiple HANDSHAKE groups, **When** trigger API is called for one specific group, **Then** only that group executes polling, other groups remain idle
3. **Given** a HANDSHAKE group is already executing a poll, **When** another trigger request arrives for the same group, **Then** the system queues the request and executes it after the current poll completes
4. **Given** the trigger API is called, **When** polling completes, **Then** the API response includes execution status (success/failure) and number of tags read

---

### User Story 3 - Polling Engine Control and Monitoring (Priority: P2)

System administrators need to start, stop, and monitor the status of polling groups to manage system resources and respond to maintenance windows or equipment downtime.

**Why this priority**: Essential for operational control but not required for basic data collection. Operators can deploy P1 functionality and let it run continuously, but P3 provides necessary control for real-world operations.

**Independent Test**: Can be tested by starting individual polling groups via API, checking their status (running/stopped, last poll time, success/error count), and stopping them. Test confirms control API works without requiring data consumption (Feature 4).

**Acceptance Scenarios**:

1. **Given** polling groups are configured in the database, **When** administrator calls the start API for a specific group, **Then** that group begins polling according to its mode (FIXED or HANDSHAKE)
2. **Given** a polling group is running, **When** administrator calls the stop API for that group, **Then** the group's thread terminates gracefully after completing the current polling cycle
3. **Given** multiple polling groups are running, **When** administrator queries status API, **Then** the system returns status for all groups including: name, mode, state (running/stopped), last poll time, success count, error count
4. **Given** 10 polling groups are running simultaneously, **When** status is queried, **Then** response includes resource utilization metrics (active threads, queue size)
5. **Given** the engine is running, **When** administrator calls stop-all API, **Then** all polling groups terminate gracefully within 5 seconds

---

### User Story 4 - Error Recovery and Resilience (Priority: P3)

The system must continue operating when PLC connection errors occur, automatically retrying failed polls and logging errors without stopping the entire polling engine.

**Why this priority**: Improves system reliability and reduces manual intervention. While P1 can collect data successfully under normal conditions, P4 ensures the system gracefully handles real-world network issues and equipment failures.

**Independent Test**: Can be tested by simulating PLC connection failures (disconnect network, stop PLC simulator) and verifying that: (1) the polling group logs the error, (2) continues attempting polls at the next interval, (3) automatically recovers when connection is restored, (4) other polling groups continue unaffected.

**Acceptance Scenarios**:

1. **Given** a polling group is running, **When** PLC connection fails during a poll, **Then** the system logs the error with timestamp and group name, and retries at the next scheduled interval (FIXED mode) or next trigger (HANDSHAKE mode)
2. **Given** a PLC connection failure occurred, **When** the connection is restored, **Then** the next polling cycle succeeds automatically without manual intervention
3. **Given** one polling group encounters continuous errors, **When** other polling groups execute, **Then** they continue operating normally without impact
4. **Given** a polling cycle fails, **When** the error is logged, **Then** the log includes: timestamp, polling group name, error type, affected tag count, and retry strategy
5. **Given** connection pool errors occur (all connections busy, timeout), **When** polling executes, **Then** the system waits for available connection with timeout (up to 10 seconds) before marking poll as failed

---

### Edge Cases

- What happens when a polling group is stopped while a polling cycle is in progress? (System must complete the current cycle gracefully before terminating the thread)
- What happens when the database is updated with new tags for an active polling group? (System continues with the original tag list until group is restarted)
- How does system handle when 10 polling groups are already running and an 11th start request arrives? (System rejects the request with error message indicating maximum capacity reached)
- What happens when queue capacity is full and new polling data arrives? (System logs a warning and either blocks until space available or drops oldest data based on configured policy - default: block with 30-second timeout)
- How does system handle clock changes or system time adjustments during fixed-interval polling? (Polling intervals are based on elapsed time, not wall clock, so system adjusts automatically)
- What happens when multiple HANDSHAKE trigger requests arrive for the same group simultaneously? (Requests are queued and executed sequentially, with duplicate requests within 1 second window being deduplicated)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load polling group configurations from SQLite database polling_groups table including: group name, polling mode (FIXED/HANDSHAKE), interval (for FIXED mode), and associated tag list
- **FR-002**: System MUST support two polling modes: FIXED (automatic polling at specified interval) and HANDSHAKE (manual trigger via API)
- **FR-003**: System MUST execute each polling group in an independent thread, allowing concurrent operation of multiple groups
- **FR-004**: System MUST use the PoolManager from Feature 2 to read PLC tag values, leveraging connection pooling and batch read operations
- **FR-005**: System MUST store collected data in a thread-safe queue structure with timestamp, polling group name, and tag values
- **FR-006**: System MUST provide REST API endpoints to: start polling group, stop polling group, trigger HANDSHAKE poll, query status of all groups
- **FR-007**: System MUST support at least 10 concurrent polling groups running simultaneously
- **FR-008**: System MUST support at least 100 tags per polling group
- **FR-009**: System MUST log all polling operations including: poll start, poll completion, success/failure status, error details
- **FR-010**: System MUST handle PLC connection errors by logging the error and retrying at the next scheduled interval (FIXED) or next trigger (HANDSHAKE)
- **FR-011**: System MUST terminate polling threads gracefully when stop command is issued, completing current polling cycle before shutdown
- **FR-012**: System MUST prevent resource leaks by ensuring all threads are properly cleaned up on shutdown
- **FR-013**: System MUST deduplicate multiple HANDSHAKE trigger requests for the same group within a 1-second window
- **FR-014**: System MUST reject start requests when maximum polling group capacity (10 groups) is reached
- **FR-015**: System MUST provide status information including: group state (running/stopped), last poll timestamp, total success count, total error count, current queue size

### Key Entities

- **Polling Group**: Represents a collection of PLC tags that are polled together. Attributes include: unique name, polling mode (FIXED/HANDSHAKE), interval (for FIXED mode), list of tag IDs, associated PLC connection, current state (running/stopped), last poll timestamp, success/error counters.

- **Polling Data**: Represents the result of a single polling cycle. Attributes include: timestamp, polling group name, list of tag-value pairs (tag ID, value, quality/status), polling duration.

- **Polling Thread**: Represents the execution context for a polling group. Attributes include: thread ID, associated polling group, state (active/stopping/stopped), last execution time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully polls 10 concurrent polling groups without thread conflicts or data corruption
- **SC-002**: Each polling group handles at least 100 tags with polling cycle completion time under 2 seconds (including PLC communication)
- **SC-003**: FIXED mode polling maintains interval accuracy within ±10% of configured interval (e.g., 1-second interval completes between 0.9-1.1 seconds)
- **SC-004**: HANDSHAKE mode trigger API responds within 500ms, with actual polling execution starting within 1 second
- **SC-005**: System recovers automatically from PLC connection failures within one polling interval after connection restoration
- **SC-006**: Polling engine operates continuously for 24 hours without thread deadlocks, memory leaks, or unexpected terminations
- **SC-007**: Status API returns current state of all polling groups within 200ms
- **SC-008**: System handles start/stop commands for polling groups within 5 seconds, including graceful thread termination
- **SC-009**: Error rate during normal operation (with stable PLC connections) is below 0.1% of total polling cycles
- **SC-010**: Thread-safe queue operations complete without data loss when multiple polling groups write concurrently
