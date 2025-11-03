"""
Tags API Routes

Feature 5: Database Management REST API
Provides CRUD operations for PLC tags including CSV bulk import
"""

from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File
from database.sqlite_manager import SQLiteManager
from .models import TagCreate, TagUpdate, TagResponse, TagImportResult, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from database.validators import (
    validate_plc_exists,
    validate_process_exists,
    validate_polling_group_exists
)
import pandas as pd
import io

router = APIRouter(prefix="/api/tags", tags=["tags"])


# ==============================================================================
# POST /api/tags - Create new tag
# ==============================================================================

@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new PLC tag

    - **plc_id**: ID of PLC connection (must exist)
    - **process_id**: ID of process (must exist)
    - **tag_address**: Tag address (max 20 chars, e.g., D100, W200)
    - **tag_name**: Tag name (max 200 chars)
    - **tag_division**: Optional division (max 50 chars)
    - **data_type**: Data type (default: WORD, max 20 chars)
    - **unit**: Optional unit (max 20 chars)
    - **scale**: Scale factor (default: 1.0)
    - **machine_code**: Optional machine code (max 200 chars)
    - **polling_group_id**: Optional polling group ID
    - **enabled**: Enable/disable flag (default: true)

    Returns created tag with id, created_at, updated_at
    """
    # Validate foreign keys
    validate_plc_exists(db, tag.plc_id)
    validate_process_exists(db, tag.process_id)
    if tag.polling_group_id is not None:
        validate_polling_group_exists(db, tag.polling_group_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tags (
                plc_id, process_id, tag_address, tag_name, tag_division,
                data_type, unit, scale, machine_code, polling_group_id, enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tag.plc_id,
            tag.process_id,
            tag.tag_address,
            tag.tag_name,
            tag.tag_division,
            tag.data_type,
            tag.unit,
            tag.scale,
            tag.machine_code,
            tag.polling_group_id,
            tag.enabled
        ))
        conn.commit()
        tag_id = cursor.lastrowid

    # Log operation
    log_crud_operation("CREATE", "Tag", tag_id, success=True)

    # Return created tag
    return get_tag(tag_id, db)


# ==============================================================================
# GET /api/tags - List all tags with pagination
# ==============================================================================

@router.get("", response_model=PaginatedResponse[TagResponse])
def list_tags(
    plc_id: int = None,
    process_id: int = None,
    polling_group_id: int = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all tags with pagination and filters

    - **plc_id**: Optional filter by PLC ID
    - **process_id**: Optional filter by process ID
    - **polling_group_id**: Optional filter by polling group ID
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of tags
    """
    # Build WHERE clause
    conditions = []
    params = []

    if plc_id:
        conditions.append("plc_id = ?")
        params.append(plc_id)
    if process_id:
        conditions.append("process_id = ?")
        params.append(process_id)
    if polling_group_id:
        conditions.append("polling_group_id = ?")
        params.append(polling_group_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM tags {where_clause}", params)
        total_count = cursor.fetchone()[0]

    # Get paginated tags
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM tags
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, params + [pagination.limit, pagination.skip])
        rows = cursor.fetchall()

    tags = [_row_to_tag_response(row) for row in rows]

    metadata = pagination.get_pagination_metadata(total_count)

    return PaginatedResponse(
        items=tags,
        **metadata
    )


# ==============================================================================
# GET /api/tags/{id} - Get single tag by ID
# ==============================================================================

@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Get a single tag by ID

    - **tag_id**: Tag ID

    Returns tag details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        row = cursor.fetchone()

    if not row:
        raise_not_found("Tag", tag_id)

    return _row_to_tag_response(row)


# ==============================================================================
# PUT /api/tags/{id} - Update tag
# ==============================================================================

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    Update a tag

    - **tag_id**: Tag ID
    - **tag_name**: Optional new tag name
    - **tag_division**: Optional new division
    - **data_type**: Optional new data type
    - **unit**: Optional new unit
    - **scale**: Optional new scale
    - **polling_group_id**: Optional new polling group ID
    - **enabled**: Optional enable/disable flag

    Returns updated tag
    """
    # Check tag exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
        if not cursor.fetchone():
            raise_not_found("Tag", tag_id)

    # Validate polling group if provided
    if tag_update.polling_group_id is not None:
        validate_polling_group_exists(db, tag_update.polling_group_id)

    # Build update query
    updates = []
    params = []

    if tag_update.tag_name is not None:
        updates.append("tag_name = ?")
        params.append(tag_update.tag_name)

    if tag_update.tag_division is not None:
        updates.append("tag_division = ?")
        params.append(tag_update.tag_division)

    if tag_update.data_type is not None:
        updates.append("data_type = ?")
        params.append(tag_update.data_type)

    if tag_update.unit is not None:
        updates.append("unit = ?")
        params.append(tag_update.unit)

    if tag_update.scale is not None:
        updates.append("scale = ?")
        params.append(tag_update.scale)

    if tag_update.polling_group_id is not None:
        updates.append("polling_group_id = ?")
        params.append(tag_update.polling_group_id)

    if tag_update.enabled is not None:
        updates.append("enabled = ?")
        params.append(tag_update.enabled)

    if not updates:
        # No changes, return current tag
        return get_tag(tag_id, db)

    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(tag_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE tags SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    # Log operation
    log_crud_operation("UPDATE", "Tag", tag_id, success=True)

    # Return updated tag
    return get_tag(tag_id, db)


# ==============================================================================
# DELETE /api/tags/{id} - Delete tag
# ==============================================================================

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: SQLiteManager = Depends(get_db)):
    """
    Delete a tag

    - **tag_id**: Tag ID

    Returns 204 No Content on success
    """
    # Check tag exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
        if not cursor.fetchone():
            raise_not_found("Tag", tag_id)

    # Delete tag
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()

    # Log operation
    log_crud_operation("DELETE", "Tag", tag_id, success=True)


# ==============================================================================
# DELETE /api/tags/batch - Batch delete tags
# ==============================================================================

@router.delete("/batch", status_code=status.HTTP_204_NO_CONTENT)
def delete_tags_batch(tag_ids: List[int], db: SQLiteManager = Depends(get_db)):
    """
    Batch delete multiple tags

    - **tag_ids**: List of tag IDs to delete

    Returns 204 No Content on success
    """
    if not tag_ids:
        return

    with db.get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(tag_ids))
        cursor.execute(f"DELETE FROM tags WHERE id IN ({placeholders})", tag_ids)
        conn.commit()
        deleted_count = cursor.rowcount

    # Log operation
    log_crud_operation("BATCH_DELETE", "Tag", success=True, error=f"Deleted {deleted_count} tags")


# ==============================================================================
# POST /api/tags/import-csv - Import tags from CSV file
# ==============================================================================

@router.post("/import-csv", response_model=TagImportResult)
async def import_tags_csv(
    file: UploadFile = File(...),
    db: SQLiteManager = Depends(get_db)
):
    """
    Import tags from CSV file

    CSV format (columns):
    - PLC_CODE: PLC code (required) - will be resolved to plc_id
    - PROCESS_CODE: Process code (required) - will be resolved to process_id
    - TAG_ADDRESS: Tag address (required, max 20 chars)
    - TAG_NAME: Tag name (required, max 200 chars)
    - TAG_DIVISION: Division (optional, max 50 chars)
    - DATA_TYPE: Data type (optional, default: WORD)
    - UNIT: Unit (optional, max 20 chars)
    - SCALE: Scale factor (optional, default: 1.0)
    - MACHINE_CODE: Machine code (optional, max 200 chars)
    - ENABLED: Enabled flag (optional, default: 1)

    Performance:
    - Processes in chunks of 1000 rows for optimal performance
    - Target: 3000 tags in <30 seconds

    Returns import result with success count, failure count, and errors
    """
    success_count = 0
    failure_count = 0
    errors = []

    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Validate required columns
        required_cols = ['PLC_CODE', 'PROCESS_CODE', 'TAG_ADDRESS', 'TAG_NAME']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return TagImportResult(
                success_count=0,
                failure_count=len(df),
                errors=[{"row": 0, "error": f"Missing required columns: {', '.join(missing_cols)}"}]
            )

        # Build PLC_CODE → plc_id lookup
        plc_lookup = _build_plc_lookup(db)

        # Build PROCESS_CODE → process_id lookup
        process_lookup = _build_process_lookup(db)

        # Process in chunks of 1000
        chunk_size = 1000
        total_rows = len(df)

        for chunk_start in range(0, total_rows, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_rows)
            chunk = df.iloc[chunk_start:chunk_end]

            # Prepare batch insert
            batch_data = []

            for idx, row in chunk.iterrows():
                row_num = idx + 2  # CSV row number (1-indexed, +1 for header)

                try:
                    # Resolve PLC_CODE to plc_id
                    plc_code = str(row['PLC_CODE']).strip()
                    if plc_code not in plc_lookup:
                        errors.append({"row": row_num, "error": f"PLC_CODE '{plc_code}' not found"})
                        failure_count += 1
                        continue
                    plc_id = plc_lookup[plc_code]

                    # Resolve PROCESS_CODE to process_id
                    process_code = str(row['PROCESS_CODE']).strip()
                    if process_code not in process_lookup:
                        errors.append({"row": row_num, "error": f"PROCESS_CODE '{process_code}' not found"})
                        failure_count += 1
                        continue
                    process_id = process_lookup[process_code]

                    # Extract fields
                    tag_address = str(row['TAG_ADDRESS']).strip()
                    tag_name = str(row['TAG_NAME']).strip()
                    tag_division = str(row.get('TAG_DIVISION', '')).strip() or None
                    data_type = str(row.get('DATA_TYPE', 'WORD')).strip()
                    unit = str(row.get('UNIT', '')).strip() or None
                    scale = float(row.get('SCALE', 1.0))
                    machine_code = str(row.get('MACHINE_CODE', '')).strip() or None
                    enabled = int(row.get('ENABLED', 1))

                    batch_data.append((
                        plc_id, process_id, tag_address, tag_name, tag_division,
                        data_type, unit, scale, machine_code, None, enabled
                    ))

                except Exception as e:
                    errors.append({"row": row_num, "error": str(e)})
                    failure_count += 1

            # Batch insert chunk
            if batch_data:
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.executemany("""
                            INSERT INTO tags (
                                plc_id, process_id, tag_address, tag_name, tag_division,
                                data_type, unit, scale, machine_code, polling_group_id, enabled
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, batch_data)
                        conn.commit()
                        success_count += len(batch_data)

                except Exception as e:
                    # If batch insert fails, try individual inserts to identify specific errors
                    for i, data in enumerate(batch_data):
                        row_num = chunk_start + i + 2
                        try:
                            with db.get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO tags (
                                        plc_id, process_id, tag_address, tag_name, tag_division,
                                        data_type, unit, scale, machine_code, polling_group_id, enabled
                                    )
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, data)
                                conn.commit()
                                success_count += 1
                        except Exception as e2:
                            errors.append({"row": row_num, "error": str(e2)})
                            failure_count += 1

        # Log operation
        log_crud_operation("CSV_IMPORT", "Tag", success=True, error=f"Imported {success_count} tags, {failure_count} failures")

        return TagImportResult(
            success_count=success_count,
            failure_count=failure_count,
            errors=errors[:100]  # Limit to first 100 errors
        )

    except Exception as e:
        return TagImportResult(
            success_count=0,
            failure_count=0,
            errors=[{"row": 0, "error": f"File processing error: {str(e)}"}]
        )


# ==============================================================================
# Helper Functions
# ==============================================================================

def _row_to_tag_response(row) -> TagResponse:
    """Convert database row to TagResponse"""
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


def _build_plc_lookup(db: SQLiteManager) -> dict:
    """Build PLC_CODE → plc_id lookup dictionary"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, plc_code FROM plc_connections")
        return {row[1]: row[0] for row in cursor.fetchall()}


def _build_process_lookup(db: SQLiteManager) -> dict:
    """Build PROCESS_CODE → process_id lookup dictionary"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, process_code FROM processes")
        return {row[1]: row[0] for row in cursor.fetchall()}
