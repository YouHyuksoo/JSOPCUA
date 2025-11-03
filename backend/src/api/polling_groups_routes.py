"""
Polling Groups API Routes

Feature 5: Database Management REST API
Provides CRUD operations for polling groups
"""

from typing import List
from fastapi import APIRouter, Depends, status
from database.sqlite_manager import SQLiteManager
from .models import PollingGroupCreate, PollingGroupUpdate, PollingGroupResponse, TagResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from database.validators import (
    validate_plc_exists,
    validate_polling_mode
)

router = APIRouter(prefix="/api/polling-groups", tags=["polling-groups"])


# ==============================================================================
# POST /api/polling-groups - Create new polling group
# ==============================================================================

@router.post("", response_model=PollingGroupResponse, status_code=status.HTTP_201_CREATED)
def create_polling_group(group: PollingGroupCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new polling group

    - **group_name**: Group name (max 200 chars)
    - **line_code**: Optional line code filter (max 50 chars)
    - **process_code**: Optional process code filter (max 50 chars)
    - **plc_id**: ID of PLC connection (must exist)
    - **mode**: Polling mode (FIXED or HANDSHAKE, default: FIXED)
    - **interval_ms**: Polling interval in milliseconds (default: 1000)
    - **trigger_bit_address**: Trigger bit address (required for HANDSHAKE mode)
    - **trigger_bit_offset**: Trigger bit offset (default: 0)
    - **auto_reset_trigger**: Auto-reset trigger after read (default: true)
    - **priority**: Priority (NORMAL, HIGH, LOW, default: NORMAL)
    - **enabled**: Enable/disable flag (default: true)

    Returns created polling group with id, created_at, updated_at
    """
    # Validate foreign key
    validate_plc_exists(db, group.plc_id)

    # Validate polling mode and trigger configuration
    validate_polling_mode(group.mode, group.trigger_bit_address)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO polling_groups (
                group_name, line_code, process_code, plc_id, mode,
                interval_ms, trigger_bit_address, trigger_bit_offset,
                auto_reset_trigger, priority, enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            group.group_name,
            group.line_code,
            group.process_code,
            group.plc_id,
            group.mode,
            group.interval_ms,
            group.trigger_bit_address,
            group.trigger_bit_offset,
            group.auto_reset_trigger,
            group.priority,
            group.enabled
        ))
        conn.commit()
        group_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "Polling Group", group_id, success=True)

    # Return created group
    return get_polling_group(group_id, db)


# ==============================================================================
# GET /api/polling-groups - List all polling groups with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[PollingGroupResponse])
def list_polling_groups(
    plc_id: int = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all polling groups with pagination

    - **plc_id**: Optional filter by PLC ID
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of polling groups
    """
    # Build query
    where_clause = "WHERE plc_id = ?" if plc_id else ""
    params_count = (plc_id,) if plc_id else ()
    params_list = (plc_id, pagination.limit, pagination.skip) if plc_id else (pagination.limit, pagination.skip)

    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM polling_groups {where_clause}", params_count)
        total_count = cursor.fetchone()[0]

    # Get paginated polling groups
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM polling_groups
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, params_list)
        rows = cursor.fetchall()

    groups = [_row_to_polling_group_response(row) for row in rows]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=groups,
        **metadata
    )


# ==============================================================================
# GET /api/polling-groups/{id} - Get single polling group by ID
# ==============================================================================

@router.get("/{group_id}", response_model=PollingGroupResponse)
def get_polling_group(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single polling group by ID

    - **group_id**: Polling group ID

    Returns polling group details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polling_groups WHERE id = ?", (group_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Polling Group", group_id)

    return _row_to_polling_group_response(row)


# ==============================================================================
# GET /api/polling-groups/{id}/tags - Get tags in polling group
# ==============================================================================

@router.get("/{group_id}/tags", response_model=List[TagResponse])
def get_polling_group_tags(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get all tags assigned to a polling group

    - **group_id**: Polling group ID

    Returns list of tags in the polling group
    """
    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM polling_groups WHERE id = ?", (group_id,))
        if not cursor.fetchone():
            raise_not_found("Polling Group", group_id)

    # Get tags in group
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tags
            WHERE polling_group_id = ?
            ORDER BY id
        """, (group_id,))
        rows = cursor.fetchall()

    tags = [_row_to_tag_response(row) for row in rows]
    return tags


# ==============================================================================
# PUT /api/polling-groups/{id} - Update polling group
# ==============================================================================

@router.put("/{group_id}", response_model=PollingGroupResponse)
def update_polling_group(
    group_id: int,
    group_update: PollingGroupUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a polling group

    - **group_id**: Polling group ID
    - **group_name**: Optional new group name
    - **mode**: Optional new polling mode (FIXED or HANDSHAKE)
    - **interval_ms**: Optional new polling interval
    - **trigger_bit_address**: Optional new trigger bit address
    - **enabled**: Optional enable/disable flag

    Returns updated polling group
    """
    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polling_groups WHERE id = ?", (group_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Polling Group", group_id)

    # Get current values for validation
    current_mode = row[5] if group_update.mode is None else group_update.mode
    current_trigger = row[7] if group_update.trigger_bit_address is None else group_update.trigger_bit_address

    # Validate mode and trigger
    validate_polling_mode(current_mode, current_trigger)

    # Build update query
    updates = []
    params = []

    if group_update.group_name is not None:
        updates.append("group_name = ?")
        params.append(group_update.group_name)

    if group_update.mode is not None:
        updates.append("mode = ?")
        params.append(group_update.mode)

    if group_update.interval_ms is not None:
        updates.append("interval_ms = ?")
        params.append(group_update.interval_ms)

    if group_update.trigger_bit_address is not None:
        updates.append("trigger_bit_address = ?")
        params.append(group_update.trigger_bit_address)

    if group_update.enabled is not None:
        updates.append("enabled = ?")
        params.append(group_update.enabled)

    if not updates:
        # No changes, return current group
        return get_polling_group(group_id, db)

    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(group_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE polling_groups SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Polling Group", group_id, success=True)

    # Return updated group
    return get_polling_group(group_id, db)


# ==============================================================================
# DELETE /api/polling-groups/{id} - Delete polling group
# ==============================================================================

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_polling_group(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a polling group

    - **group_id**: Polling group ID

    Returns 204 No Content on success

    Note: Tags in this group will have their polling_group_id set to NULL
    """
    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM polling_groups WHERE id = ?", (group_id,))
        if not cursor.fetchone():
            raise_not_found("Polling Group", group_id)

    # Delete polling group
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM polling_groups WHERE id = ?", (group_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "Polling Group", group_id, success=True)


# ==============================================================================
# Helper Functions
# ==============================================================================

def _row_to_polling_group_response(row) -> PollingGroupResponse:
    """Convert database row to PollingGroupResponse"""
    return PollingGroupResponse(
        id=row[0],
        group_name=row[1],
        line_code=row[2],
        process_code=row[3],
        plc_id=row[4],
        mode=row[5],
        interval_ms=row[6],
        trigger_bit_address=row[7],
        trigger_bit_offset=row[8],
        auto_reset_trigger=bool(row[9]),
        priority=row[10],
        enabled=bool(row[11]),
        created_at=row[12],
        updated_at=row[13]
    )


def _row_to_tag_response(row) -> TagResponse:
    """Convert database row to TagResponse (for /tags endpoint)"""
    return TagResponse(
        id=row[0],
        plc_id=row[1],
        process_id=row[2],
        tag_address=row[3],
        tag_name=row[4],
        tag_division=row[5],
        data_type=row[6],
        unit=row[7],
        scale=row[8],
        machine_code=row[9],
        polling_group_id=row[10],
        enabled=bool(row[11]),
        created_at=row[12],
        updated_at=row[13]
    )
