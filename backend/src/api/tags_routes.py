"""
Tags API Routes

Feature 5: Database Management REST API
Provides CRUD operations for PLC tags including CSV bulk import
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from src.database.sqlite_manager import SQLiteManager
from .models import TagCreate, TagUpdate, TagResponse, TagImportResult, PaginatedResponse
from .dependencies import get_db, PaginationParams, log_crud_operation
from .exceptions import raise_not_found
from src.database.validators import (
    validate_polling_group_exists
)
import pandas as pd
import io
from datetime import datetime

router = APIRouter(prefix="/api/tags", tags=["tags"])


# ==============================================================================
# POST /api/tags - Create new tag
# ==============================================================================

@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: SQLiteManager = Depends(get_db)):
    """
    Create a new PLC tag

    - **plc_code**: PLC code (must not be empty)
    - **machine_code**: Machine code (must not be empty)
    - **tag_address**: Tag address (max 20 chars, e.g., D100, W200)
    - **tag_name**: Tag name (max 200 chars)
    - **tag_division**: Optional division (max 50 chars)
    - **data_type**: Data type (default: WORD, max 20 chars)
    - **unit**: Optional unit (max 20 chars)
    - **scale**: Scale factor (default: 1.0)
    - **polling_group_id**: Optional polling group ID
    - **enabled**: Enable/disable flag (default: true)

    Returns created tag with id, created_at, updated_at
    """
    # Validate codes are not empty
    if not tag.plc_code or not tag.plc_code.strip():
        raise HTTPException(status_code=400, detail="plc_code cannot be empty")

    if not tag.machine_code or not tag.machine_code.strip():
        raise HTTPException(status_code=400, detail="machine_code cannot be empty")

    if tag.polling_group_id is not None:
        validate_polling_group_exists(db, tag.polling_group_id)

    # 태그명이 "unknown"이면 is_active를 'N'으로 설정
    is_active = tag.enabled
    if tag.tag_name and tag.tag_name.lower() == "unknown":
        is_active = False

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tags (
                plc_code, polling_group_id, tag_address, tag_name, tag_type,
                unit, scale, machine_code, log_mode, description, is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tag.plc_code.strip(),
            tag.polling_group_id,
            tag.tag_address,
            tag.tag_name,
            tag.data_type,  # tag_type
            tag.unit,
            tag.scale,
            tag.machine_code.strip(),
            tag.log_mode,  # log_mode
            tag.tag_division,  # description
            is_active  # is_active (unknown이면 False)
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
    plc_code: Optional[str] = None,
    machine_code: Optional[str] = None,
    polling_group_id: Optional[int] = None,
    tag_category: Optional[str] = None,
    is_active: Optional[bool] = None,
    pagination: PaginationParams = Depends(),
    db: SQLiteManager = Depends(get_db)
):
    """
    List all tags with pagination and filters

    - **plc_code**: Optional filter by PLC code
    - **machine_code**: Optional filter by machine code
    - **polling_group_id**: Optional filter by polling group ID
    - **tag_category**: Optional filter by tag category (tag type)
    - **is_active**: Optional filter by active status (true/false)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 1000)

    Returns paginated list of tags
    """
    # Build WHERE clause
    conditions = []
    params = []

    if plc_code:
        conditions.append("t.plc_code = ?")
        params.append(plc_code)
    if machine_code:
        conditions.append("t.machine_code = ?")
        params.append(machine_code)
    if polling_group_id:
        conditions.append("t.polling_group_id = ?")
        params.append(polling_group_id)
    if tag_category:
        conditions.append("t.tag_category = ?")
        params.append(tag_category)
    if is_active is not None:
        conditions.append("t.is_active = ?")
        params.append(1 if is_active else 0)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Get total count
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM tags t {where_clause}", params)
        total_count = cursor.fetchone()[0]

    # Get paginated tags
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT t.*
            FROM tags t
            {where_clause}
            ORDER BY t.id DESC
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
# GET /api/tags/tag-categories - Get distinct tag categories
# ==============================================================================

@router.get("/tag-categories")
def get_tag_categories(db: SQLiteManager = Depends(get_db)):
    """
    Get list of distinct tag categories (tag types) from database

    Returns list of unique tag_category values for filter dropdown
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT tag_category
            FROM tags
            WHERE tag_category IS NOT NULL AND tag_category != ''
            ORDER BY tag_category
        """)
        rows = cursor.fetchall()

    categories = [row[0] for row in rows]
    return {"categories": categories}


# ==============================================================================
# Oracle Synchronization APIs (MUST be before /{tag_id} route)
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
def sync_tags_from_oracle(db: SQLiteManager = Depends(get_db)):
    """
    Synchronize tags from Oracle ICOM_PLC_TAG_MASTER table to SQLite tags

    매핑: ICOM_PLC_TAG_MASTER (Oracle) → tags (SQLite)

    This endpoint:
    1. Fetches all active tags (TAG_USE_YN='Y') from Oracle ICOM_PLC_TAG_MASTER
    2. For each Oracle tag:
       - Uses plc_code, machine_code directly from Oracle
       - If tag exists (by plc_code + tag_address): UPDATE
       - If tag doesn't exist: INSERT
    3. Returns sync statistics

    Returns:
        {
            "success": true,
            "total_oracle_tags": 100,
            "created": 50,
            "updated": 30,
            "skipped": 20,
            "errors": 0,
            "error_details": []
        }
    """
    from src.oracle_writer.oracle_helper import get_oracle_tags
    from src.config.logging_config import get_logger

    logger = get_logger(__name__)

    try:
        # Fetch tags from Oracle
        logger.info("Starting Oracle tag synchronization...")
        oracle_tags = get_oracle_tags()
        logger.info(f"Fetched {len(oracle_tags)} tags from Oracle")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        error_details = []

        with db.get_connection() as conn:
            cursor = conn.cursor()

            for oracle_tag in oracle_tags:
                plc_code = oracle_tag['plc_code']
                machine_code = oracle_tag.get('machine_code')
                tag_address = oracle_tag['tag_address']
                tag_name = oracle_tag['tag_name'] or 'UNKNOWN'  # NULL 값을 'UNKNOWN'으로 대체
                tag_category = oracle_tag.get('tag_category')  # Oracle TAG_TYPE → tag_category
                tag_type = oracle_tag['tag_type']  # Oracle TAG_DATA_TYPE → tag_type
                unit = oracle_tag.get('unit', '')
                scale = oracle_tag.get('scale', 1.0)
                min_value = oracle_tag.get('min_value')
                max_value = oracle_tag.get('max_value')

                try:
                    # Validate required codes
                    if not plc_code or not plc_code.strip():
                        error_count += 1
                        error_msg = f"Missing plc_code for tag {tag_address}"
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                        continue

                    if not machine_code or not machine_code.strip():
                        error_count += 1
                        error_msg = f"Missing machine_code for tag {tag_address}"
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                        continue

                    # Check if tag exists
                    cursor.execute(
                        "SELECT id FROM tags WHERE plc_code = ? AND tag_address = ?",
                        (plc_code, tag_address)
                    )
                    existing = cursor.fetchone()

                    # 태그명이 "unknown"이면 is_active=0, 아니면 1
                    is_active = 0 if tag_name.lower() == "unknown" else 1

                    if existing:
                        # UPDATE existing tag
                        cursor.execute("""
                            UPDATE tags
                            SET tag_name = ?,
                                tag_category = ?,
                                tag_type = ?,
                                unit = ?,
                                scale = ?,
                                min_value = ?,
                                max_value = ?,
                                machine_code = ?,
                                is_active = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE plc_code = ? AND tag_address = ?
                        """, (tag_name, tag_category, tag_type, unit, scale, min_value, max_value,
                              machine_code, is_active, plc_code, tag_address))
                        updated_count += 1
                        logger.debug(f"Updated tag: {plc_code}/{tag_address}")

                    else:
                        # INSERT new tag
                        cursor.execute("""
                            INSERT INTO tags
                            (plc_code, tag_address, tag_name, tag_category, tag_type,
                             unit, scale, min_value, max_value, machine_code, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (plc_code, tag_address, tag_name, tag_category, tag_type,
                              unit, scale, min_value, max_value, machine_code, is_active))
                        created_count += 1
                        logger.debug(f"Created tag: {plc_code}/{tag_address}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Error processing tag {plc_code}/{tag_address}: {str(e)}"
                    error_details.append(error_msg)
                    logger.error(error_msg)
                    continue

            # Commit all changes
            conn.commit()

        logger.info(
            f"Tag sync completed: {created_count} created, "
            f"{updated_count} updated, {error_count} errors"
        )

        return {
            "success": True,
            "total_oracle_tags": len(oracle_tags),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_count,
            "error_details": error_details
        }

    except Exception as e:
        logger.error(f"Oracle tag sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync tags from Oracle: {str(e)}"
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

        # 태그명이 "unknown"이면 is_active를 False로 설정
        if tag_update.tag_name.lower() == "unknown":
            updates.append("is_active = ?")
            params.append(False)

    if tag_update.tag_division is not None:
        updates.append("description = ?")
        params.append(tag_update.tag_division)

    if tag_update.data_type is not None:
        updates.append("tag_type = ?")
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

    if tag_update.log_mode is not None:
        updates.append("log_mode = ?")
        params.append(tag_update.log_mode)

    if tag_update.enabled is not None:
        # tag_name이 "unknown"이면 enabled 무시
        if tag_update.tag_name and tag_update.tag_name.lower() == "unknown":
            pass  # is_active는 이미 False로 설정됨
        else:
            updates.append("is_active = ?")
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
    - PLC_CODE: PLC code (required)
    - MACHINE_CODE: Machine code (required, max 200 chars)
    - TAG_ADDRESS: Tag address (required, max 20 chars)
    - TAG_NAME: Tag name (required, max 200 chars)
    - TAG_DIVISION: Division (optional, max 50 chars)
    - DATA_TYPE: Data type (optional, default: WORD)
    - UNIT: Unit (optional, max 20 chars)
    - SCALE: Scale factor (optional, default: 1.0)
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
        required_cols = ['PLC_CODE', 'MACHINE_CODE', 'TAG_ADDRESS', 'TAG_NAME']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return TagImportResult(
                success_count=0,
                failure_count=len(df),
                errors=[{"row": 0, "error": f"Missing required columns: {', '.join(missing_cols)}"}]
            )

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
                    # Get codes directly
                    plc_code = str(row['PLC_CODE']).strip()
                    machine_code = str(row['MACHINE_CODE']).strip()

                    # Validate codes are not empty
                    if not plc_code:
                        errors.append({"row": row_num, "error": "PLC_CODE cannot be empty"})
                        failure_count += 1
                        continue

                    if not machine_code:
                        errors.append({"row": row_num, "error": "MACHINE_CODE cannot be empty"})
                        failure_count += 1
                        continue

                    # Extract fields
                    tag_address = str(row['TAG_ADDRESS']).strip()
                    tag_name = str(row['TAG_NAME']).strip()
                    tag_division = str(row.get('TAG_DIVISION', '')).strip() or None
                    data_type = str(row.get('DATA_TYPE', 'WORD')).strip()
                    unit = str(row.get('UNIT', '')).strip() or None
                    scale = float(row.get('SCALE', 1.0))
                    enabled = int(row.get('ENABLED', 1))

                    # 태그명이 "unknown"이면 is_active=0으로 설정
                    if tag_name.lower() == "unknown":
                        enabled = 0

                    batch_data.append((
                        plc_code, None, tag_address, tag_name, data_type,
                        unit, scale, machine_code, tag_division, enabled
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
                                plc_code, polling_group_id, tag_address, tag_name, tag_type,
                                unit, scale, machine_code, description, is_active
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                                        plc_code, polling_group_id, tag_address, tag_name, tag_type,
                                        unit, scale, machine_code, description, is_active
                                    )
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    # Row format (plc_code, machine_code):
    # (0:id, 1:plc_code, 2:machine_code, 3:tag_address, 4:tag_name, 5:tag_type, 6:unit,
    #  7:scale, 8:offset, 9:min_value, 10:max_value, 11:polling_group_id, 12:description,
    #  13:is_active, 14:last_value, 15:last_updated_at, 16:created_at, 17:updated_at,
    #  18:tag_category, 19:log_mode)
    return TagResponse(
        id=row[0],
        plc_code=row[1] if row[1] else '',
        machine_code=row[2] if row[2] else '',
        tag_address=row[3],
        tag_name=row[4],
        tag_division=row[12] if row[12] else '',  # description
        tag_category=row[18] if len(row) > 18 and row[18] else None,  # tag_category
        data_type=row[5],  # tag_type
        unit=str(row[6]) if row[6] else None,
        scale=float(row[7]) if row[7] is not None else 1.0,
        polling_group_id=row[11],
        enabled=bool(row[13]),  # is_active
        created_at=row[16] if row[16] else datetime.now().isoformat(),
        updated_at=row[17] if row[17] else datetime.now().isoformat()
    )
