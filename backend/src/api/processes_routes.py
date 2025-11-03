"""
Processes API Routes

Feature 5: Database Management REST API
Provides CRUD operations for production processes
"""

from typing import List
from fastapi import APIRouter, Depends, status
from database.sqlite_manager import SQLiteManager
from .models import ProcessCreate, ProcessUpdate, ProcessResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from database.validators import (
    validate_line_exists,
    validate_process_code_unique,
    validate_process_code
)

router = APIRouter(prefix="/api/processes", tags=["processes"])


# ==============================================================================
# POST /api/processes - Create new process
# ==============================================================================

@router.post("", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
def create_process(process: ProcessCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new production process

    - **line_id**: ID of parent line (must exist)
    - **process_sequence**: Sequence number in line
    - **process_code**: 14-character process code (format: [A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3})
    - **process_name**: Process name (max 200 chars)
    - **equipment_type**: Optional equipment type (max 10 chars)
    - **enabled**: Enable/disable flag (default: true)

    Returns created process with id, created_at, updated_at
    """
    # Validate foreign key
    validate_line_exists(db, process.line_id)

    # Validate process code format
    validate_process_code(process.process_code)

    # Validate unique process_code
    validate_process_code_unique(db, process.process_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO processes (
                line_id, process_sequence, process_code, process_name,
                equipment_type, enabled
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            process.line_id,
            process.process_sequence,
            process.process_code,
            process.process_name,
            process.equipment_type,
            process.enabled
        ))
        conn.commit()
        process_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "Process", process_id, success=True)

    # Fetch created process
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM processes WHERE id = ?", (process_id,))
        row = cursor.fetchone()

    return ProcessResponse(
        id=row[0],
        line_id=row[1],
        process_sequence=row[2],
        process_code=row[3],
        process_name=row[4],
        equipment_type=row[5],
        enabled=bool(row[6]),
        created_at=row[7],
        updated_at=row[8]
    )


# ==============================================================================
# GET /api/processes - List all processes with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[ProcessResponse])
def list_processes(
    line_id: int = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all production processes with pagination

    - **line_id**: Optional filter by line ID
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of processes
    """
    # Build query
    where_clause = "WHERE line_id = ?" if line_id else ""
    params_count = (line_id,) if line_id else ()
    params_list = (line_id, pagination.limit, pagination.skip) if line_id else (pagination.limit, pagination.skip)

    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM processes {where_clause}", params_count)
        total_count = cursor.fetchone()[0]

    # Get paginated processes
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM processes
            {where_clause}
            ORDER BY line_id, process_sequence
            LIMIT ? OFFSET ?
        """, params_list)
        rows = cursor.fetchall()

    processes = [
        ProcessResponse(
            id=row[0],
            line_id=row[1],
            process_sequence=row[2],
            process_code=row[3],
            process_name=row[4],
            equipment_type=row[5],
            enabled=bool(row[6]),
            created_at=row[7],
            updated_at=row[8]
        )
        for row in rows
    ]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=processes,
        **metadata
    )


# ==============================================================================
# GET /api/processes/{id} - Get single process by ID
# ==============================================================================

@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(process_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single production process by ID

    - **process_id**: Process ID

    Returns process details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM processes WHERE id = ?", (process_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Process", process_id)

    return ProcessResponse(
        id=row[0],
        line_id=row[1],
        process_sequence=row[2],
        process_code=row[3],
        process_name=row[4],
        equipment_type=row[5],
        enabled=bool(row[6]),
        created_at=row[7],
        updated_at=row[8]
    )


# ==============================================================================
# PUT /api/processes/{id} - Update process
# ==============================================================================

@router.put("/{process_id}", response_model=ProcessResponse)
def update_process(
    process_id: int,
    process_update: ProcessUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a production process

    - **process_id**: Process ID
    - **process_sequence**: Optional new sequence number
    - **process_name**: Optional new process name
    - **equipment_type**: Optional new equipment type
    - **enabled**: Optional enable/disable flag

    Note: process_code and line_id cannot be updated

    Returns updated process
    """
    # Check process exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM processes WHERE id = ?", (process_id,))
        if not cursor.fetchone():
            raise_not_found("Process", process_id)

    # Build update query
    updates = []
    params = []

    if process_update.process_sequence is not None:
        updates.append("process_sequence = ?")
        params.append(process_update.process_sequence)

    if process_update.process_name is not None:
        updates.append("process_name = ?")
        params.append(process_update.process_name)

    if process_update.equipment_type is not None:
        updates.append("equipment_type = ?")
        params.append(process_update.equipment_type)

    if process_update.enabled is not None:
        updates.append("enabled = ?")
        params.append(process_update.enabled)

    if not updates:
        # No changes, return current process
        return get_process(process_id, db)

    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(process_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE processes SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Process", process_id, success=True)

    # Return updated process
    return get_process(process_id, db)


# ==============================================================================
# DELETE /api/processes/{id} - Delete process
# ==============================================================================

@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(process_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a production process

    - **process_id**: Process ID

    Returns 204 No Content on success

    Note: Will fail if process has associated PLCs or tags (foreign key constraint)
    """
    # Check process exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM processes WHERE id = ?", (process_id,))
        if not cursor.fetchone():
            raise_not_found("Process", process_id)

    # Delete process
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processes WHERE id = ?", (process_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "Process", process_id, success=True)
