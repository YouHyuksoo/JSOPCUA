# JSScada Project Constitution

## Core Principles

### I. Autonomous Implementation
- **Default behavior**: `/speckit.implement` executes ALL tasks without stopping for approval
- **User intervention required ONLY when**:
  1. Critical technical decision with multiple valid approaches
  2. Spec is ambiguous or contradictory
  3. Blocking error that cannot be auto-resolved
  4. User explicitly requests approval gates
- **Progress tracking**: Use TodoWrite to show phase completion
- **Task completion**: Mark tasks complete immediately after finishing
- **Reasoning**: Maximize development velocity, reduce context switching

### II. Feature Independence
- Each feature is independently testable
- Features communicate via well-defined interfaces
- Feature branches follow naming: `###-short-name` (e.g., `005-database-crud-api`)
- Dependencies must be explicitly declared in `plan.md`

### III. API-First Design
- All backend features expose REST API or WebSocket endpoints
- OpenAPI/Swagger documentation is auto-generated
- Pydantic models for request/response validation
- Error responses follow consistent format (error, detail, field)

### IV. Database Integrity
- All foreign keys validated at application level before insert
- Unique constraints checked before database operations
- 14-character process code format enforced: `[A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}`
- IPv4 addresses validated using Python ipaddress module

### V. Performance Standards
- Single CRUD operations: <200ms response time
- Bulk operations: <30 seconds for 3000+ items
- CSV imports use chunked processing (1000 items/chunk)
- Connection pooling for all external resources (PLC, Oracle DB)

### VI. Error Handling
- User-friendly error messages with field-specific details
- HTTP status codes follow REST conventions (200, 201, 400, 404, 409, 422, 500)
- All CRUD operations logged for auditing
- Exceptions use custom classes with consistent formatting

### VII. Testing Requirements
- Test scripts provided for all major features
- Manual testing acceptable (pytest optional)
- Performance benchmarks validated via test scripts
- Integration testing with real PLC connections when available

## Technology Stack

### Backend (Python 3.11+)
- **Web Framework**: FastAPI 0.104+
- **Data Validation**: Pydantic 2.4+
- **Database**: SQLite (config), Oracle (time-series data)
- **PLC Communication**: pymcprotocol (MC 3E ASCII)
- **CSV Processing**: pandas 2.1+
- **File Uploads**: python-multipart

### Frontend (Next.js 14+)
- **Framework**: Next.js App Router
- **Language**: TypeScript 5.3+
- **Styling**: Tailwind CSS
- **State**: React hooks

### Communication
- **REST**: JSON over HTTP
- **Real-time**: WebSocket (1-second intervals)
- **CORS**: Configured for localhost:3000, localhost:3001

## Development Workflow

### SpecKit Workflow (Mandatory)
1. `/speckit.specify` - Feature specification (business requirements only)
2. `/speckit.plan` - Implementation plan (technical decisions)
3. `/speckit.tasks` - Task breakdown (dependency-ordered)
4. `/speckit.implement` - Autonomous execution (no approval gates)

### Code Organization
```
backend/src/
├── database/       # SQLiteManager, validators
├── plc/            # MC3EClient, PoolManager
├── polling/        # PollingEngine (Feature 3)
├── buffer/         # CircularBuffer, OracleWriter (Feature 4)
├── api/            # FastAPI routes, models, exceptions
└── scripts/        # Utilities, test scripts
```

### Branch Strategy
- `main`: Stable releases
- `###-feature-name`: Feature development
- Features merge to `main` after completion

## Quality Gates

### Before Starting Implementation
- [ ] All checklists in `specs/###-feature/checklists/` complete
- [ ] Dependencies verified (previous features complete)
- [ ] Technical approach approved in `plan.md`

### During Implementation
- [x] Tasks marked complete in `tasks.md` as they finish
- [x] TodoWrite used to track phase progress
- [x] No approval required between phases (autonomous execution)

### Before Merging to Main
- [ ] All tasks in `tasks.md` marked complete (100%)
- [ ] Test scripts validate functionality
- [ ] Performance benchmarks met
- [ ] README.md updated with feature status
- [ ] Completion summary document created

## Governance

- Constitution supersedes all other practices
- `/speckit.implement` runs autonomously unless critical issue
- Complexity violations must be justified in `plan.md`
- All features follow SpecKit workflow
- Breaking changes require README update

**Version**: 1.0.0 | **Ratified**: 2025-11-02 | **Last Amended**: 2025-11-02
