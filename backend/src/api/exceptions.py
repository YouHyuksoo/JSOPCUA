"""
Custom Exceptions for Database Management API

Feature 5: Database Management REST API
Provides custom exception classes and handlers for consistent error responses
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import sqlite3
import logging

logger = logging.getLogger(__name__)


# ==============================================================================
# Custom Exception Classes
# ==============================================================================

class DatabaseError(Exception):
    """Base database error"""
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class ResourceNotFoundError(DatabaseError):
    """Resource not found in database"""
    pass


class DuplicateResourceError(DatabaseError):
    """Duplicate resource (unique constraint violation)"""
    pass


class ForeignKeyError(DatabaseError):
    """Foreign key constraint violation"""
    pass


class ValidationError(DatabaseError):
    """Business logic validation error"""
    pass


# ==============================================================================
# Error Response Formatters
# ==============================================================================

def format_error_response(error: str, detail: str, field: str = None) -> dict:
    """
    Format consistent error response

    Args:
        error: Error type/title
        detail: Detailed error message
        field: Optional field name that caused the error

    Returns:
        Dictionary with error, detail, and optional field
    """
    response = {
        "error": error,
        "detail": detail
    }
    if field:
        response["field"] = field
    return response


def format_validation_errors(errors: list) -> dict:
    """
    Format Pydantic validation errors into user-friendly message

    Args:
        errors: List of validation errors from Pydantic

    Returns:
        Formatted error response
    """
    if len(errors) == 1:
        err = errors[0]
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        return format_error_response(
            error="Validation Error",
            detail=err["msg"],
            field=field or None
        )

    # Multiple errors
    error_details = []
    for err in errors:
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        error_details.append(f"{field}: {err['msg']}")

    return format_error_response(
        error="Validation Error",
        detail="; ".join(error_details)
    )


def format_sqlite_error(error: sqlite3.Error) -> dict:
    """
    Format SQLite error into user-friendly message

    Args:
        error: SQLite error

    Returns:
        Formatted error response
    """
    error_msg = str(error).lower()

    # UNIQUE constraint violation
    if "unique" in error_msg:
        # Extract field name from error message
        # Example: "UNIQUE constraint failed: lines.line_code"
        if "." in error_msg:
            parts = error_msg.split(".")
            if len(parts) >= 2:
                field = parts[-1].strip()
                return format_error_response(
                    error="Conflict",
                    detail=f"A record with this {field} already exists",
                    field=field
                )
        return format_error_response(
            error="Conflict",
            detail="A record with these values already exists"
        )

    # FOREIGN KEY constraint violation
    elif "foreign key" in error_msg:
        return format_error_response(
            error="Bad Request",
            detail="Referenced resource not found. Check foreign key values."
        )

    # NOT NULL constraint violation
    elif "not null" in error_msg:
        if "." in error_msg:
            parts = error_msg.split(".")
            if len(parts) >= 2:
                field = parts[-1].strip()
                return format_error_response(
                    error="Bad Request",
                    detail=f"Field '{field}' is required",
                    field=field
                )
        return format_error_response(
            error="Bad Request",
            detail="Required field is missing"
        )

    # Generic database error
    return format_error_response(
        error="Internal Server Error",
        detail="Database operation failed"
    )


# ==============================================================================
# Exception Handlers
# ==============================================================================

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler for Pydantic validation errors (HTTP 422)

    Converts Pydantic validation errors to user-friendly format
    """
    logger.warning(f"Validation error: {exc.errors()}")
    error_response = format_validation_errors(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def sqlite_exception_handler(request: Request, exc: sqlite3.Error):
    """
    Handler for SQLite errors

    Converts SQLite errors to appropriate HTTP status codes and messages
    """
    logger.error(f"SQLite error: {exc}")
    error_response = format_sqlite_error(exc)

    # Determine status code based on error type
    error_msg = str(exc).lower()
    if "unique" in error_msg:
        status_code = status.HTTP_409_CONFLICT
    elif "foreign key" in error_msg or "not null" in error_msg:
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    """Handler for resource not found errors (HTTP 404)"""
    logger.warning(f"Resource not found: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=format_error_response("Not Found", exc.detail)
    )


async def duplicate_resource_handler(request: Request, exc: DuplicateResourceError):
    """Handler for duplicate resource errors (HTTP 409)"""
    logger.warning(f"Duplicate resource: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=format_error_response("Conflict", exc.detail)
    )


async def foreign_key_handler(request: Request, exc: ForeignKeyError):
    """Handler for foreign key constraint errors (HTTP 400)"""
    logger.warning(f"Foreign key error: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=format_error_response("Bad Request", exc.detail)
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    """Handler for business logic validation errors (HTTP 400)"""
    logger.warning(f"Validation error: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=format_error_response("Validation Error", exc.detail)
    )


# ==============================================================================
# Helper Functions
# ==============================================================================

def raise_not_found(resource_type: str, resource_id: int):
    """
    Raise ResourceNotFoundError with formatted message

    Args:
        resource_type: Type of resource (e.g., 'Line', 'Process')
        resource_id: ID of the resource
    """
    raise ResourceNotFoundError(
        message=f"{resource_type} not found",
        detail=f"{resource_type} with id {resource_id} not found"
    )


def raise_duplicate(resource_type: str, field: str, value: str):
    """
    Raise DuplicateResourceError with formatted message

    Args:
        resource_type: Type of resource
        field: Field name that has duplicate value
        value: The duplicate value
    """
    raise DuplicateResourceError(
        message=f"Duplicate {resource_type}",
        detail=f"{resource_type} with {field} '{value}' already exists"
    )


def raise_foreign_key_error(field: str, value: int):
    """
    Raise ForeignKeyError with formatted message

    Args:
        field: Foreign key field name
        value: Foreign key value that doesn't exist
    """
    raise ForeignKeyError(
        message="Foreign key constraint failed",
        detail=f"{field} {value} not found"
    )
