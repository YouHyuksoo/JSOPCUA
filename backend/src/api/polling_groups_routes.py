"""
Polling Groups API Routes

Feature 5: Database Management REST API
Provides CRUD operations for polling groups
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, status
from src.database.sqlite_manager import SQLiteManager
from .models import PollingGroupCreate, PollingGroupUpdate, PollingGroupResponse, TagResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import (
    validate_plc_exists,
    validate_polling_mode
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/polling-groups", tags=["polling-groups"])


# ==============================================================================
# POST /api/polling-groups - Create new polling group
# ==============================================================================

@router.post("", response_model=PollingGroupResponse, status_code=status.HTTP_201_CREATED)
def create_polling_group(group: PollingGroupCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new polling group

    - **group_name**: Group name (max 200 chars)
    - **machine_code**: Optional machine code filter (max 50 chars)
    - **workstage_code**: Optional workstage code filter
    - **plc_code**: PLC code (must exist)
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
    validate_plc_exists(db, group.plc_code)

    # Validate polling mode and trigger configuration
    validate_polling_mode(group.mode, group.trigger_bit_address)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO polling_groups (
                group_name, polling_mode, polling_interval_ms, group_category, description, is_active, plc_code
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            group.group_name,
            group.mode,  # polling_mode
            group.interval_ms,  # polling_interval_ms
            group.group_category,  # group_category
            f"Line: {group.line_code or 'N/A'}, Workstage: {group.workstage_code or 'N/A'}",  # description
            group.enabled,  # is_active
            group.plc_code
        ))
        group_id = cursor.lastrowid

        # Assign tags to this polling group
        if group.tag_ids:
            placeholders = ','.join(['?'] * len(group.tag_ids))
            cursor.execute(f"""
                UPDATE tags
                SET polling_group_id = ?
                WHERE id IN ({placeholders})
            """, [group_id] + group.tag_ids)

        conn.commit()

    # Log operation
    log_crud_operation("CREATE", "Polling Group", group_id, success=True)

    # Return created group
    return get_polling_group(group_id, db)


# ==============================================================================
# GET /api/polling-groups - List all polling groups with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[PollingGroupResponse])
def list_polling_groups(
    plc_code: str = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all polling groups with pagination

    - **plc_code**: Optional filter by PLC code
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of polling groups
    """
    # Build query
    where_clause = "WHERE plc_code = ?" if plc_code else ""
    params_count = (plc_code,) if plc_code else ()
    params_list = (plc_code, pagination.limit, pagination.skip) if plc_code else (pagination.limit, pagination.skip)

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

    # Get tags in group (is_active='Y'인 태그만 반환)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tags
            WHERE polling_group_id = ?
              AND is_active = 1
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

    # Row format: (id, group_name, polling_mode, polling_interval_ms, description, is_active, created_at, updated_at, plc_id)
    # Get current values for validation
    current_mode = row[2] if group_update.mode is None else group_update.mode
    current_trigger = group_update.trigger_bit_address  # Not stored in DB

    # Validate mode and trigger (skip validation since trigger not in DB)
    # validate_polling_mode(current_mode, current_trigger)

    # Build update query
    updates = []
    params = []

    if group_update.group_name is not None:
        updates.append("group_name = ?")
        params.append(group_update.group_name)

    if group_update.mode is not None:
        updates.append("polling_mode = ?")
        params.append(group_update.mode)

    if group_update.interval_ms is not None:
        updates.append("polling_interval_ms = ?")
        params.append(group_update.interval_ms)

    if group_update.group_category is not None:
        updates.append("group_category = ?")
        params.append(group_update.group_category)

    # trigger_bit_address is not in DB (ignored)

    if group_update.enabled is not None:
        updates.append("is_active = ?")
        params.append(group_update.enabled)

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Update polling group if there are changes
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(group_id)
            query = f"UPDATE polling_groups SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)

        # Update tag assignments if provided
        if group_update.tag_ids is not None:
            # First, remove this group from all tags
            cursor.execute("""
                UPDATE tags
                SET polling_group_id = NULL
                WHERE polling_group_id = ?
            """, (group_id,))

            # Then, assign new tags
            if group_update.tag_ids:
                placeholders = ','.join(['?'] * len(group_update.tag_ids))
                cursor.execute(f"""
                    UPDATE tags
                    SET polling_group_id = ?
                    WHERE id IN ({placeholders})
                """, [group_id] + group_update.tag_ids)

        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Polling Group", group_id, success=True)

    # Return updated group
    return get_polling_group(group_id, db)


# ==============================================================================
# GET /api/polling-groups/{id}/pre-start-check - Check before starting
# ==============================================================================

@router.get("/{group_id}/pre-start-check")
def pre_start_check(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Pre-start validation check for polling group

    Validates:
    - Group exists and has tags
    - PLC connection is available
    - Tag count information

    Returns check results with detailed information
    """
    from src.polling.polling_group_manager import PollingGroupManager

    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, group_name, plc_code, polling_interval_ms
            FROM polling_groups
            WHERE id = ?
        """, (group_id,))
        group = cursor.fetchone()
        if not group:
            raise_not_found("Polling Group", group_id)

        group_name = group[1]
        plc_code = group[2]
        interval_ms = group[3]

        # Get tag count
        cursor.execute("""
            SELECT COUNT(*)
            FROM tags
            WHERE polling_group_id = ? AND is_active = 1
        """, (group_id,))
        tag_count = cursor.fetchone()[0]

        # Get PLC info
        cursor.execute("""
            SELECT plc_name, ip_address, port, is_active
            FROM plc_connections
            WHERE plc_code = ?
        """, (plc_code,))
        plc_info = cursor.fetchone()

    # Check if no tags
    if tag_count == 0:
        return {
            "can_start": False,
            "reason": "NO_TAGS",
            "message": f"폴링 그룹 '{group_name}'에 활성 태그가 없습니다.",
            "group_name": group_name,
            "plc_code": plc_code,
            "tag_count": 0,
            "plc_status": "unknown"
        }

    # Check PLC exists and active
    if not plc_info or not plc_info[3]:
        return {
            "can_start": False,
            "reason": "PLC_INACTIVE",
            "message": f"PLC '{plc_code}'가 비활성 상태이거나 존재하지 않습니다.",
            "group_name": group_name,
            "plc_code": plc_code,
            "tag_count": tag_count,
            "plc_status": "inactive"
        }

    plc_name = plc_info[0]
    ip_address = plc_info[1]
    port = plc_info[2]

    # Test PLC connection
    manager = PollingGroupManager.get_instance()
    if manager is None:
        return {
            "can_start": False,
            "reason": "ENGINE_NOT_READY",
            "message": "폴링 엔진이 초기화되지 않았습니다.",
            "group_name": group_name,
            "plc_code": plc_code,
            "tag_count": tag_count,
            "plc_status": "unknown"
        }

    # Test actual PLC connection
    plc_connected = False
    connection_error = None

    try:
        pool_manager = manager.pool_manager
        # Try to get a connection (will create if needed)
        pool = pool_manager._get_pool(plc_code)
        test_conn = pool.get_connection(timeout=5)

        # Connection successful
        plc_connected = True

        # Return connection immediately
        pool.return_connection(test_conn)

    except Exception as e:
        connection_error = str(e)
        logger.warning(f"PLC connection test failed for {plc_code} ({ip_address}:{port}): {e}")

    # Return result
    if plc_connected:
        return {
            "can_start": True,
            "reason": "OK",
            "message": f"폴링 시작 준비 완료",
            "group_name": group_name,
            "plc_code": plc_code,
            "plc_name": plc_name,
            "plc_ip": ip_address,
            "plc_port": port,
            "tag_count": tag_count,
            "interval_ms": interval_ms,
            "plc_status": "connected"
        }
    else:
        return {
            "can_start": False,
            "reason": "PLC_CONNECTION_FAILED",
            "message": f"PLC '{plc_code}' ({ip_address}:{port}) 연결 실패: {connection_error}",
            "group_name": group_name,
            "plc_code": plc_code,
            "plc_name": plc_name,
            "plc_ip": ip_address,
            "plc_port": port,
            "tag_count": tag_count,
            "interval_ms": interval_ms,
            "plc_status": "connection_failed",
            "error_detail": connection_error
        }


# ==============================================================================
# POST /api/polling-groups/{id}/start - Start polling group
# ==============================================================================

@router.post("/{group_id}/start")
def start_polling_group(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Start a polling group

    - **group_id**: Polling group ID

    Returns success message
    """
    from src.polling.polling_group_manager import PollingGroupManager
    from src.polling.exceptions import PollingGroupNotFoundError, PollingGroupAlreadyRunningError

    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, group_name FROM polling_groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        if not group:
            raise_not_found("Polling Group", group_id)

    # Get polling group manager instance
    manager = PollingGroupManager.get_instance()
    if manager is None:
        # Manager not initialized yet
        return {
            "success": False,
            "message": "Polling engine not initialized. Please start the backend service.",
            "new_status": "stopped"
        }

    try:
        # Start the polling group
        result = manager.start_group(group_id)
        return result

    except (PollingGroupNotFoundError, PollingGroupAlreadyRunningError) as e:
        return {
            "success": False,
            "message": str(e),
            "new_status": "stopped"
        }
    except Exception as e:
        logger.error(f"Failed to start polling group {group_id}: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Failed to start polling group: {str(e)}",
            "new_status": "error"
        }


# ==============================================================================
# POST /api/polling-groups/{id}/stop - Stop polling group
# ==============================================================================

@router.post("/{group_id}/stop")
def stop_polling_group(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Stop a polling group

    - **group_id**: Polling group ID

    Returns success message
    """
    from src.polling.polling_group_manager import PollingGroupManager
    from src.polling.exceptions import PollingGroupNotFoundError, PollingGroupNotRunningError

    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, group_name FROM polling_groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        if not group:
            raise_not_found("Polling Group", group_id)

    # Get polling group manager instance
    manager = PollingGroupManager.get_instance()
    if manager is None:
        return {
            "success": False,
            "message": "Polling engine not initialized. Please start the backend service.",
            "new_status": "stopped"
        }

    try:
        # Stop the polling group
        result = manager.stop_group(group_id)
        return result

    except (PollingGroupNotFoundError, PollingGroupNotRunningError) as e:
        return {
            "success": False,
            "message": str(e),
            "new_status": "stopped"
        }
    except Exception as e:
        logger.error(f"Failed to stop polling group {group_id}: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Failed to stop polling group: {str(e)}",
            "new_status": "error"
        }


# ==============================================================================
# POST /api/polling-groups/{id}/restart - Restart polling group
# ==============================================================================

@router.post("/{group_id}/restart")
def restart_polling_group(group_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Restart a polling group

    - **group_id**: Polling group ID

    Returns success message
    """
    from src.polling.polling_group_manager import PollingGroupManager
    from src.polling.exceptions import PollingGroupNotFoundError

    # Check group exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, group_name FROM polling_groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        if not group:
            raise_not_found("Polling Group", group_id)

    # Get polling group manager instance
    manager = PollingGroupManager.get_instance()
    if manager is None:
        return {
            "success": False,
            "message": "Polling engine not initialized. Please start the backend service.",
            "new_status": "stopped"
        }

    try:
        # Restart the polling group
        result = manager.restart_group(group_id)
        return result

    except PollingGroupNotFoundError as e:
        return {
            "success": False,
            "message": str(e),
            "new_status": "stopped"
        }
    except Exception as e:
        logger.error(f"Failed to restart polling group {group_id}: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Failed to restart polling group: {str(e)}",
            "new_status": "error"
        }


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
    # Row format after migration with group_category:
    # (0:id, 1:group_name, 2:plc_code, 3:polling_mode, 4:polling_interval_ms, 5:group_category,
    #  6:trigger_bit_address, 7:trigger_bit_offset, 8:auto_reset_trigger, 9:priority,
    #  10:description, 11:is_active, 12:created_at, 13:updated_at)
    group_id = row[0]

    # Count tags in this polling group
    from .dependencies import get_db
    db = next(get_db())
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tags WHERE polling_group_id = ? AND is_active = 1", (group_id,))
        tag_count = cursor.fetchone()[0]

    return PollingGroupResponse(
        id=group_id,
        group_name=row[1],
        line_code=None,  # Legacy field, not in DB
        machine_code=None,  # Not in DB
        workstage_code=None,  # Not in DB
        plc_code=row[2],
        mode=row[3],  # polling_mode
        interval_ms=row[4],  # polling_interval_ms
        group_category=row[5],  # group_category (OPERATION, STATE, ALARM)
        trigger_bit_address=row[6],
        trigger_bit_offset=row[7] if row[7] is not None else 0,  # Default to 0 if None
        auto_reset_trigger=bool(row[8]),
        priority=row[9],
        enabled=bool(row[11]),  # is_active
        created_at=row[12],
        updated_at=row[13],
        tag_count=tag_count,
        status="stopped"  # Default status, will be updated by polling engine
    )


def _row_to_tag_response(row) -> TagResponse:
    """Convert database row to TagResponse (for /tags endpoint)"""
    # Row format from PRAGMA table_info:
    # 0:id, 1:plc_code, 2:workstage_code, 3:tag_address, 4:tag_name, 5:tag_type,
    # 6:unit, 7:scale, 8:offset, 9:min_value, 10:max_value, 11:polling_group_id,
    # 12:description, 13:is_active, 14:last_value, 15:last_updated_at, 16:created_at,
    # 17:updated_at, 18:tag_category, 19:log_mode, 20:machine_code
    from datetime import datetime
    return TagResponse(
        id=row[0],
        plc_code=row[1],
        tag_address=row[3],
        tag_name=row[4],
        tag_division=row[18] if len(row) > 18 and row[18] else '',  # tag_category
        data_type=row[5],  # tag_type
        unit=str(row[6]) if row[6] else None,
        scale=float(row[7]) if row[7] is not None else 1.0,
        machine_code=str(row[20]) if len(row) > 20 and row[20] is not None else None,
        polling_group_id=row[11],  # polling_group_id is at index 11
        enabled=bool(row[13]),  # is_active
        created_at=row[16] if row[16] else datetime.now().isoformat(),
        updated_at=row[17] if row[17] else datetime.now().isoformat()
    )
