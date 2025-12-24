"""
Lines API Routes

Feature 5: Database Management REST API
Provides CRUD operations for production lines
"""

from typing import List
from fastapi import APIRouter, Depends, status
from src.database.sqlite_manager import SQLiteManager
from .models import LineCreate, LineUpdate, LineResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import validate_line_code_unique

router = APIRouter(prefix="/api/lines", tags=["lines"])


# ==============================================================================
# POST /api/lines - Create new line
# ==============================================================================

@router.post("", response_model=LineResponse, status_code=status.HTTP_201_CREATED)
def create_line(line: LineCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new production line

    - **line_code**: Unique line code (max 50 chars)
    - **line_name**: Line name (max 200 chars)
    - **location**: Optional location (max 100 chars)
    - **enabled**: Enable/disable flag (default: true)

    Returns created line with id, created_at, updated_at
    """
    # Validate unique line_code
    validate_line_code_unique(db, line.line_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lines (line_code, line_name, description, is_active)
            VALUES (?, ?, ?, ?)
        """, (line.line_code, line.line_name, line.location, line.enabled))
        conn.commit()
        line_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "Line", line_id, success=True)

    # Fetch created line
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lines WHERE id = ?", (line_id,))
        row = cursor.fetchone()

    # Row format: (id, line_code, line_name, description, is_active, created_at, updated_at)
    return LineResponse(
        id=row[0],
        line_code=row[1],
        line_name=row[2],
        location=row[3],  # description
        enabled=bool(row[4]),  # is_active
        created_at=row[5],
        updated_at=row[6]
    )


# ==============================================================================
# GET /api/lines - List all lines with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[LineResponse])
def list_lines(
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all production lines with pagination

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of lines
    """
    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM lines")
        total_count = cursor.fetchone()[0]

    # Get paginated lines
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM lines
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (pagination.limit, pagination.skip))
        rows = cursor.fetchall()

    # Row format: (id, line_code, line_name, description, is_active, created_at, updated_at)
    lines = [
        LineResponse(
            id=row[0],
            line_code=row[1],
            line_name=row[2],
            location=row[3],  # description
            enabled=bool(row[4]),  # is_active
            created_at=row[5],
            updated_at=row[6]
        )
        for row in rows
    ]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=lines,
        **metadata
    )


# ==============================================================================
# GET /api/lines/{id} - Get single line by ID
# ==============================================================================

@router.get("/{line_id}", response_model=LineResponse)
def get_line(line_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single production line by ID

    - **line_id**: Line ID

    Returns line details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lines WHERE id = ?", (line_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Line", line_id)

    # Row format: (id, line_code, line_name, description, is_active, created_at, updated_at)
    return LineResponse(
        id=row[0],
        line_code=row[1],
        line_name=row[2],
        location=row[3],  # description
        enabled=bool(row[4]),  # is_active
        created_at=row[5],
        updated_at=row[6]
    )


# ==============================================================================
# PUT /api/lines/{id} - Update line
# ==============================================================================

@router.put("/{line_id}", response_model=LineResponse)
def update_line(
    line_id: int,
    line_update: LineUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a production line

    - **line_id**: Line ID
    - **line_name**: Optional new line name
    - **location**: Optional new location
    - **enabled**: Optional enable/disable flag

    Returns updated line
    """
    # Check line exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lines WHERE id = ?", (line_id,))
        if not cursor.fetchone():
            raise_not_found("Line", line_id)

    # Build update query
    updates = []
    params = []

    if line_update.line_name is not None:
        updates.append("line_name = ?")
        params.append(line_update.line_name)

    if line_update.location is not None:
        updates.append("description = ?")
        params.append(line_update.location)

    if line_update.enabled is not None:
        updates.append("is_active = ?")
        params.append(line_update.enabled)

    if not updates:
        # No changes, return current line
        return get_line(line_id, db)

    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(line_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE lines SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Line", line_id, success=True)

    # Return updated line
    return get_line(line_id, db)


# ==============================================================================
# DELETE /api/lines/{id} - Delete line
# ==============================================================================

@router.delete("/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_line(line_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a production line

    - **line_id**: Line ID

    Returns 204 No Content on success

    Note: Will fail if line has associated processes (foreign key constraint)
    """
    # Check line exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lines WHERE id = ?", (line_id,))
        if not cursor.fetchone():
            raise_not_found("Line", line_id)

    # Delete line
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lines WHERE id = ?", (line_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "Line", line_id, success=True)
