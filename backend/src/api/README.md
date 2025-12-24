# Database Management REST API

**Feature 5**: Complete CRUD REST API for SCADA database configuration management

## Overview

This API provides comprehensive database management capabilities for the SCADA system, including:

- Production lines and processes
- PLC connection configuration and testing
- Tag management with CSV bulk import (3000+ tags in <30s)
- Polling group configuration (FIXED and HANDSHAKE modes)
- Robust error handling with user-friendly messages

## Quick Start

### Start the Server

```bash
cd backend
python -m uvicorn src.api.main:app --reload
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

## API Endpoints

### Lines

- `POST /api/lines` - Create new line
- `GET /api/lines` - List all lines (paginated)
- `GET /api/lines/{id}` - Get single line
- `PUT /api/lines/{id}` - Update line
- `DELETE /api/lines/{id}` - Delete line

### Processes

- `POST /api/processes` - Create new process
- `GET /api/processes` - List all processes (paginated, filterable by line_id)
- `GET /api/processes/{id}` - Get single process
- `PUT /api/processes/{id}` - Update process
- `DELETE /api/processes/{id}` - Delete process

### PLC Connections

- `POST /api/plc-connections` - Create new PLC connection
- `GET /api/plc-connections` - List all PLCs (paginated, filterable by process_id)
- `GET /api/plc-connections/{id}` - Get single PLC
- `POST /api/plc-connections/{id}/test` - Test PLC connectivity
- `PUT /api/plc-connections/{id}` - Update PLC connection
- `DELETE /api/plc-connections/{id}` - Delete PLC connection

### Tags

- `POST /api/tags` - Create new tag
- `GET /api/tags` - List all tags (paginated, filterable by plc_id, process_id, polling_group_id)
- `GET /api/tags/{id}` - Get single tag
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag
- `DELETE /api/tags/batch` - Batch delete tags
- `POST /api/tags/import-csv` - Import tags from CSV file

### Polling Groups

- `POST /api/polling-groups` - Create new polling group
- `GET /api/polling-groups` - List all groups (paginated, filterable by plc_id)
- `GET /api/polling-groups/{id}` - Get single group
- `GET /api/polling-groups/{id}/tags` - Get tags in group
- `PUT /api/polling-groups/{id}` - Update group
- `DELETE /api/polling-groups/{id}` - Delete group

## Usage Examples

### Create a Line

```bash
curl -X POST http://localhost:8000/api/lines \
  -H "Content-Type: application/json" \
  -d '{
    "line_code": "LINE001",
    "line_name": "Assembly Line 1",
    "location": "Factory A - Building 1",
    "enabled": true
  }'
```

Response:
```json
{
  "id": 1,
  "line_code": "LINE001",
  "line_name": "Assembly Line 1",
  "location": "Factory A - Building 1",
  "enabled": true,
  "created_at": "2025-11-02T10:30:00",
  "updated_at": "2025-11-02T10:30:00"
}
```

### Create a Process

```bash
curl -X POST http://localhost:8000/api/processes \
  -H "Content-Type: application/json" \
  -d '{
    "line_id": 1,
    "process_sequence": 1,
    "process_code": "KRCWO12ELOA101",
    "process_name": "Electroplating Process A",
    "equipment_type": "ELO",
    "enabled": true
  }'
```

**Process Code Format**: 14 characters matching `[A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}`
- Example: `KRCWO12ELOA101`
  - `KR`: Country code (2 chars)
  - `CWO`: Factory code (3 chars)
  - `12`: Line number (2 digits)
  - `ELO`: Equipment type (3 chars)
  - `A`: Category (1 char)
  - `101`: Sequence (3 digits)

### Create a PLC Connection

```bash
curl -X POST http://localhost:8000/api/plc-connections \
  -H "Content-Type: application/json" \
  -d '{
    "process_id": 1,
    "plc_code": "PLC001",
    "ip_address": "192.168.1.100",
    "port": 5000,
    "network_no": 0,
    "station_no": 0,
    "enabled": true
  }'
```

### Test PLC Connection

```bash
curl -X POST http://localhost:8000/api/plc-connections/1/test
```

Response:
```json
{
  "status": "success",
  "response_time_ms": 45,
  "error": null
}
```

### Create Tags (Single)

```bash
curl -X POST http://localhost:8000/api/tags \
  -H "Content-Type: application/json" \
  -d '{
    "plc_id": 1,
    "process_id": 1,
    "tag_address": "D100",
    "tag_name": "Temperature_Sensor_1",
    "tag_division": "Temperature",
    "data_type": "WORD",
    "unit": "°C",
    "scale": 0.1,
    "enabled": true
  }'
```

### Import Tags from CSV

```bash
curl -X POST http://localhost:8000/api/tags/import-csv \
  -F "file=@backend/data/sample_tags_1000.csv"
```

**CSV Format**:
```csv
PLC_CODE,PROCESS_CODE,TAG_ADDRESS,TAG_NAME,TAG_DIVISION,DATA_TYPE,UNIT,SCALE,MACHINE_CODE,ENABLED
PLC001,KRCWO12ELOA101,D100,Temp_Sensor_1,Temperature,WORD,°C,0.1,MACHINE_1,1
PLC001,KRCWO12ELOA101,D101,Pressure_Sensor_1,Pressure,WORD,bar,0.01,MACHINE_1,1
```

Response:
```json
{
  "success_count": 998,
  "failure_count": 2,
  "errors": [
    {"row": 15, "error": "PLC_CODE 'INVALID' not found"},
    {"row": 234, "error": "PROCESS_CODE 'INVALID' not found"}
  ]
}
```

### Create Polling Group (FIXED Mode)

```bash
curl -X POST http://localhost:8000/api/polling-groups \
  -H "Content-Type: application/json" \
  -d '{
    "group_name": "Temperature Sensors Group",
    "plc_id": 1,
    "mode": "FIXED",
    "interval_ms": 1000,
    "priority": "NORMAL",
    "enabled": true
  }'
```

### Create Polling Group (HANDSHAKE Mode)

```bash
curl -X POST http://localhost:8000/api/polling-groups \
  -H "Content-Type: application/json" \
  -d '{
    "group_name": "Critical Process Group",
    "plc_id": 1,
    "mode": "HANDSHAKE",
    "interval_ms": 500,
    "trigger_bit_address": "M100",
    "trigger_bit_offset": 0,
    "auto_reset_trigger": true,
    "priority": "HIGH",
    "enabled": true
  }'
```

## Pagination

All list endpoints support pagination:

```bash
# Get page 2 with 100 items per page
curl "http://localhost:8000/api/tags?page=2&limit=100"
```

Response format:
```json
{
  "items": [...],
  "total_count": 1500,
  "total_pages": 15,
  "current_page": 2,
  "page_size": 100
}
```

## Error Handling

The API provides user-friendly error messages with appropriate HTTP status codes.

### Validation Error (422)

Request with missing required field:
```json
{
  "error": "Validation Error",
  "detail": "field required",
  "field": "line_name"
}
```

### Resource Not Found (404)

```json
{
  "error": "Not Found",
  "detail": "Line with id 999 not found"
}
```

### Duplicate Resource (409)

```json
{
  "error": "Conflict",
  "detail": "Line with line_code 'LINE001' already exists"
}
```

### Foreign Key Error (400)

```json
{
  "error": "Bad Request",
  "detail": "line_id 999 not found"
}
```

### Invalid Process Code (400)

```json
{
  "error": "Validation Error",
  "detail": "process_code must match pattern: [A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3}"
}
```

### Invalid IP Address (400)

```json
{
  "error": "Validation Error",
  "detail": "'999.999.999.999' is not a valid IPv4 address"
}
```

## Testing

### Test Scripts

All API endpoints have dedicated test scripts:

```bash
# Test Lines API
python backend/src/scripts/test_lines_api.py

# Test Processes API
python backend/src/scripts/test_processes_api.py

# Test PLC Connections API
python backend/src/scripts/test_plc_connections_api.py

# Test Tags CSV Import
python backend/src/scripts/test_tags_csv_import.py

# Test Polling Groups API
python backend/src/scripts/test_polling_groups_api.py
```

### Generate Sample CSV Files

```bash
python backend/src/scripts/generate_sample_csv.py
```

This creates:
- `backend/data/sample_tags_1000.csv` - 1000 valid tags
- `backend/data/sample_tags_errors.csv` - 5 rows (2 valid, 3 errors)

## Performance

- **Single CRUD operations**: <200ms response time
- **CSV import (3000 tags)**: <30 seconds
- **Concurrent requests**: Supports up to 10 concurrent users

CSV import uses chunked batch inserts (1000 tags per chunk) for optimal performance.

## Data Model

### Foreign Key Relationships

```
Lines (1) ─→ (N) Processes
Processes (1) ─→ (N) PLC Connections
PLC Connections (1) ─→ (N) Tags
PLC Connections (1) ─→ (N) Polling Groups
Polling Groups (1) ─→ (N) Tags
```

### Constraints

- `line_code`: Unique across all lines
- `process_code`: Unique across all processes (14-char format)
- `plc_code`: Unique across all PLCs
- Foreign keys: Validated at application level before database insert
- Deletion: Cascade handled by SQLite foreign key constraints

## CORS Configuration

Configured for Next.js dev servers:
- `http://localhost:3000`
- `http://localhost:3001`

To add additional origins, update `backend/src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://your-frontend-url"],
    ...
)
```

## Architecture

### File Structure

```
backend/src/api/
├── main.py                      # FastAPI app with routers
├── models.py                    # Pydantic models
├── exceptions.py                # Custom exceptions and handlers
├── dependencies.py              # DB, pagination, logging
├── lines_routes.py              # Lines CRUD
├── processes_routes.py          # Processes CRUD
├── plc_connections_routes.py   # PLCs CRUD + testing
├── tags_routes.py               # Tags CRUD + CSV import
└── polling_groups_routes.py    # Polling groups CRUD
```

### Dependencies

- **FastAPI 0.104+**: Web framework
- **Pydantic 2.4+**: Data validation
- **pandas 2.1+**: CSV parsing
- **python-multipart**: File uploads
- **SQLite**: Database (via Feature 1 SQLiteManager)
- **MC3EClient**: PLC testing (via Feature 2)

## Logging

All CRUD operations are logged for auditing:

```
[2025-11-02T10:30:00] CREATE Line:1 - SUCCESS
[2025-11-02T10:30:15] UPDATE Process:5 - SUCCESS
[2025-11-02T10:30:30] DELETE PLC Connection:3 - FAILED - Error: FK constraint
```

## Security Considerations

- Input validation via Pydantic models
- SQL injection prevention via parameterized queries
- Foreign key validation prevents orphaned records
- File upload validation (CSV only)
- No authentication in current version (add if needed)

## Future Enhancements

- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Audit log API endpoint
- [ ] Batch operations for all resources
- [ ] Tag template management
- [ ] Backup/restore functionality
