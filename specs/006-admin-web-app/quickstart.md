# Quickstart: Next.js Admin Web Application

**Feature**: 006-admin-web-app | **Date**: 2025-11-02

## Prerequisites

1. **Backend Running**: FastAPI server must be running on http://localhost:8000
   ```bash
   cd backend
   python -m venv .venv
   .venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   uvicorn src.api.main:app --reload
   ```

2. **Database**: SQLite database must exist at backend/config/scada.db with tables from Features 1-5

3. **Node.js**: Version 18+ required

## Installation

```bash
# Install dependencies for admin app
cd apps/admin
npm install

# Initialize shadcn/ui (if not already done)
npx shadcn-ui@latest init
# Select: TypeScript, Tailwind, App Router, @/ alias, Yes to RSC

# Install additional dependencies
npm install axios zod react-hook-form @hookform/resolvers papaparse @types/papaparse

# Install shadcn/ui components
npx shadcn-ui@latest add button card table dialog toast select input textarea label form checkbox tabs badge alert pagination separator skeleton dropdown-menu
```

## Development Server

```bash
cd apps/admin
npm run dev

# Server runs on http://localhost:3001 (or 3000 if available)
```

## Page Navigation

**Homepage**: http://localhost:3001
- Dashboard with navigation links

**Line Management**: http://localhost:3001/lines
- List, create, edit, delete lines

**Process Management**: http://localhost:3001/processes
- List, create, edit, delete processes

**PLC Management**: http://localhost:3001/plcs
- List, create, edit, delete PLCs
- Test PLC connections

**Tag Management**: http://localhost:3001/tags
- List, create, edit, delete tags
- Upload CSV for bulk tag creation: http://localhost:3001/tags/upload

**Polling Groups**: http://localhost:3001/polling-groups
- List, create, edit, delete polling groups
- Start/stop/restart polling groups

**System Dashboard**: http://localhost:3001/dashboard
- Real-time system status monitoring
- CPU, memory, disk usage
- PLC connection status
- Buffer and Oracle writer metrics

**Log Viewer**: http://localhost:3001/logs
- View logs from 4 log files
- Filter by time range, level, keyword
- Download logs as CSV

## Testing Workflow

### 1. Test Line CRUD
```
1. Navigate to /lines
2. Click "Add Line" button
3. Fill form: name="Line 1", code="LINE001"
4. Submit and verify line appears in list
5. Click edit icon, modify name to "Line 1 Updated"
6. Submit and verify update
7. Click delete icon, confirm deletion
```

### 2. Test CSV Upload
```
1. Create test CSV file with columns: name,device_address,data_type,polling_interval,plc_id
2. Add rows: "Tag1,D100,INT,1.0,1" (repeat for 10 tags)
3. Navigate to /tags/upload
4. Select CSV file
5. Click Upload
6. Verify success count, check any errors
7. Go to /tags and verify tags created
```

### 3. Test Polling Control
```
1. Navigate to /polling-groups
2. Create polling group with 5 tags
3. Click "Start" button
4. Verify status changes to "Running"
5. Go to /dashboard
6. Verify active polling groups count increased
7. Return to /polling-groups, click "Stop"
8. Verify status changes to "Stopped"
```

### 4. Test Dashboard Real-time Updates
```
1. Open /dashboard in browser
2. Open browser DevTools Network tab
3. Observe API calls every 5 seconds to /api/system/status
4. Modify backend data (e.g., stop a polling group)
5. Wait 5 seconds
6. Verify dashboard reflects changes automatically
```

### 5. Test Log Viewer
```
1. Navigate to /logs
2. Select "error.log" from dropdown
3. Apply filter: level=ERROR, time range=Last 24 hours
4. Enter keyword search: "timeout"
5. Verify filtered results
6. Click pagination to navigate pages
7. Click "Download CSV" to export logs
```

## Common Issues

**Error: Cannot connect to backend**
- Check FastAPI is running on http://localhost:8000
- Verify CORS is configured for localhost:3001
- Check browser console for CORS errors

**Error: Module not found**
- Run npm install in apps/admin/
- Verify tsconfig.json has "@/*" path alias

**Error: shadcn/ui component not found**
- Run npx shadcn-ui@latest add [component-name]
- Check components/ui/ directory exists

**Port 3000 already in use**
- Next.js will auto-switch to 3001
- Or manually kill process on port 3000

## Environment Variables (Optional)

Create apps/admin/.env.local:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

Update lib/api/client.ts to use env var:
```typescript
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
  // ...
});
```

## Build for Production

```bash
cd apps/admin
npm run build
npm run start  # Production server on port 3000
```
