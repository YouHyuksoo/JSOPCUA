"""
Machines API Routes

Feature 5: Database Management REST API
Provides CRUD operations for production machines (equipment/facilities)
"""

from typing import List, Dict
from fastapi import APIRouter, Depends, status, HTTPException
from src.database.sqlite_manager import SQLiteManager
from .models import MachineCreate, MachineUpdate, MachineResponse, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import validate_machine_code_unique
from src.oracle_writer.oracle_helper import get_oracle_machines
from src.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/machines", tags=["machines"])


# ==============================================================================
# POST /api/machines - Create new machine
# ==============================================================================

@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(machine: MachineCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new production machine

    - **machine_code**: Unique machine code (max 50 chars)
    - **machine_name**: Machine name (max 200 chars)
    - **location**: Optional location (max 100 chars)
    - **enabled**: Enable/disable flag (default: true)

    Returns created machine with id, created_at, updated_at
    """
    # Validate unique machine_code
    validate_machine_code_unique(db, machine.machine_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO machines (machine_code, machine_name, location, is_active)
            VALUES (?, ?, ?, ?)
        """, (machine.machine_code, machine.machine_name, machine.location, machine.enabled))
        conn.commit()
        machine_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "Machine", machine_id, success=True)

    # Fetch created machine
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines WHERE id = ?", (machine_id,))
        row = cursor.fetchone()

    # Row format: (id, machine_code, machine_name, location, is_active, created_at, updated_at)
    return MachineResponse(
        id=row[0],
        machine_code=row[1],
        machine_name=row[2],
        location=row[3],  # description
        enabled=bool(row[4]),  # is_active
        created_at=row[5],
        updated_at=row[6]
    )


# ==============================================================================
# GET /api/machines - List all machines with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[MachineResponse])
def list_machines(
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all production machines with pagination

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of machines
    """
    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM machines")
        total_count = cursor.fetchone()[0]

    # Get paginated machines
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM machines
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (pagination.limit, pagination.skip))
        rows = cursor.fetchall()

    # Row format: (id, machine_code, machine_name, location, is_active, created_at, updated_at)
    machines = [
        MachineResponse(
            id=row[0],
            machine_code=row[1],
            machine_name=row[2],
            location=row[3],  # description
            enabled=bool(row[4]),  # is_active
            created_at=row[5],
            updated_at=row[6]
        )
        for row in rows
    ]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=machines,
        **metadata
    )


# ==============================================================================
# GET /api/machines/oracle-connection-info - Get Oracle connection info
# ==============================================================================

@router.get("/oracle-connection-info", response_model=Dict)
def get_oracle_connection_info():
    """
    Get Oracle database connection information (without password)

    Returns:
        {
            "host": "localhost",
            "port": 1521,
            "service_name": "ORCL",
            "username": "scada_user",
            "dsn": "localhost:1521/ORCL",
            "connection_string": "scada_user@localhost:1521/ORCL"
        }
    """
    try:
        from src.oracle_writer.config import load_config_from_env
        config = load_config_from_env()
        return config.to_dict()
    except Exception as e:
        logger.error(f"Failed to load Oracle config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load Oracle configuration: {str(e)}"
        )


# ==============================================================================
# POST /api/machines/sync-from-oracle - Sync machines from Oracle DB
# ==============================================================================

@router.post("/sync-from-oracle", response_model=Dict)
def sync_machines_from_oracle(db: SQLiteManager = Depends(get_db)):
    """
    Synchronize machines from Oracle ICOM_MACHINE_MASTER table to SQLite

    This endpoint:
    1. Fetches all active machines (USE_YN='Y') from Oracle ICOM_MACHINE_MASTER
    2. For each Oracle machine:
       - If machine_code exists in SQLite: UPDATE the machine
       - If machine_code doesn't exist: INSERT new machine
    3. Returns sync statistics (total, created, updated, skipped, errors)

    Returns:
        {
            "success": true,
            "total_oracle_machines": 10,
            "created": 5,
            "updated": 3,
            "skipped": 2,
            "errors": 0,
            "error_details": []
        }
    """
    try:
        # Fetch machines from Oracle
        logger.info("Starting Oracle machine synchronization...")
        oracle_machines = get_oracle_machines()
        logger.info(f"Fetched {len(oracle_machines)} machines from Oracle")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        error_details = []

        with db.get_connection() as conn:
            cursor = conn.cursor()

            for oracle_machine in oracle_machines:
                machine_code = oracle_machine['machine_code']
                machine_name = oracle_machine['machine_name']
                location = oracle_machine.get('location')
                is_active = oracle_machine.get('is_active', 1)

                try:
                    # Check if machine exists in SQLite
                    cursor.execute(
                        "SELECT id FROM machines WHERE machine_code = ?",
                        (machine_code,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # UPDATE existing machine
                        machine_id = existing[0]
                        cursor.execute("""
                            UPDATE machines
                            SET machine_name = ?,
                                location = ?,
                                is_active = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE machine_code = ?
                        """, (machine_name, location, is_active, machine_code))
                        updated_count += 1
                        logger.info(f"Updated machine: {machine_code}")
                    else:
                        # INSERT new machine
                        cursor.execute("""
                            INSERT INTO machines (machine_code, machine_name, location, is_active)
                            VALUES (?, ?, ?, ?)
                        """, (machine_code, machine_name, location, is_active))
                        created_count += 1
                        logger.info(f"Created machine: {machine_code}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Failed to sync {machine_code}: {str(e)}"
                    error_details.append(error_msg)
                    logger.error(error_msg)

            conn.commit()

        result = {
            "success": error_count == 0,
            "total_oracle_machines": len(oracle_machines),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_count,
            "error_details": error_details
        }

        logger.info(f"Oracle sync completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Oracle sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync from Oracle: {str(e)}"
        )


# ==============================================================================
# GET /api/machines/{id} - Get single machine by ID
# ==============================================================================

@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single production machine by ID

    - **machine_id**: Machine ID

    Returns machine details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines WHERE id = ?", (machine_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Machine", machine_id)

    # Row format: (id, machine_code, machine_name, location, is_active, created_at, updated_at)
    return MachineResponse(
        id=row[0],
        machine_code=row[1],
        machine_name=row[2],
        location=row[3],  # description
        enabled=bool(row[4]),  # is_active
        created_at=row[5],
        updated_at=row[6]
    )


# ==============================================================================
# PUT /api/machines/{id} - Update machine
# ==============================================================================

@router.put("/{machine_id}", response_model=MachineResponse)
def update_machine(
    machine_id: int,
    machine_update: MachineUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a production machine

    - **machine_id**: Machine ID
    - **machine_name**: Optional new machine name
    - **location**: Optional new location
    - **enabled**: Optional enable/disable flag

    Returns updated machine
    """
    # Check machine exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM machines WHERE id = ?", (machine_id,))
        if not cursor.fetchone():
            raise_not_found("Machine", machine_id)

    # Build update query
    updates = []
    params = []

    if machine_update.machine_name is not None:
        updates.append("machine_name = ?")
        params.append(machine_update.machine_name)

    if machine_update.location is not None:
        updates.append("location = ?")
        params.append(machine_update.location)

    if machine_update.enabled is not None:
        updates.append("is_active = ?")
        params.append(machine_update.enabled)

    if not updates:
        # No changes, return current machine
        return get_machine(machine_id, db)

    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(machine_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE machines SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Machine", machine_id, success=True)

    # Return updated machine
    return get_machine(machine_id, db)


# ==============================================================================
# DELETE /api/machines/{id} - Delete machine
# ==============================================================================

@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(machine_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a production machine

    - **machine_id**: Machine ID

    Returns 204 No Content on success

    Note: Will fail if machine has associated processes (foreign key constraint)
    """
    # Check machine exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM machines WHERE id = ?", (machine_id,))
        if not cursor.fetchone():
            raise_not_found("Machine", machine_id)

    # Delete machine
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "Machine", machine_id, success=True)
