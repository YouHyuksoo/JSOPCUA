"""
FastAPI Dependencies for Database Management API

Feature 5: Database Management REST API
Provides dependency injection for database sessions, pagination, and logging
"""

from typing import Optional
from fastapi import Query
from database.sqlite_manager import SQLiteManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Database path (same as Feature 1)
DB_PATH = "backend/config/scada.db"


# ==============================================================================
# Database Dependency
# ==============================================================================

def get_db():
    """
    Dependency for database access

    Yields:
        SQLiteManager instance

    Usage:
        @app.get("/api/lines")
        def get_lines(db: SQLiteManager = Depends(get_db)):
            ...
    """
    db = SQLiteManager(DB_PATH)
    try:
        yield db
    finally:
        # SQLiteManager uses context managers, no explicit cleanup needed
        pass


# ==============================================================================
# Pagination Dependency
# ==============================================================================

class PaginationParams:
    """
    Pagination parameters for list endpoints

    Attributes:
        page: Page number (1-indexed)
        limit: Items per page (max 1000)
        skip: Items to skip (calculated)
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        limit: int = Query(50, ge=1, le=1000, description="Items per page (max 1000)")
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit

    def get_pagination_metadata(self, total_count: int) -> dict:
        """
        Generate pagination metadata for response

        Args:
            total_count: Total number of items

        Returns:
            Dictionary with pagination metadata
        """
        total_pages = (total_count + self.limit - 1) // self.limit  # Ceiling division

        return {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": self.page,
            "page_size": self.limit
        }


# ==============================================================================
# Logging Helpers
# ==============================================================================

def log_crud_operation(
    operation: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    success: bool = True,
    error: str = None
):
    """
    Log CRUD operation for auditing

    Args:
        operation: CRUD operation (CREATE, READ, UPDATE, DELETE)
        resource_type: Type of resource (Line, Process, etc.)
        resource_id: Optional ID of the resource
        success: Whether operation succeeded
        error: Optional error message if failed

    Example:
        log_crud_operation("CREATE", "Line", resource_id=1, success=True)
        log_crud_operation("DELETE", "Process", resource_id=5, success=False, error="FK constraint")
    """
    timestamp = datetime.now().isoformat()
    resource_str = f"{resource_type}:{resource_id}" if resource_id else resource_type
    status = "SUCCESS" if success else "FAILED"

    log_message = f"[{timestamp}] {operation} {resource_str} - {status}"
    if error:
        log_message += f" - Error: {error}"

    if success:
        logger.info(log_message)
    else:
        logger.error(log_message)


# ==============================================================================
# Query Parameter Helpers
# ==============================================================================

def get_filter_params(
    enabled: Optional[bool] = Query(None, description="Filter by enabled status")
) -> dict:
    """
    Common filter parameters for list endpoints

    Args:
        enabled: Optional filter for enabled/disabled records

    Returns:
        Dictionary of filter parameters
    """
    filters = {}
    if enabled is not None:
        filters['enabled'] = enabled
    return filters
