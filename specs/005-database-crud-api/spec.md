# Feature Specification: Database Management REST API

**Feature Branch**: `005-database-crud-api`
**Created**: 2025-11-02
**Status**: Draft
**Input**: User description: "Feature 5"

## User Scenarios & Testing

### User Story 1 - Production Line and Process Configuration (Priority: P1)

Administrators need to create and manage production lines and processes.

**Why this priority**: Foundational MVP for hierarchy setup.

**Independent Test**: Create line via POST /api/lines, verify CRUD operations.

**Acceptance Scenarios**:

1. **Given** no lines, **When** creating line "LINE01", **Then** returns HTTP 201
2. **Given** line exists, **When** retrieving all, **Then** returns HTTP 200 with list
3. **Given** line exists, **When** creating process "KRCWO12ELOA101", **Then** validates and returns HTTP 201

---

### User Story 2 - PLC Connection Management (Priority: P2)

Administrators configure and test PLC connections.

**Why this priority**: Enables connection verification.

**Independent Test**: Create PLC, test connectivity.

**Acceptance Scenarios**:

1. **Given** process exists, **When** creating PLC, **Then** validates IPv4 and returns HTTP 201
2. **Given** PLC exists, **When** testing connection, **Then** returns connection status

---

### User Story 3 - Tag Configuration and CSV Import (Priority: P2)

Administrators configure tags and import from CSV.

**Why this priority**: Essential for 3000+ tags.

**Independent Test**: Create tags, upload CSV.

**Acceptance Scenarios**:

1. **Given** PLC exists, **When** creating tag, **Then** returns HTTP 201
2. **Given** CSV with 1000 tags, **When** uploading, **Then** creates all valid tags

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide POST /api/lines
- **FR-002**: System MUST provide GET /api/lines with pagination
- **FR-007**: System MUST provide POST /api/processes with validation
- **FR-013**: System MUST provide POST /api/plc-connections with IPv4 validation
- **FR-015**: System MUST provide POST /api/plc-connections/{id}/test
- **FR-020**: System MUST provide POST /api/tags
- **FR-021**: System MUST provide POST /api/tags/import-csv
- **FR-037**: All endpoints MUST use Pydantic models
- **FR-041**: Endpoints MUST respond within 200ms

### Key Entities

- **Line**: Production line with code, name
- **Process**: Manufacturing process with 14-char code
- **PLCConnection**: Mitsubishi PLC with IP, port
- **Tag**: Data point with address, type
- **PollingGroup**: Tag collection with polling config

## Success Criteria

- **SC-001**: Create hierarchy in under 5 minutes
- **SC-002**: CSV import 3000 tags in under 30 seconds
- **SC-003**: Single operations respond within 200ms
