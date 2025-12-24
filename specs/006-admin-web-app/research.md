# Research: Next.js Admin Web Application

**Feature**: 006-admin-web-app | **Date**: 2025-11-02

## Decisions Made

### 1. shadcn/ui Component Library

**Decision**: Use shadcn/ui (copy-paste components, not npm package)

**Rationale**: Pre-built accessible React components on Radix UI, Tailwind CSS integration, TypeScript-first, full control over code, supports dark mode, active community.

**Alternatives**: Material-UI (too heavy), Ant Design (not TypeScript-first), Chakra UI (npm dependency)

**Implementation**: npx shadcn-ui@latest init

### 2. CSV File Upload & Parsing

**Decision**: Use Papa Parse for client-side CSV parsing

**Rationale**: Lightweight (5KB), fast, streaming support, excellent error handling with row/column details, browser-native.

**Alternatives**: csv-parser (server-side only), manual parsing (error-prone), xlsx (overkill)

**Implementation**: npm install papaparse @types/papaparse

### 3. Real-time Dashboard Updates

**Decision**: HTTP polling with 5-second intervals (NOT WebSocket)

**Rationale**: Simple React useEffect + setInterval, no persistent connection, backend may not support WebSocket, 5s refresh acceptable, easy retry logic.

**Alternatives**: WebSocket (complex), SSE (compatibility issues), React Query (overkill)

### 4. Form Validation

**Decision**: Zod + React Hook Form

**Rationale**: TypeScript-first schema validation, derive types from schemas, perfect React Hook Form integration, client-side validation reduces server load.

**Alternatives**: Yup (less TypeScript-friendly), Joi (server-focused), manual (error-prone)

**Implementation**: npm install zod react-hook-form @hookform/resolvers

### 5. API Client Pattern

**Decision**: Axios with interceptors

**Rationale**: Cleaner API than fetch, global error handling via interceptors, automatic JSON transformation, better error messages.

**Alternatives**: Native fetch (more boilerplate), SWR/React Query (overkill)

### 6. State Management

**Decision**: React hooks only (useState, useEffect) - NO global state library

**Rationale**: Simple state requirements, no complex cross-component sharing, each page independent, React Context for toast, reduces bundle size.

**Alternatives**: Redux Toolkit (too complex), Zustand (unnecessary), Jotai (not needed)

### 7. Pagination Strategy

**Decision**: Server-side pagination with query parameters

**Rationale**: Backend supports ?page=1&limit=20, avoids loading all data, REST conventions, shadcn/ui Pagination component support.

### 8. File Upload Handling

**Decision**: FormData multipart/form-data upload

**Rationale**: Standard browser API, FastAPI supports python-multipart, metadata alongside file, axios onUploadProgress for tracking.

### 9. Error Display Pattern

**Decision**: Toast for global errors, inline for form fields

**Rationale**: shadcn/ui Toast non-blocking, react-hook-form field errors below input, separation of concerns, clear UX.

### 10. Responsive Design

**Decision**: Tailwind CSS responsive classes (mobile-first)

**Rationale**: Utility classes for breakpoints, mobile-first design, shadcn/ui already responsive, no custom CSS.

**Breakpoints**: Mobile (default 375px+), Tablet (md: 768px+), Desktop (lg: 1024px+)

## Technology Stack

**Frontend**: Next.js 14.2.33, TypeScript 5.3+, shadcn/ui, Tailwind CSS, React Hook Form, Zod, Axios, Papa Parse
**Backend Integration**: FastAPI REST (http://localhost:8000/api), No auth, CORS for localhost:3000/3001
**State**: React hooks (useState, useEffect, useContext)

## Installation Commands

```bash
cd apps/admin
npm install axios zod react-hook-form @hookform/resolvers papaparse @types/papaparse
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card table dialog toast select input textarea label form checkbox tabs badge alert pagination
```
