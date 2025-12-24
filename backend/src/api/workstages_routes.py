"""
Workstages API Routes

Feature 5: Database Management REST API
Provides CRUD operations for production workstages
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from src.database.sqlite_manager import SQLiteManager
from .models import WorkstageCreate, WorkstageUpdate, WorkstageResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import (
    validate_machine_exists,
    validate_workstage_code_unique,
    validate_workstage_code
)

router = APIRouter(prefix="/api/workstages", tags=["workstages"])


# ==============================================================================
# Helper function to convert database row to WorkstageResponse
# ==============================================================================

def _row_to_workstage_response(row):
    """
    Convert workstages table row to WorkstageResponse

    Row format: (id, workstage_code, workstage_name, description, sequence_order, is_active, created_at, updated_at)
    """
    return WorkstageResponse(
        id=row[0],
        machine_code=None,
        workstage_sequence=row[4],  # sequence_order
        workstage_code=row[1],
        workstage_name=row[2],
        equipment_type=row[3],  # description
        enabled=bool(row[5]),  # is_active
        created_at=row[6],
        updated_at=row[7]
    )


# ==============================================================================
# POST /api/workstages - Create new workstage
# ==============================================================================

@router.post("", response_model=WorkstageResponse, status_code=status.HTTP_201_CREATED)
def create_workstage(workstage: WorkstageCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new production workstage

    - **machine_code**: Code of parent machine (must exist if provided)
    - **workstage_sequence**: Sequence number in machine
    - **workstage_code**: 14-character workstage code (format: [A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3})
    - **workstage_name**: Workstage name (max 200 chars)
    - **equipment_type**: Optional equipment type (max 10 chars)
    - **enabled**: Enable/disable flag (default: true)

    Returns created workstage with id, created_at, updated_at
    """
    # Validate foreign key if machine_code is provided
    if workstage.machine_code:
        validate_machine_exists(db, workstage.machine_code)

    # Validate workstage code format
    validate_workstage_code(workstage.workstage_code)

    # Validate unique workstage_code
    validate_workstage_code_unique(db, workstage.workstage_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workstages (
                machine_code, sequence_order, workstage_code, workstage_name,
                description, is_active
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            workstage.machine_code,
            workstage.workstage_sequence,
            workstage.workstage_code,
            workstage.workstage_name,
            workstage.equipment_type,
            workstage.enabled
        ))
        conn.commit()
        workstage_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "Workstage", workstage_id, success=True)

    # Fetch created workstage
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workstages WHERE id = ?", (workstage_id,))
        row = cursor.fetchone()

    return _row_to_workstage_response(row)


# ==============================================================================
# GET /api/workstages - List all workstages with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[WorkstageResponse])
def list_workstages(
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all production workstages with pagination

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of workstages
    """
    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM workstages")
        total_count = cursor.fetchone()[0]

    # Get paginated workstages
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM workstages
            ORDER BY sequence_order, workstage_code
            LIMIT ? OFFSET ?
        """, (pagination.limit, pagination.skip))
        rows = cursor.fetchall()

    workstages = [_row_to_workstage_response(row) for row in rows]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=workstages,
        **metadata
    )


# ==============================================================================
# GET /api/workstages/{id} - Get single workstage by ID
# ==============================================================================

@router.get("/{workstage_id}", response_model=WorkstageResponse)
def get_workstage(workstage_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single production workstage by ID

    - **workstage_id**: Workstage ID

    Returns workstage details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workstages WHERE id = ?", (workstage_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Workstage", workstage_id)

    return _row_to_workstage_response(row)


# ==============================================================================
# PUT /api/workstages/{id} - Update workstage
# ==============================================================================

@router.put("/{workstage_id}", response_model=WorkstageResponse)
def update_workstage(
    workstage_id: int,
    workstage_update: WorkstageUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a production workstage

    - **workstage_id**: Workstage ID
    - **workstage_sequence**: Optional new sequence number
    - **workstage_name**: Optional new workstage name
    - **equipment_type**: Optional new equipment type
    - **enabled**: Optional enable/disable flag

    Note: workstage_code and machine_code cannot be updated

    Returns updated workstage
    """
    # Check workstage exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM workstages WHERE id = ?", (workstage_id,))
        if not cursor.fetchone():
            raise_not_found("Workstage", workstage_id)

    # Build update query
    updates = []
    params = []

    if workstage_update.workstage_sequence is not None:
        updates.append("sequence_order = ?")
        params.append(workstage_update.workstage_sequence)

    if workstage_update.workstage_name is not None:
        updates.append("workstage_name = ?")
        params.append(workstage_update.workstage_name)

    if workstage_update.equipment_type is not None:
        updates.append("description = ?")
        params.append(workstage_update.equipment_type)

    if workstage_update.enabled is not None:
        updates.append("is_active = ?")
        params.append(workstage_update.enabled)

    if not updates:
        # No changes, return current workstage
        return get_workstage(workstage_id, db)

    # Add updated_at and workstage_id for WHERE clause
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(workstage_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE workstages SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Workstage", workstage_id, success=True)

    # Return updated workstage
    return get_workstage(workstage_id, db)


# ==============================================================================
# DELETE /api/workstages/{id} - Delete workstage
# ==============================================================================

@router.delete("/{workstage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workstage(workstage_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a production workstage

    - **workstage_id**: Workstage ID

    Returns 204 No Content on success

    Note: Will fail if workstage has associated PLCs or tags (foreign key constraint)
    """
    # Check workstage exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM workstages WHERE id = ?", (workstage_id,))
        if not cursor.fetchone():
            raise_not_found("Workstage", workstage_id)

    # Delete workstage
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workstages WHERE id = ?", (workstage_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "Workstage", workstage_id, success=True)


# ==============================================================================
# Oracle Synchronization APIs
# ==============================================================================

@router.get("/oracle-connection-info")
def get_oracle_connection_info():
    """
    Get Oracle database connection information (without password)

    Returns connection details for Oracle sync confirmation dialog
    """
    try:
        from src.oracle_writer.config import load_config_from_env
        from src.config.logging_config import get_logger

        logger = get_logger(__name__)
        config = load_config_from_env()
        return config.to_dict()
    except Exception as e:
        from src.config.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Failed to load Oracle config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load Oracle configuration: {str(e)}"
        )


@router.post("/sync-from-oracle")
def sync_workstages_from_oracle(db: SQLiteManager = Depends(get_db)):
    """
    Synchronize workstages from Oracle ICOM_WORKSTAGE_MASTER table to SQLite workstages

    매핑: ICOM_WORKSTAGE_MASTER (Oracle) → workstages (SQLite)

    This endpoint:
    1. Fetches all active workstages (USE_YN='Y') from Oracle ICOM_WORKSTAGE_MASTER
    2. For each Oracle workstage:
       - If workstage_code exists in SQLite: UPDATE the workstage
       - If workstage_code doesn't exist: INSERT new workstage
    3. Returns sync statistics

    Returns:
        {
            "success": true,
            "total_oracle_workstages": 20,
            "created": 10,
            "updated": 8,
            "skipped": 2,
            "errors": 0,
            "error_details": []
        }
    """
    from src.oracle_writer.oracle_helper import get_oracle_workstages
    from src.config.logging_config import get_logger

    logger = get_logger(__name__)

    try:
        # Fetch workstages from Oracle
        logger.info("Starting Oracle workstage synchronization...")
        oracle_workstages = get_oracle_workstages()
        logger.info(f"Fetched {len(oracle_workstages)} workstages from Oracle")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        error_details = []

        with db.get_connection() as conn:
            cursor = conn.cursor()

            for oracle_workstage in oracle_workstages:
                workstage_code = oracle_workstage['workstage_code']
                workstage_name = oracle_workstage['workstage_name']
                description = oracle_workstage.get('description', '')
                sequence_order = oracle_workstage.get('sequence_order', 0)

                try:
                    # Check if workstage exists in SQLite
                    cursor.execute(
                        "SELECT id FROM workstages WHERE workstage_code = ?",
                        (workstage_code,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # UPDATE existing workstage
                        cursor.execute("""
                            UPDATE workstages
                            SET workstage_name = ?,
                                description = ?,
                                sequence_order = ?,
                                is_active = 1,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE workstage_code = ?
                        """, (workstage_name, description, sequence_order, workstage_code))
                        updated_count += 1
                        logger.debug(f"Updated workstage: {workstage_code}")

                    else:
                        # INSERT new workstage (without machine_code and plc_id - will be set later)
                        cursor.execute("""
                            INSERT INTO workstages
                            (workstage_code, workstage_name, description, sequence_order, is_active)
                            VALUES (?, ?, ?, ?, 1)
                        """, (workstage_code, workstage_name, description, sequence_order))
                        created_count += 1
                        logger.debug(f"Created workstage: {workstage_code}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Error processing {workstage_code}: {str(e)}"
                    error_details.append(error_msg)
                    logger.error(error_msg)
                    continue

            # Commit all changes
            conn.commit()

        logger.info(
            f"Workstage sync completed: {created_count} created, "
            f"{updated_count} updated, {error_count} errors"
        )

        return {
            "success": True,
            "total_oracle_workstages": len(oracle_workstages),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_count,
            "error_details": error_details
        }

    except Exception as e:
        logger.error(f"Oracle workstage sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync workstages from Oracle: {str(e)}"
        )
