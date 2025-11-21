"""
Processes API Routes

Feature 5: Database Management REST API
Provides CRUD operations for production processes
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from src.database.sqlite_manager import SQLiteManager
from .models import ProcessCreate, ProcessUpdate, ProcessResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import (
    validate_machine_exists,
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

    - **machine_code**: Code of parent machine (must exist if provided)
    - **process_sequence**: Sequence number in machine
    - **process_code**: 14-character process code (format: [A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3})
    - **process_name**: Process name (max 200 chars)
    - **equipment_type**: Optional equipment type (max 10 chars)
    - **enabled**: Enable/disable flag (default: true)

    Returns created process with id, created_at, updated_at
    """
    # Validate foreign key if machine_code is provided
    if process.machine_code:
        validate_machine_exists(db, process.machine_code)

    # Validate process code format
    validate_process_code(process.process_code)

    # Validate unique process_code
    validate_process_code_unique(db, process.process_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO processes (
                machine_code, sequence_order, process_code, process_name,
                description, is_active
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            process.machine_code,
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

    # Row format: (id, process_code, process_name, machine_code, plc_id, description, is_active, created_at, updated_at, sequence_order)
    return ProcessResponse(
        id=row[0],
        machine_code=row[3],  # machine_code
        process_sequence=row[9],  # sequence_order
        process_code=row[1],
        process_name=row[2],
        equipment_type=row[5],  # description
        enabled=bool(row[6]),  # is_active
        created_at=row[7],
        updated_at=row[8]
    )


# ==============================================================================
# GET /api/processes - List all processes with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[ProcessResponse])
def list_processes(
    machine_code: str = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all production processes with pagination

    - **machine_code**: Optional filter by machine code
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of processes
    """
    # Build query
    where_clause = "WHERE machine_code = ?" if machine_code else ""
    params_count = (machine_code,) if machine_code else ()
    params_list = (machine_code, pagination.limit, pagination.skip) if machine_code else (pagination.limit, pagination.skip)

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
            ORDER BY machine_code, sequence_order
            LIMIT ? OFFSET ?
        """, params_list)
        rows = cursor.fetchall()

    # Row format: (id, process_code, process_name, machine_code, plc_id, description, is_active, created_at, updated_at, sequence_order)
    processes = [
        ProcessResponse(
            id=row[0],
            machine_code=row[3],  # machine_code
            process_sequence=row[9],  # sequence_order
            process_code=row[1],
            process_name=row[2],
            equipment_type=row[5],  # description
            enabled=bool(row[6]),  # is_active
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

    # Row format: (id, process_code, process_name, machine_code, plc_id, description, is_active, created_at, updated_at, sequence_order)
    return ProcessResponse(
        id=row[0],
        machine_code=row[3],  # machine_code
        process_sequence=row[9],  # sequence_order
        process_code=row[1],
        process_name=row[2],
        equipment_type=row[5],  # description
        enabled=bool(row[6]),  # is_active
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

    Note: process_code and machine_code cannot be updated

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
        updates.append("sequence_order = ?")
        params.append(process_update.process_sequence)

    if process_update.process_name is not None:
        updates.append("process_name = ?")
        params.append(process_update.process_name)

    if process_update.equipment_type is not None:
        updates.append("description = ?")
        params.append(process_update.equipment_type)

    if process_update.enabled is not None:
        updates.append("is_active = ?")
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
def sync_processes_from_oracle(db: SQLiteManager = Depends(get_db)):
    """
    Synchronize processes from Oracle ICOM_WORKSTAGE_MASTER table to SQLite processes

    매핑: ICOM_WORKSTAGE_MASTER (Oracle) → processes (SQLite)

    This endpoint:
    1. Fetches all active processes (USE_YN='Y') from Oracle ICOM_WORKSTAGE_MASTER
    2. For each Oracle process:
       - If process_code exists in SQLite: UPDATE the process
       - If process_code doesn't exist: INSERT new process
    3. Returns sync statistics

    Returns:
        {
            "success": true,
            "total_oracle_processes": 20,
            "created": 10,
            "updated": 8,
            "skipped": 2,
            "errors": 0,
            "error_details": []
        }
    """
    from src.oracle_writer.oracle_helper import get_oracle_processes
    from src.config.logging_config import get_logger

    logger = get_logger(__name__)

    try:
        # Fetch processes from Oracle
        logger.info("Starting Oracle process synchronization...")
        oracle_processes = get_oracle_processes()
        logger.info(f"Fetched {len(oracle_processes)} processes from Oracle")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        error_details = []

        with db.get_connection() as conn:
            cursor = conn.cursor()

            for oracle_process in oracle_processes:
                process_code = oracle_process['process_code']
                process_name = oracle_process['process_name']
                description = oracle_process.get('description', '')
                sequence_order = oracle_process.get('sequence_order', 0)

                try:
                    # Check if process exists in SQLite
                    cursor.execute(
                        "SELECT id FROM processes WHERE process_code = ?",
                        (process_code,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # UPDATE existing process
                        cursor.execute("""
                            UPDATE processes
                            SET process_name = ?,
                                description = ?,
                                sequence_order = ?,
                                is_active = 1,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE process_code = ?
                        """, (process_name, description, sequence_order, process_code))
                        updated_count += 1
                        logger.debug(f"Updated process: {process_code}")

                    else:
                        # INSERT new process (without machine_code and plc_id - will be set later)
                        cursor.execute("""
                            INSERT INTO processes
                            (process_code, process_name, description, sequence_order, is_active)
                            VALUES (?, ?, ?, ?, 1)
                        """, (process_code, process_name, description, sequence_order))
                        created_count += 1
                        logger.debug(f"Created process: {process_code}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Error processing {process_code}: {str(e)}"
                    error_details.append(error_msg)
                    logger.error(error_msg)
                    continue

            # Commit all changes
            conn.commit()

        logger.info(
            f"Process sync completed: {created_count} created, "
            f"{updated_count} updated, {error_count} errors"
        )

        return {
            "success": True,
            "total_oracle_processes": len(oracle_processes),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_count,
            "error_details": error_details
        }

    except Exception as e:
        logger.error(f"Oracle process sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync processes from Oracle: {str(e)}"
        )
