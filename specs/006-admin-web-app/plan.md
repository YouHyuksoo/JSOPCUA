# Implementation Plan: Next.js 관리 웹 애플리케이션

**Branch**: `006-admin-web-app` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-admin-web-app/spec.md`

## Summary

Complete the Next.js-based admin web application that controls and manages the Python SCADA backend. Provide CRUD interfaces for lines, processes, PLCs, and tags with CSV bulk upload. Enable polling group management with start/stop/restart controls. Display real-time system monitoring dashboard and log viewer. Use shadcn/ui for consistent UI components and implement responsive design.

**Technical Approach**: Extend existing Next.js 14.2.33 app in apps/admin/, add new pages for CRUD management, integrate with FastAPI backend at localhost:8000, use shadcn/ui components, implement client-side state management with React hooks, add file upload for CSV, create real-time dashboard with HTTP polling (5s interval), and build log viewer with filtering/pagination.

## Technical Context

**Language/Version**: TypeScript 5.3+ (frontend), Python 3.11+ (backend APIs assumed existing)
**Primary Dependencies**: Next.js 14.2.33, React 18, shadcn/ui, Tailwind CSS, Zod (validation)
**Storage**: SQLite backend/config/scada.db (via FastAPI REST API)
**Testing**: Manual testing, integration with existing FastAPI endpoints
**Target Platform**: Web browsers (Chrome, Firefox, Edge, Safari latest), responsive (mobile 375px+, tablet 768px+, desktop 1024px+)
**Project Type**: Web application (monorepo with apps/admin/)
**Performance Goals**: CRUD operations <200ms, CSV upload 100 tags <1min, dashboard refresh every 5s, log query <1s for 10k+ logs
**Constraints**: Must use existing FastAPI backend (localhost:8000), shadcn/ui only (no custom CSS), server-side pagination, file upload <5MB, TypeScript strict mode
**Scale/Scope**: 10 concurrent users, 100+ tags, 10,000+ log entries, 6 main feature pages, ~30 shadcn/ui components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Autonomous Implementation**: Plan supports fully autonomous `/speckit.implement` execution
✅ **Feature Independence**: Frontend-only feature, communicates via existing FastAPI REST APIs
✅ **API-First Design**: Frontend consumes existing backend REST APIs (assumed already implemented)
✅ **Database Integrity**: No direct database access; all operations via backend API
✅ **Performance Standards**: Target <200ms CRUD, <1min CSV upload, 5s dashboard refresh
✅ **Error Handling**: User-friendly error messages via toast notifications, field-specific validation
✅ **Testing Requirements**: Manual testing with test scripts, integration with backend API

**No violations** - Feature follows constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/006-admin-web-app/
├── plan.md              # This file
├── research.md          # Phase 0 output (shadcn/ui setup, CSV parsing, real-time updates)
├── data-model.md        # Phase 1 output (TypeScript interfaces for API responses)
├── quickstart.md        # Phase 1 output (dev server setup, page navigation)
├── contracts/           # Phase 1 output (API endpoint documentation)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
apps/admin/                          # Next.js 14.2.33 App Router
├── app/
│   ├── layout.tsx                  # Root layout (already exists)
│   ├── page.tsx                    # Dashboard home (already exists)
│   ├── lines/                      # NEW: Line management
│   │   ├── page.tsx               # List view
│   │   ├── [id]/page.tsx          # Detail/edit view
│   │   └── new/page.tsx           # Create view
│   ├── processes/                  # NEW: Process management
│   │   ├── page.tsx
│   │   ├── [id]/page.tsx
│   │   └── new/page.tsx
│   ├── plcs/                       # NEW: PLC management
│   │   ├── page.tsx
│   │   ├── [id]/page.tsx
│   │   └── new/page.tsx
│   ├── tags/                       # NEW: Tag management with CSV upload
│   │   ├── page.tsx
│   │   ├── [id]/page.tsx
│   │   ├── new/page.tsx
│   │   └── upload/page.tsx
│   ├── polling-groups/             # NEW: Polling group management
│   │   ├── page.tsx
│   │   ├── [id]/page.tsx
│   │   └── new/page.tsx
│   ├── dashboard/                  # NEW: System status monitoring
│   │   └── page.tsx
│   └── logs/                       # NEW: Log viewer
│       └── page.tsx
├── components/                     # shadcn/ui components + custom
│   ├── ui/                        # shadcn/ui auto-generated
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── dialog.tsx
│   │   ├── toast.tsx
│   │   ├── select.tsx
│   │   ├── input.tsx
│   │   └── ... (25+ components)
│   ├── line-form.tsx              # NEW: Line create/edit form
│   ├── process-form.tsx           # NEW: Process create/edit form
│   ├── plc-form.tsx               # NEW: PLC create/edit form
│   ├── tag-form.tsx               # NEW: Tag create/edit form
│   ├── csv-upload.tsx             # NEW: CSV file upload component
│   ├── polling-group-form.tsx     # NEW: Polling group form
│   ├── system-status-card.tsx     # NEW: Dashboard status card
│   └── log-filter.tsx             # NEW: Log filtering UI
├── lib/
│   ├── api/
│   │   ├── client.ts              # NEW: Axios/fetch wrapper
│   │   ├── lines.ts               # NEW: Line CRUD API calls
│   │   ├── processes.ts           # NEW: Process CRUD API calls
│   │   ├── plcs.ts                # NEW: PLC CRUD API calls
│   │   ├── tags.ts                # NEW: Tag CRUD API calls
│   │   ├── polling-groups.ts      # NEW: Polling group CRUD + control
│   │   ├── system-status.ts       # NEW: System monitoring API
│   │   └── logs.ts                # NEW: Log retrieval API
│   ├── types/
│   │   ├── line.ts                # NEW: Line TypeScript interfaces
│   │   ├── process.ts             # NEW: Process interfaces
│   │   ├── plc.ts                 # NEW: PLC interfaces
│   │   ├── tag.ts                 # NEW: Tag interfaces
│   │   ├── polling-group.ts       # NEW: Polling group interfaces
│   │   └── log.ts                 # NEW: Log entry interfaces
│   ├── utils.ts                   # Utility functions
│   └── validators.ts              # NEW: Zod schemas for forms
├── public/
├── package.json
├── tsconfig.json                  # TypeScript config (already exists)
├── tailwind.config.ts            # Tailwind config
└── next.config.js                # Next.js config

backend/src/api/                   # Assumed existing FastAPI routes
├── lines.py                      # Assumed: GET/POST/PUT/DELETE /api/lines
├── processes.py                  # Assumed: CRUD /api/processes
├── plc_connections.py            # Assumed: CRUD /api/plc_connections
├── tags.py                       # Assumed: CRUD /api/tags, POST /api/tags/upload
├── polling_groups.py             # Assumed: CRUD + POST /api/polling/groups/{id}/start|stop|restart
├── system.py                     # Assumed: GET /api/system/status
└── logs.py                       # Assumed: GET /api/logs/{log_type}
```

**Structure Decision**: Extend existing monorepo structure with apps/admin/ directory. Feature 3 already created Next.js app with basic polling pages. Feature 6 adds 6 new page groups (lines, processes, plcs, tags, polling-groups, dashboard, logs), shadcn/ui components, API client library, and TypeScript types.

