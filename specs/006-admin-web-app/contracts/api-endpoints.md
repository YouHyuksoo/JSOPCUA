# API Endpoints: Next.js Admin Web Application

**Feature**: 006-admin-web-app | **Date**: 2025-11-02
**Base URL**: http://localhost:8000/api

## Lines API

### GET /api/lines
List all lines with pagination
**Query Params**: ?page=1&limit=20
**Response**: PaginatedResponse<Line>

### POST /api/lines
Create new line
**Body**: CreateLineRequest
**Response**: Line

### GET /api/lines/{id}
Get line by ID
**Response**: Line

### PUT /api/lines/{id}
Update line
**Body**: CreateLineRequest
**Response**: Line

### DELETE /api/lines/{id}
Delete line
**Response**: {success: boolean, message: string}

## Processes API

### GET /api/processes
List all processes
**Query Params**: ?page=1&limit=20&line_id=1
**Response**: PaginatedResponse<Process>

### POST /api/processes
Create new process
**Body**: CreateProcessRequest
**Response**: Process

### GET /api/processes/{id}
Get process by ID
**Response**: Process

### PUT /api/processes/{id}
Update process
**Body**: CreateProcessRequest
**Response**: Process

### DELETE /api/processes/{id}
Delete process
**Response**: {success: boolean, message: string}

## PLCs API

### GET /api/plc_connections
List all PLCs
**Query Params**: ?page=1&limit=20&process_id=1
**Response**: PaginatedResponse<PLC>

### POST /api/plc_connections
Create new PLC
**Body**: CreatePLCRequest
**Response**: PLC

### GET /api/plc_connections/{id}
Get PLC by ID
**Response**: PLC

### PUT /api/plc_connections/{id}
Update PLC
**Body**: CreatePLCRequest
**Response**: PLC

### DELETE /api/plc_connections/{id}
Delete PLC
**Response**: {success: boolean, message: string}

### POST /api/plc_connections/{id}/test
Test PLC connection
**Response**: PLCTestResponse

## Tags API

### GET /api/tags
List all tags
**Query Params**: ?page=1&limit=20&plc_id=1&search=temp
**Response**: PaginatedResponse<Tag>

### POST /api/tags
Create new tag
**Body**: CreateTagRequest
**Response**: Tag

### GET /api/tags/{id}
Get tag by ID
**Response**: Tag

### PUT /api/tags/{id}
Update tag
**Body**: CreateTagRequest
**Response**: Tag

### DELETE /api/tags/{id}
Delete tag
**Response**: {success: boolean, message: string}

### POST /api/tags/upload
Upload CSV file for bulk tag creation
**Body**: multipart/form-data with file field
**Response**: CSVUploadResponse

## Polling Groups API

### GET /api/polling/groups
List all polling groups
**Query Params**: ?page=1&limit=20
**Response**: PaginatedResponse<PollingGroup>

### POST /api/polling/groups
Create new polling group
**Body**: CreatePollingGroupRequest
**Response**: PollingGroup

### GET /api/polling/groups/{id}
Get polling group by ID
**Response**: PollingGroup

### PUT /api/polling/groups/{id}
Update polling group
**Body**: CreatePollingGroupRequest
**Response**: PollingGroup

### DELETE /api/polling/groups/{id}
Delete polling group
**Response**: {success: boolean, message: string}

### POST /api/polling/groups/{id}/start
Start polling group
**Response**: PollingControlResponse

### POST /api/polling/groups/{id}/stop
Stop polling group
**Response**: PollingControlResponse

### POST /api/polling/groups/{id}/restart
Restart polling group
**Response**: PollingControlResponse

### POST /api/polling/groups/start-all
Start all stopped polling groups
**Response**: {success: boolean, started_count: number}

### POST /api/polling/groups/stop-all
Stop all running polling groups
**Response**: {success: boolean, stopped_count: number}

## System Status API

### GET /api/system/status
Get current system status
**Response**: DashboardData

## Logs API

### GET /api/logs/{log_type}
Get logs by type
**Path Param**: log_type = scada | error | communication | performance
**Query Params**: ?page=1&limit=50&start_time=2025-11-01T00:00:00&levels=ERROR,CRITICAL&search=timeout
**Response**: LogQueryResponse

### GET /api/logs/{log_type}/download
Download filtered logs as CSV
**Query Params**: same as GET /api/logs/{log_type}
**Response**: CSV file download

## Error Response Format

All endpoints return errors in consistent format:
```json
{
  "error": "ValidationError",
  "detail": "Line code must be unique",
  "field": "code"
}
```

**HTTP Status Codes**:
- 200: Success (GET, PUT)
- 201: Created (POST)
- 400: Bad Request (invalid input)
- 404: Not Found
- 409: Conflict (unique constraint)
- 422: Validation Error
- 500: Internal Server Error
