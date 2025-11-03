# API Contracts Summary

**Feature**: 005-database-crud-api

## Endpoints Overview

### Lines API (`/api/lines`)
- `POST /api/lines` - Create line
- `GET /api/lines` - List lines (paginated)
- `GET /api/lines/{id}` - Get line by ID
- `PUT /api/lines/{id}` - Update line
- `DELETE /api/lines/{id}` - Delete line

### Processes API (`/api/processes`)
- `POST /api/processes` - Create process
- `GET /api/processes` - List processes (filtered by line_id)
- `GET /api/processes/{id}` - Get process by ID
- `PUT /api/processes/{id}` - Update process
- `DELETE /api/processes/{id}` - Delete process

### PLC Connections API (`/api/plc-connections`)
- `POST /api/plc-connections` - Create PLC connection
- `GET /api/plc-connections` - List PLCs (filtered by process_id)
- `GET /api/plc-connections/{id}` - Get PLC by ID
- `POST /api/plc-connections/{id}/test` - Test PLC connectivity
- `PUT /api/plc-connections/{id}` - Update PLC
- `DELETE /api/plc-connections/{id}` - Delete PLC

### Tags API (`/api/tags`)
- `POST /api/tags` - Create tag
- `POST /api/tags/import-csv` - Import tags from CSV
- `GET /api/tags` - List tags (filtered, paginated)
- `GET /api/tags/{id}` - Get tag by ID
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag
- `DELETE /api/tags/batch` - Delete multiple tags

### Polling Groups API (`/api/polling-groups`)
- `POST /api/polling-groups` - Create polling group
- `GET /api/polling-groups` - List groups (filtered)
- `GET /api/polling-groups/{id}` - Get group by ID
- `GET /api/polling-groups/{id}/tags` - Get tags in group
- `PUT /api/polling-groups/{id}` - Update group
- `DELETE /api/polling-groups/{id}` - Delete group

## Common Patterns

### Pagination Query Parameters
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 1000)

### Filter Query Parameters
- Varies by resource (e.g., `line_id`, `process_id`, `enabled`)

### HTTP Status Codes
- `200 OK` - Successful read/update/delete
- `201 Created` - Successful create
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate unique key
- `422 Unprocessable Entity` - Pydantic validation error
- `500 Internal Server Error` - Server error

## Authentication
Currently: None (localhost only)
Future: Bearer token authentication (Feature 7)
