# Research: 통합 테스트 및 배포 준비

**Feature**: 008-integration-test-deployment  
**Date**: 2025-11-04

## Phase 0: Technical Research

### 1. E2E Testing Framework Selection

**Decision**: pytest 7.4+ with pytest-asyncio

**Rationale**:
- Already specified in project constitution (Section VII)
- Excellent async support for testing WebSocket connections
- Rich plugin ecosystem (pytest-asyncio, pytest-timeout, pytest-xdist)
- Clean fixture-based test organization
- HTML report generation via pytest-html

**Alternatives Considered**:
- **unittest** (Python stdlib): Rejected - Verbose syntax, limited async support
- **nose2**: Rejected - Deprecated, less active development

**Implementation Notes**:
- Use pytest.mark.asyncio for async tests
- Fixture-based setup/teardown for PLC mock server
- pytest-timeout to enforce 5-minute E2E test limit
- HTML reports via pytest --html=report.html

### 2. Mock PLC Server Implementation

**Decision**: Custom Python socket server simulating MC 3E ASCII protocol

**Rationale**:
- Full control over test scenarios (normal, timeout, malformed responses)
- No external dependencies beyond Python stdlib
- Can simulate multiple PLC instances on different ports
- Reusable across all integration tests

**Alternatives Considered**:
- **tcpdump replay**: Rejected - Limited to pre-recorded scenarios
- **Real PLC**: Rejected - Not always available, hard to simulate errors

**Implementation Notes**:
- Server listens on configurable ports (5000-5010)
- Handles MC 3E ASCII read requests (batch reads)
- Returns configurable responses (success, timeout, error codes)
- Thread-safe for concurrent connections

### 3. Docker Best Practices

**Decision**: Multi-stage builds with Alpine base images

**Rationale**:
- Multi-stage builds: Separate build and runtime stages
- Alpine Linux: Minimal base image (5MB vs 100MB Ubuntu)
- Layer caching: Optimize build time
- Non-root user: Security best practice

**Expected Image Sizes**:
- Backend: 300-400MB (Python + dependencies)
- Frontend: 150-180MB (Node.js + Next.js)

### 4. Load Testing Tool Selection

**Decision**: Locust 2.15+ (Python-based load testing)

**Rationale**:
- Python-based: Easy integration with existing backend
- WebSocket support: Can test Monitor UI connections
- Real-time web UI: Monitor load test progress
- Scriptable: Write test scenarios in Python

**Alternatives Considered**:
- **Apache JMeter**: Rejected - Java-based, heavier
- **K6**: Rejected - JavaScript test scripts, steeper learning curve

### 5. Memory Profiling Approach

**Decision**: memory_profiler 0.61+ + psutil for long-running monitoring

**Rationale**:
- memory_profiler: Line-by-line memory usage analysis
- psutil: System-wide resource monitoring
- Continuous monitoring: Track memory over 8-hour period
- CSV output: Export metrics for trend analysis

**Alternatives Considered**:
- **tracemalloc**: Rejected - Less detailed
- **guppy3**: Rejected - Python 2 legacy, unmaintained

## Summary of Decisions

| Research Area | Decision | Key Benefit |
|---------------|----------|-------------|
| E2E Testing | pytest 7.4+ | Async support, plugins, constitution compliance |
| Mock PLC | Custom Python socket server | Full control, no external deps |
| Docker Build | Multi-stage + Alpine | Minimal image size |
| Load Testing | Locust 2.15+ | Python-friendly, WebSocket support |
| Memory Profiling | memory_profiler + psutil | Line-by-line analysis, long-running monitoring |

## Next Steps

All research questions resolved. No NEEDS CLARIFICATION remaining.

Proceed to **Phase 1: Design & Contracts**.
