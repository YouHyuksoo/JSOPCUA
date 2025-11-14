"""
PLC Connections API Routes

Feature 5: Database Management REST API
Provides CRUD operations for PLC connections with connectivity testing
"""

from typing import List
from fastapi import APIRouter, Depends, status
from src.database.sqlite_manager import SQLiteManager
from .models import PLCConnectionCreate, PLCConnectionUpdate, PLCConnectionResponse, PLCTestResult, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import (
    validate_process_exists,
    validate_plc_code_unique,
    validate_ipv4_address
)
from src.plc.mc3e_client import MC3EClient
import time

router = APIRouter(prefix="/api/plc-connections", tags=["plc-connections"])


# ==============================================================================
# POST /api/plc-connections - Create new PLC connection
# ==============================================================================

@router.post("", response_model=PLCConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_plc_connection(plc: PLCConnectionCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new PLC connection

    - **plc_code**: Unique PLC code (max 50 chars)
    - **plc_name**: PLC name (max 100 chars)
    - **ip_address**: IPv4 address
    - **port**: Port number (default: 5010)
    - **protocol**: Protocol type (default: 'MC_3E_ASCII')
    - **network_no**: Network number (default: 0)
    - **station_no**: Station number (default: 0)
    - **connection_timeout**: Connection timeout in seconds (default: 5)
    - **is_active**: Enable/disable flag (default: true)

    Returns created PLC connection with id, created_at, updated_at
    """
    # Validate IP address
    validate_ipv4_address(plc.ip_address)

    # Validate unique plc_code
    validate_plc_code_unique(db, plc.plc_code)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plc_connections (
                plc_code, plc_name, plc_spec, plc_type, ip_address, port, protocol,
                network_no, station_no, connection_timeout, is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plc.plc_code,
            plc.plc_name,
            plc.plc_spec,
            plc.plc_type,
            plc.ip_address,
            plc.port,
            plc.protocol,
            plc.network_no,
            plc.station_no,
            plc.connection_timeout,
            plc.is_active
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

    # Row format: (id, plc_code, plc_name, ip_address, port, protocol, network_no, station_no, connection_timeout, is_active, last_connected_at, created_at, updated_at, plc_spec, plc_type)
    from datetime import datetime
    return PLCConnectionResponse(
        id=row[0],
        plc_code=row[1],
        plc_name=row[2],
        plc_spec=row[13] if len(row) > 13 else None,
        plc_type=row[14] if len(row) > 14 else None,
        ip_address=row[3],
        port=row[4],
        protocol=row[5],
        network_no=row[6] if row[6] is not None else 0,
        station_no=row[7] if row[7] is not None else 0,
        connection_timeout=row[8] if row[8] is not None else 5,
        is_active=bool(row[9]),
        created_at=row[11] if row[11] else datetime.now().isoformat(),
        updated_at=row[12] if row[12] else datetime.now().isoformat()
    )


# ==============================================================================
# GET /api/plc-connections - List all PLC connections with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[PLCConnectionResponse])
def list_plc_connections(
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all PLC connections with pagination

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of PLC connections
    """
    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM plc_connections")
        total_count = cursor.fetchone()[0]

    # Get paginated PLC connections
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM plc_connections
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (pagination.limit, pagination.skip))
        rows = cursor.fetchall()

    # Row format: (id, plc_code, plc_name, ip_address, port, protocol, network_no, station_no, connection_timeout, is_active, last_connected_at, created_at, updated_at, plc_spec, plc_type)
    from datetime import datetime
    plcs = [
        PLCConnectionResponse(
            id=row[0],
            plc_code=row[1],
            plc_name=row[2],
            plc_spec=row[13] if len(row) > 13 else None,
            plc_type=row[14] if len(row) > 14 else None,
            ip_address=row[3],
            port=row[4],
            protocol=row[5],
            network_no=row[6] if row[6] is not None else 0,
            station_no=row[7] if row[7] is not None else 0,
            connection_timeout=row[8] if row[8] is not None else 5,
            is_active=bool(row[9]),
            created_at=row[11] if row[11] else datetime.now().isoformat(),
            updated_at=row[12] if row[12] else datetime.now().isoformat()
        )
        for row in rows
    ]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=plcs,
        **metadata
    )


# ==============================================================================
# Oracle Synchronization APIs (MUST be before /{plc_id} to avoid path conflicts)
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
        from fastapi import HTTPException
        from src.config.logging_config import get_logger

        logger = get_logger(__name__)
        logger.error(f"Failed to load Oracle config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load Oracle configuration: {str(e)}"
        )


@router.post("/sync-from-oracle")
def sync_plcs_from_oracle(db: SQLiteManager = Depends(get_db)):
    """
    Synchronize PLCs from Oracle ICOM_PLC_MASTER table to SQLite plc_connections

    매핑: ICOM_PLC_MASTER (Oracle) → plc_connections (SQLite)

    This endpoint:
    1. Fetches all active PLCs (PLC_USE_YN='Y') from Oracle ICOM_PLC_MASTER
    2. For each Oracle PLC:
       - If plc_code exists in SQLite: UPDATE the PLC
       - If plc_code doesn't exist: INSERT new PLC
    3. Returns sync statistics

    Returns:
        {
            "success": true,
            "total_oracle_plcs": 10,
            "created": 5,
            "updated": 3,
            "skipped": 2,
            "errors": 0,
            "error_details": []
        }
    """
    from src.oracle_writer.oracle_helper import get_oracle_plcs
    from src.config.logging_config import get_logger
    from fastapi import HTTPException

    logger = get_logger(__name__)

    try:
        # Fetch PLCs from Oracle
        logger.info("Starting Oracle PLC synchronization...")
        oracle_plcs = get_oracle_plcs()
        logger.info(f"Fetched {len(oracle_plcs)} PLCs from Oracle")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        error_details = []

        with db.get_connection() as conn:
            cursor = conn.cursor()

            for oracle_plc in oracle_plcs:
                plc_code = oracle_plc['plc_code']
                plc_name = oracle_plc['plc_name']
                plc_spec = oracle_plc.get('plc_spec')
                plc_type = oracle_plc.get('plc_type')
                ip_address = oracle_plc['ip_address']
                port = oracle_plc['port']
                network_no = oracle_plc['network_no']
                station_no = oracle_plc['station_no']

                try:
                    # Check if PLC exists in SQLite
                    cursor.execute(
                        "SELECT id FROM plc_connections WHERE plc_code = ?",
                        (plc_code,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # UPDATE existing PLC
                        cursor.execute("""
                            UPDATE plc_connections
                            SET plc_name = ?,
                                plc_spec = ?,
                                plc_type = ?,
                                ip_address = ?,
                                port = ?,
                                protocol = ?,
                                network_no = ?,
                                station_no = ?,
                                is_active = 1,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE plc_code = ?
                        """, (plc_name, plc_spec, plc_type, ip_address, port, 'MC_3E_ASCII', network_no, station_no, plc_code))
                        updated_count += 1
                        logger.debug(f"Updated PLC: {plc_code}")

                    else:
                        # INSERT new PLC
                        cursor.execute("""
                            INSERT INTO plc_connections
                            (plc_code, plc_name, plc_spec, plc_type, ip_address, port, protocol, network_no, station_no, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (plc_code, plc_name, plc_spec, plc_type, ip_address, port, 'MC_3E_ASCII', network_no, station_no))
                        created_count += 1
                        logger.debug(f"Created PLC: {plc_code}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Error processing {plc_code}: {str(e)}"
                    error_details.append(error_msg)
                    logger.error(error_msg)
                    continue

            # Commit all changes
            conn.commit()

        logger.info(
            f"PLC sync completed: {created_count} created, "
            f"{updated_count} updated, {error_count} errors"
        )

        return {
            "success": True,
            "total_oracle_plcs": len(oracle_plcs),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_count,
            "error_details": error_details
        }

    except Exception as e:
        logger.error(f"Oracle PLC sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync PLCs from Oracle: {str(e)}"
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

    # Row format: (id, plc_code, plc_name, ip_address, port, protocol, network_no, station_no, connection_timeout, is_active, last_connected_at, created_at, updated_at, plc_spec, plc_type)
    from datetime import datetime
    return PLCConnectionResponse(
        id=row[0],
        plc_code=row[1],
        plc_name=row[2],
        plc_spec=row[13] if len(row) > 13 else None,
        plc_type=row[14] if len(row) > 14 else None,
        ip_address=row[3],
        port=row[4],
        protocol=row[5],
        network_no=row[6] if row[6] is not None else 0,
        station_no=row[7] if row[7] is not None else 0,
        connection_timeout=row[8] if row[8] is not None else 5,
        is_active=bool(row[9]),
        created_at=row[11] if row[11] else datetime.now().isoformat(),
        updated_at=row[12] if row[12] else datetime.now().isoformat()
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
    # Row format: (id, plc_code, plc_name, ip_address, port, protocol, network_no, station_no, connection_timeout, is_active, last_connected_at, created_at, updated_at)
    plc_code = row[1]
    ip_address = row[3]
    port = row[4]
    connection_timeout = row[8] if row[8] is not None else 5

    # Test connection using MC3EClient
    client = None
    try:
        start_time = time.time()

        # Create client and attempt connection
        client = MC3EClient(
            ip_address=ip_address,
            port=port,
            plc_code=plc_code,
            timeout=connection_timeout
        )

        # Try to connect
        client.connect()

        # Read D100, W100+W101, and M100 test values
        test_value_d100 = None
        test_value_w100 = None
        test_value_m100 = None

        from src.config.logging_config import get_logger
        logger = get_logger(__name__)

        try:
            test_value_d100 = client.read_single("D100")
            logger.info(f"[{plc_code}] Test read D100 = {test_value_d100}")
        except Exception as read_error:
            logger.warning(f"[{plc_code}] Failed to read D100: {read_error}")

        try:
            # W100과 W101을 읽어서 32비트로 결합
            values = client.read_batch(["W100", "W101"])

            if "W100" in values and "W101" in values:
                w100 = values["W100"]
                w101 = values["W101"]

                # 16비트 워드 2개를 32비트로 결합
                # W100: 하위 16비트, W101: 상위 16비트
                # 음수 처리를 위해 & 0xFFFF로 16비트 양수로 변환
                w100_unsigned = w100 & 0xFFFF if w100 < 0 else w100
                w101_unsigned = w101 & 0xFFFF if w101 < 0 else w101

                # 32비트 결합: (상위 16비트 << 16) | 하위 16비트
                test_value_w100 = (w101_unsigned << 16) | w100_unsigned

                # 32비트 부호 있는 정수로 변환 (필요시)
                if test_value_w100 >= 0x80000000:
                    test_value_w100 = test_value_w100 - 0x100000000

                logger.info(f"[{plc_code}] Test read W100+W101 = {test_value_w100} (W100={w100}, W101={w101})")
            else:
                logger.warning(f"[{plc_code}] Failed to read W100 or W101")
        except Exception as read_error:
            logger.warning(f"[{plc_code}] Failed to read W100+W101: {read_error}")

        try:
            # M100 비트 읽기
            test_value_m100 = client.read_single("M100")
            logger.info(f"[{plc_code}] Test read M100 = {test_value_m100}")
        except Exception as read_error:
            logger.warning(f"[{plc_code}] Failed to read M100: {read_error}")

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Disconnect
        client.disconnect()

        return PLCTestResult(
            status="success",
            response_time_ms=response_time_ms,
            test_value_d100=test_value_d100,
            test_value_w100=test_value_w100,
            test_value_m100=test_value_m100,
            error=None
        )

    except Exception as e:
        error_message = str(e)

        return PLCTestResult(
            status="failed",
            response_time_ms=None,
            test_value_d100=None,
            test_value_w100=None,
            test_value_m100=None,
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
    - **plc_name**: Optional new PLC name
    - **ip_address**: Optional new IP address
    - **port**: Optional new port number
    - **protocol**: Optional new protocol
    - **network_no**: Optional new network number
    - **station_no**: Optional new station number
    - **connection_timeout**: Optional new timeout
    - **is_active**: Optional enable/disable flag

    Note: plc_code cannot be updated

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

    if plc_update.plc_name is not None:
        updates.append("plc_name = ?")
        params.append(plc_update.plc_name)

    if plc_update.plc_spec is not None:
        updates.append("plc_spec = ?")
        params.append(plc_update.plc_spec)

    if plc_update.plc_type is not None:
        updates.append("plc_type = ?")
        params.append(plc_update.plc_type)

    if plc_update.ip_address is not None:
        updates.append("ip_address = ?")
        params.append(plc_update.ip_address)

    if plc_update.port is not None:
        updates.append("port = ?")
        params.append(plc_update.port)

    if plc_update.protocol is not None:
        updates.append("protocol = ?")
        params.append(plc_update.protocol)

    if plc_update.network_no is not None:
        updates.append("network_no = ?")
        params.append(plc_update.network_no)

    if plc_update.station_no is not None:
        updates.append("station_no = ?")
        params.append(plc_update.station_no)

    if plc_update.connection_timeout is not None:
        updates.append("connection_timeout = ?")
        params.append(plc_update.connection_timeout)

    if plc_update.is_active is not None:
        updates.append("is_active = ?")
        params.append(plc_update.is_active)

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
