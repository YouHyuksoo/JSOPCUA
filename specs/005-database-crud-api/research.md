# Research: Database Management REST API

**Feature**: 005-database-crud-api
**Date**: 2025-11-02

## Decision 1: FastAPI Router Organization

**Decision**: Create separate router modules per resource (lines_routes.py, processes_routes.py, etc.)

**Rationale**:
- Each resource has 5-7 endpoints - separate files prevent single file from becoming >1000 lines
- Enables parallel development of different resources
- Follows FastAPI best practices for large applications
- Matches existing pattern in Feature 3 (polling_routes.py, websocket_handler.py)

**Alternatives Considered**:
- Single routes.py file: Rejected due to complexity (29 endpoints = ~800-1000 lines)
- Grouped by CRUD operation: Rejected as it scatters related endpoints

## Decision 2: CSV Import Strategy

**Decision**: Use pandas for parsing + chunked batch inserts (1000 tags per chunk)

**Rationale**:
- pandas handles encoding detection (UTF-8/CP949) automatically
- Chunking prevents database lock timeouts for large imports
- Allows partial success reporting if some chunks fail
- Transaction per chunk balances atomicity and performance

**Alternatives Considered**:
- Python csv module: Rejected due to manual encoding handling
- Single transaction for all tags: Rejected due to lock timeout risk with 3000+ tags
- Row-by-row inserts: Rejected due to poor performance (30s target unreachable)

## Decision 3: Pydantic Model Hierarchy

**Decision**: Base models (LineBase, ProcessBase, etc.) + specialized models (LineCreate, LineResponse, LineUpdate)

**Rationale**:
- Avoids duplication of field definitions
- Clear separation: Create (required fields), Update (optional fields), Response (includes computed fields like timestamps)
- Type safety for request/response contracts
- Automatic OpenAPI schema generation

**Alternatives Considered**:
- Single model per resource: Rejected as requires all fields optional for updates
- No base models: Rejected due to duplication across Create/Update/Response

## Decision 4: Foreign Key Validation

**Decision**: Application-level validation in route handlers before database operation

**Rationale**:
- Enables custom error messages ("process_id 999 not found" vs "FOREIGN KEY constraint failed")
- Allows checking existence before complex operations (e.g., CSV import)
- No performance impact - queries use indexed columns
- Database-level constraints remain as safety net

**Alternatives Considered**:
- Database-only validation: Rejected due to cryptic error messages
- Pydantic validators: Rejected as validators don't have database access

## Decision 5: PLC Connection Testing

**Decision**: Reuse Feature 2's MC3EClient in sync endpoint with 5s timeout

**Rationale**:
- No code duplication - MC3EClient already handles connection logic
- 5s timeout prevents blocking other requests
- Sync endpoint acceptable as tests are infrequent admin actions
- Return structured result: {status: "success"|"failed", response_time_ms: int, error: str}

**Alternatives Considered**:
- Async test with background task: Rejected as adds complexity without clear benefit
- Reimplemented test logic: Rejected due to duplication

## Implementation Notes

- All routers will be registered in main.py with prefix /api
- CORS already configured in main.py for localhost:3000 and localhost:3001
- Use FastAPI's HTTPException for error responses (status codes from spec)
- Database sessions via dependency injection pattern
- Logging to backend/logs/api.log (existing log configuration)
