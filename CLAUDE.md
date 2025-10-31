# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **SpecKit-enabled repository** - a feature-driven development workflow that structures feature development through specification, planning, task generation, and implementation phases. The workflow is managed through slash commands and generates structured documentation alongside code.

## SpecKit Workflow Commands

The repository uses a structured development workflow via slash commands:

### Core Workflow (Sequential Order)

1. **/speckit.specify [feature description]** - Create feature specification from natural language
   - Generates `specs/[###-feature-name]/spec.md` with user stories, requirements, and success criteria
   - Creates and checks out a new feature branch `[###-feature-name]`
   - Validates specification quality before proceeding
   - Maximum 3 clarification questions if requirements are ambiguous

2. **/speckit.clarify** - Resolve underspecified areas (optional)
   - Asks up to 5 targeted questions about the current spec
   - Updates spec.md with clarifications

3. **/speckit.plan** - Generate implementation plan
   - Creates `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/`
   - Determines tech stack, project structure, and architecture
   - Validates against constitution principles
   - **Must be run before /speckit.tasks**

4. **/speckit.tasks** - Generate actionable task breakdown
   - Creates `tasks.md` with dependency-ordered, parallelizable tasks
   - Tasks are organized by user story for independent implementation
   - Includes parallel execution opportunities marked with [P]
   - Each task includes exact file paths

5. **/speckit.implement** - Execute implementation
   - Processes tasks.md phase by phase
   - Checks checklists completion before starting
   - Follows TDD approach if tests are included
   - Marks tasks as completed in tasks.md

### Supplementary Commands

- **/speckit.constitution** - Create/update project constitution
- **/speckit.checklist** - Generate custom validation checklists
- **/speckit.analyze** - Cross-artifact consistency analysis

## Project Structure

### Documentation Structure (per feature)

```
specs/[###-feature-name]/
├── spec.md              # Feature specification with user stories
├── plan.md              # Implementation plan with tech stack
├── research.md          # Technical research and decisions
├── data-model.md        # Entity relationships
├── quickstart.md        # Integration scenarios
├── contracts/           # API contracts (OpenAPI/GraphQL)
├── tasks.md             # Actionable task breakdown
└── checklists/          # Quality validation checklists
    ├── requirements.md
    ├── ux.md
    └── test.md
```

### Repository Structure

- `.specify/` - SpecKit configuration and templates
  - `memory/constitution.md` - Project governance principles
  - `templates/` - Templates for specs, plans, tasks, checklists
  - `scripts/bash/` - Helper scripts for feature setup and context management
- `.claude/commands/` - Slash command definitions (speckit.*)
- `specs/` - Feature specifications and design documents (generated)
- Source code at repository root (structure determined per-feature in plan.md)

## Key Workflow Principles

### Feature Branch Naming

Format: `[###-short-name]` (e.g., `001-user-auth`, `002-analytics-dashboard`)
- Number is auto-incremented based on existing branches and specs
- Short name is 2-4 words derived from feature description

### User Story Organization

Features are broken down into prioritized user stories (P1, P2, P3...):
- Each story must be **independently testable**
- Each story delivers standalone value (MVP-capable)
- Tasks are organized by story to enable parallel development
- P1 story is the minimal viable product

### Task Format

Tasks follow strict checklist format:
```
- [ ] [TaskID] [P?] [StoryLabel?] Description with exact/file/path.ext
```

- **[P]**: Parallelizable (different files, no dependencies)
- **[US1]**, **[US2]**: User story labels (only in user story phases)
- Task IDs are sequential (T001, T002, T003...)

### Test Approach

Tests are **optional** unless explicitly requested:
- If included, follow TDD: write tests → ensure they fail → implement
- Test types: contract tests, integration tests, unit tests
- Located in `tests/contract/`, `tests/integration/`, `tests/unit/`

## Constitution Governance

All features must comply with principles in `.specify/memory/constitution.md`:
- Constitution is checked during `/speckit.plan`
- Violations must be justified in plan.md Complexity Tracking section
- Re-evaluated after Phase 1 design

## Scripts and Automation

### Feature Setup Scripts (in .specify/scripts/bash/)

- **create-new-feature.sh** - Initialize new feature branch and spec structure
  ```bash
  .specify/scripts/bash/create-new-feature.sh --json "$DESCRIPTION" --number N --short-name "name"
  ```

- **check-prerequisites.sh** - Validate feature environment before tasks/implementation
  ```bash
  .specify/scripts/bash/check-prerequisites.sh --json [--require-tasks] [--include-tasks]
  ```

- **setup-plan.sh** - Setup planning environment
  ```bash
  .specify/scripts/bash/setup-plan.sh --json
  ```

- **update-agent-context.sh** - Update AI agent context files with new tech stack
  ```bash
  .specify/scripts/bash/update-agent-context.sh claude
  ```

All scripts output JSON for parsing. Use `--json` flag for machine-readable output.

## Important Implementation Notes

### Path Conventions

Project structure varies by type (determined in plan.md):
- **Single project**: `src/`, `tests/` at root
- **Web application**: `backend/src/`, `frontend/src/`
- **Mobile + API**: `api/src/`, `ios/` or `android/`

### Checklist Validation

Before `/speckit.implement`:
- All checklists in `specs/[###-feature]/checklists/` must be complete
- If incomplete, user is prompted to proceed or wait
- Format: `- [ ]` (incomplete), `- [X]` (complete)

### Ignore Files

During implementation, automatically create/verify ignore files based on detected tech:
- `.gitignore` (if git repo)
- `.dockerignore` (if Dockerfile exists)
- `.eslintignore` (if .eslintrc* exists)
- Technology-specific patterns from plan.md tech stack

## Workflow Best Practices

1. **Always start with /speckit.specify** - Don't write code before specification
2. **Run /speckit.plan before /speckit.tasks** - Tasks need the plan context
3. **Check tasks.md before implementation** - Verify task breakdown makes sense
4. **Implement by user story** - Complete P1 story for MVP, then add P2, P3...
5. **Mark tasks completed** - Update tasks.md as you progress (change `[ ]` to `[X]`)
6. **Validate independently** - Each user story should work standalone
7. **Constitution compliance** - Justify any complexity or pattern violations

## Common Pitfalls to Avoid

- Don't create tasks.md without plan.md
- Don't implement without reading all available design docs (plan, data-model, contracts)
- Don't skip constitution validation
- Don't create implementation details in spec.md (keep it business-focused)
- Don't use relative paths in tasks or scripts (always absolute)
- Don't add [Story] labels to Setup or Foundational phase tasks
- Don't forget to update tasks.md checkboxes as tasks complete

## Quality Gates

### Specification Quality (enforced in /speckit.specify)
- No implementation details (languages, frameworks, APIs)
- All requirements testable and unambiguous
- Maximum 3 [NEEDS CLARIFICATION] markers
- Success criteria are measurable and technology-agnostic

### Planning Quality (enforced in /speckit.plan)
- All NEEDS CLARIFICATION resolved via research.md
- Constitution violations justified
- Project structure matches detected type

### Task Quality (enforced in /speckit.tasks)
- All tasks follow checklist format with IDs, labels, file paths
- User stories are independently testable
- Dependencies clearly documented
- Parallel opportunities identified

## Active Technologies
- SQLite 파일 기반 데이터베이스 (backend/config/scada.db) (001-project-structure-sqlite-setup)
- Python 3.11+ + pymcprotocol (PLC 통신), queue (스레드 안전 큐), threading (멀티스레딩) (002-mc3e-protocol-pool)
- SQLite (Feature 1의 plc_connections, tags 테이블 활용) (002-mc3e-protocol-pool)

## Recent Changes
- 001-project-structure-sqlite-setup: Added SQLite 파일 기반 데이터베이스 (backend/config/scada.db)
