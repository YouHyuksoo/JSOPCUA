"""
PLC Connections API Routes

Feature 5: Database Management REST API
Provides CRUD operations for PLC connections with connectivity testing
"""

from typing import List
from fastapi import APIRouter, Depends, status
from database.sqlite_manager import SQLiteManager
from .models import PLCConnectionCreate, PLCConnectionUpdate, PLCConnectionResponse, PLCTestResult, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from database.validators import (
    validate_process_exists,
    validate_plc_code_unique,
    validate_ipv4_address
)
from plc.mc3e_client import MC3EClient
import time

router = APIRouter(prefix="/api/plc-connections", tags=["plc-connections"])


# ==============================================================================
# POST /api/plc-connections - Create new PLC connection
# ==============================================================================

@router.post("", response_model=PLCConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_plc_connection(plc: PLCConnectionCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new PLC connection

    - **process_id**: ID of parent process (must exist)
    - **plc_code**: Unique PLC code (max 50 chars)
    - **ip_address**: IPv4 address
    - **port**: Port number (default: 5000)
    - **network_no**: Network number (default: 0)
    - **station_no**: Station number (default: 0)
    - **enabled**: Enable/disable flag (default: true)

    Returns created PLC connection with id, created_at, updated_at
    """
    # Validate foreign key
    validate_process_exists(db, plc.process_id)

    # Validate IP address
    validate_ipv4_address(plc.ip_address)

    # Validate unique plc_code
    validate_plc_code_unique(db, plc.plc_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plc_connections (
                process_id, plc_code, ip_address, port,
                network_no, station_no, enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            plc.process_id,
            plc.plc_code,
            plc.ip_address,
            plc.port,
            plc.network_no,
            plc.station_no,
            plc.enabled
        ))
        conn.commit()
        plc_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "PLC Connection", plc_id, success=True)

    # Fetch created PLC connection
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plc_connections WHERE id = ?", (plc_id,))
        row = cursor.fetchone()

    return PLCConnectionResponse(
        id=row[0],
        process_id=row[1],
        plc_code=row[2],
        ip_address=row[3],
        port=row[4],
        network_no=row[5],
        station_no=row[6],
        enabled=bool(row[7]),
        created_at=row[8],
        updated_at=row[9]
    )


# ==============================================================================
# GET /api/plc-connections - List all PLC connections with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[PLCConnectionResponse])
def list_plc_connections(
    process_id: int = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all PLC connections with pagination

    - **process_id**: Optional filter by process ID
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of PLC connections
    """
    # Build query
    where_clause = "WHERE process_id = ?" if process_id else ""
    params_count = (process_id,) if process_id else ()
    params_list = (process_id, pagination.limit, pagination.skip) if process_id else (pagination.limit, pagination.skip)

    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM plc_connections {where_clause}", params_count)
        total_count = cursor.fetchone()[0]

    # Get paginated PLC connections
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM plc_connections
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, params_list)
        rows = cursor.fetchall()

    plcs = [
        PLCConnectionResponse(
            id=row[0],
            process_id=row[1],
            plc_code=row[2],
            ip_address=row[3],
            port=row[4],
            network_no=row[5],
            station_no=row[6],
            enabled=bool(row[7]),
            created_at=row[8],
            updated_at=row[9]
        )
        for row in rows
    ]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=plcs,
        **metadata
    )


# ==============================================================================
# GET /api/plc-connections/{id} - Get single PLC connection by ID
# ==============================================================================

@router.get("/{plc_id}", response_model=PLCConnectionResponse)
def get_plc_connection(plc_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single PLC connection by ID

    - **plc_id**: PLC connection ID

    Returns PLC connection details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plc_connections WHERE id = ?", (plc_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("PLC Connection", plc_id)

    return PLCConnectionResponse(
        id=row[0],
        process_id=row[1],
        plc_code=row[2],
        ip_address=row[3],
        port=row[4],
        network_no=row[5],
        station_no=row[6],
        enabled=bool(row[7]),
        created_at=row[8],
        updated_at=row[9]
    )


# ==============================================================================
# POST /api/plc-connections/{id}/test - Test PLC connection
# ==============================================================================

@router.post("/{plc_id}/test", response_model=PLCTestResult)
def test_plc_connection(plc_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Test PLC connection

    - **plc_id**: PLC connection ID

    Returns test result with status, response time, and error message if failed

    Reuses Feature 2's MC3EClient to test connectivity
    """
    # Get PLC connection
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plc_connections WHERE id = ?", (plc_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("PLC Connection", plc_id)

    # Extract connection params
    ip_address = row[3]
    port = row[4]
    network_no = row[5]
    station_no = row[6]

    # Test connection using MC3EClient
    client = None
    try:
        start_time = time.time()

        # Create client and attempt connection
        client = MC3EClient(
            plc_type="Q",
            host=ip_address,
            port=port,
            network_no=network_no,
            station_no=station_no
        )

        # Try to connect
        client.connect()

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Disconnect
        client.disconnect()

        return PLCTestResult(
            status="success",
            response_time_ms=response_time_ms,
            error=None
        )

    except Exception as e:
        error_message = str(e)

        return PLCTestResult(
            status="failed",
            response_time_ms=None,
            error=error_message
        )

    finally:
        # Ensure client is closed
        if client:
            try:
                client.disconnect()
            except:
                pass


# ==============================================================================
# PUT /api/plc-connections/{id} - Update PLC connection
# ==============================================================================

@router.put("/{plc_id}", response_model=PLCConnectionResponse)
def update_plc_connection(
    plc_id: int,
    plc_update: PLCConnectionUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a PLC connection

    - **plc_id**: PLC connection ID
    - **ip_address**: Optional new IP address
    - **port**: Optional new port number
    - **network_no**: Optional new network number
    - **station_no**: Optional new station number
    - **enabled**: Optional enable/disable flag

    Note: plc_code and process_id cannot be updated

    Returns updated PLC connection
    """
    # Check PLC exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM plc_connections WHERE id = ?", (plc_id,))
        if not cursor.fetchone():
            raise_not_found("PLC Connection", plc_id)

    # Validate IP if provided
    if plc_update.ip_address is not None:
        validate_ipv4_address(plc_update.ip_address)

    # Build update query
    updates = []
    params = []

    if plc_update.ip_address is not None:
        updates.append("ip_address = ?")
        params.append(plc_update.ip_address)

    if plc_update.port is not None:
        updates.append("port = ?")
        params.append(plc_update.port)

    if plc_update.network_no is not None:
        updates.append("network_no = ?")
        params.append(plc_update.network_no)

    if plc_update.station_no is not None:
        updates.append("station_no = ?")
        params.append(plc_update.station_no)

    if plc_update.enabled is not None:
        updates.append("enabled = ?")
        params.append(plc_update.enabled)

    if not updates:
        # No changes, return current PLC
        return get_plc_connection(plc_id, db)

    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(plc_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE plc_connections SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "PLC Connection", plc_id, success=True)

    # Return updated PLC
    return get_plc_connection(plc_id, db)


# ==============================================================================
# DELETE /api/plc-connections/{id} - Delete PLC connection
# ==============================================================================

@router.delete("/{plc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plc_connection(plc_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a PLC connection

    - **plc_id**: PLC connection ID

    Returns 204 No Content on success

    Note: Will fail if PLC has associated tags or polling groups (foreign key constraint)
    """
    # Check PLC exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM plc_connections WHERE id = ?", (plc_id,))
        if not cursor.fetchone():
            raise_not_found("PLC Connection", plc_id)

    # Delete PLC connection
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plc_connections WHERE id = ?", (plc_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "PLC Connection", plc_id, success=True)
