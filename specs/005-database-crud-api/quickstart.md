# Quickstart: Database Management REST API

**Feature**: 005-database-crud-api

## Prerequisites

- Backend API running at http://localhost:8000
- SQLite database initialized (Feature 1)

## Example 1: Create Complete Hierarchy

```bash
# 1. Create line
curl -X POST http://localhost:8000/api/lines \
  -H "Content-Type: application/json" \
  -d '{
    "line_code": "LINE01",
    "line_name": "TUB 가공 라인",
    "location": "창원 공장",
    "enabled": true
  }'
# Response: {"id": 1, "line_code": "LINE01", ...}

# 2. Create process under line
curl -X POST http://localhost:8000/api/processes \
  -H "Content-Type: application/json" \
  -d '{
    "line_id": 1,
    "process_sequence": 1,
    "process_code": "KRCWO12ELOA101",
    "process_name": "Upper Loading",
    "equipment_type": "LOA",
    "enabled": true
  }'
# Response: {"id": 1, "process_code": "KRCWO12ELOA101", ...}

# 3. Create PLC connection
curl -X POST http://localhost:8000/api/plc-connections \
  -H "Content-Type: application/json" \
  -d '{
    "process_id": 1,
    "plc_code": "PLC01",
    "ip_address": "192.168.1.10",
    "port": 5000,
    "network_no": 0,
    "station_no": 0,
    "enabled": true
  }'
# Response: {"id": 1, "plc_code": "PLC01", ...}

# 4. Test PLC connection
curl -X POST http://localhost:8000/api/plc-connections/1/test
# Response: {"status": "success", "response_time_ms": 45, "error": null}

# 5. Create tag
curl -X POST http://localhost:8000/api/tags \
  -H "Content-Type: application/json" \
  -d '{
    "plc_id": 1,
    "process_id": 1,
    "tag_address": "W150",
    "tag_name": "온도센서1",
    "data_type": "WORD",
    "unit": "℃",
    "scale": 1.0,
    "enabled": true
  }'
# Response: {"id": 1, "tag_address": "W150", ...}
```

## Example 2: CSV Bulk Import

```bash
# Prepare CSV file (tags.csv):
# PLC_CODE,TAG_ADDRESS,TAG_NAME,TAG_DIVISION,DATA_TYPE,UNIT,SCALE,MACHINE_CODE
# PLC01,W150,온도센서1,온도,WORD,℃,1.0,KRCWO12ELOA101
# PLC01,W151,압력센서1,압력,WORD,bar,0.1,KRCWO12ELOA101

# Import CSV
curl -X POST http://localhost:8000/api/tags/import-csv \
  -F "file=@tags.csv"
# Response: {"success_count": 2, "failure_count": 0, "errors": []}
```

## Example 3: Query with Pagination

```bash
# Get all tags with pagination
curl "http://localhost:8000/api/tags?page=1&limit=50"
# Response: {
#   "items": [...],
#   "total_count": 3491,
#   "total_pages": 70,
#   "current_page": 1,
#   "page_size": 50
# }

# Filter tags by PLC
curl "http://localhost:8000/api/tags?plc_id=1&enabled=true"
```

## Example 4: Update and Delete

```bash
# Update line
curl -X PUT http://localhost:8000/api/lines/1 \
  -H "Content-Type: application/json" \
  -d '{"line_name": "TUB 가공 라인 (수정)"}'

# Delete tag
curl -X DELETE http://localhost:8000/api/tags/1

# Batch delete tags
curl -X DELETE http://localhost:8000/api/tags/batch \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3]}'
```

## Error Handling Examples

```bash
# Duplicate line_code (409 Conflict)
curl -X POST http://localhost:8000/api/lines \
  -d '{"line_code": "LINE01", ...}'
# Response: {"error": "Conflict", "detail": "line_code 'LINE01' already exists"}

# Invalid process_code format (400 Bad Request)
curl -X POST http://localhost:8000/api/processes \
  -d '{"process_code": "INVALID", ...}'
# Response: {"error": "Validation Error", "detail": "Invalid 14-char format", "field": "process_code"}

# Foreign key violation (400 Bad Request)
curl -X POST http://localhost:8000/api/plc-connections \
  -d '{"process_id": 999, ...}'
# Response: {"error": "Bad Request", "detail": "process_id 999 not found"}
```

## Next Steps

- See [data-model.md](data-model.md) for complete Pydantic models
- See [contracts/api-summary.md](contracts/api-summary.md) for all endpoints
- Run tests: `pytest backend/tests/contract/`
