"""
Database Validation Functions

Feature 5: Database Management REST API
Provides business logic validation for database operations
"""

import re
import ipaddress
from typing import Optional
from src.database.sqlite_manager import SQLiteManager
from src.api.exceptions import ForeignKeyError, ValidationError


# ==============================================================================
# Process Code Validation
# ==============================================================================

def validate_process_code(code: str) -> bool:
    """
    Validate 14-character process code format

    Format: [A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3}
    Example: KRCWO12ELOA101
    - KR: Country code (2 chars)
    - CWO: Factory code (3 chars)
    - 12: Line number (2 digits)
    - ELO: Equipment type (3 chars)
    - A: Category (1 char)
    - 101: Sequence (3 digits)

    Args:
        code: Process code to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If code format is invalid
    """
    if len(code) != 14:
        raise ValidationError(
            message="Invalid process code",
            detail=f"process_code must be exactly 14 characters, got {len(code)}"
        )

    pattern = r'^[A-Z]{2}[A-Z]{3}\d{2}[A-Z]{3}[A-Z]\d{3}$'
    if not re.match(pattern, code):
        raise ValidationError(
            message="Invalid process code format",
            detail="process_code must match pattern: [A-Z]{2}[A-Z]{3}\\d{2}[A-Z]{3}[A-Z]\\d{3}"
        )

    return True


# ==============================================================================
# IP Address Validation
# ==============================================================================

def validate_ipv4_address(ip: str) -> bool:
    """
    Validate IPv4 address format

    Args:
        ip: IP address string

    Returns:
        True if valid

    Raises:
        ValidationError: If IP format is invalid
    """
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        raise ValidationError(
            message="Invalid IP address",
            detail=f"'{ip}' is not a valid IPv4 address"
        )


# ==============================================================================
# Foreign Key Validation
# ==============================================================================

def validate_machine_exists(db: SQLiteManager, machine_code: str) -> bool:
    """
    Validate that machine exists by machine_code

    Args:
        db: Database manager
        machine_code: Machine code to check

    Returns:
        True if exists

    Raises:
        ForeignKeyError: If machine not found
    """
    if machine_code is None:
        return True  # machine_code is optional
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT machine_code FROM machines WHERE machine_code = ?", (machine_code,))
        if not cursor.fetchone():
            raise ForeignKeyError(
                message="Machine not found",
                detail=f"machine_code '{machine_code}' not found"
            )
    return True


def validate_process_exists(db: SQLiteManager, process_id: int) -> bool:
    """
    Validate that process exists

    Args:
        db: Database manager
        process_id: Process ID to check

    Returns:
        True if exists

    Raises:
        ForeignKeyError: If process not found
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM processes WHERE id = ?", (process_id,))
        if not cursor.fetchone():
            raise ForeignKeyError(
                message="Process not found",
                detail=f"process_id {process_id} not found"
            )
    return True


def validate_plc_exists(db: SQLiteManager, plc_id: int) -> bool:
    """
    Validate that PLC connection exists

    Args:
        db: Database manager
        plc_id: PLC ID to check

    Returns:
        True if exists

    Raises:
        ForeignKeyError: If PLC not found
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM plc_connections WHERE id = ?", (plc_id,))
        if not cursor.fetchone():
            raise ForeignKeyError(
                message="PLC connection not found",
                detail=f"plc_id {plc_id} not found"
            )
    return True


def validate_polling_group_exists(db: SQLiteManager, group_id: int) -> bool:
    """
    Validate that polling group exists

    Args:
        db: Database manager
        group_id: Polling group ID to check

    Returns:
        True if exists

    Raises:
        ForeignKeyError: If group not found
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM polling_groups WHERE id = ?", (group_id,))
        if not cursor.fetchone():
            raise ForeignKeyError(
                message="Polling group not found",
                detail=f"polling_group_id {group_id} not found"
            )
    return True


# ==============================================================================
# Unique Constraint Validation
# ==============================================================================

def validate_machine_code_unique(db: SQLiteManager, machine_code: str, exclude_id: Optional[int] = None) -> bool:
    """
    Validate that machine_code is unique

    Args:
        db: Database manager
        machine_code: Machine code to check
        exclude_id: Optional ID to exclude (for updates)

    Returns:
        True if unique

    Raises:
        ValidationError: If machine_code already exists
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        if exclude_id:
            cursor.execute(
                "SELECT id FROM machines WHERE machine_code = ? AND id != ?",
                (machine_code, exclude_id)
            )
        else:
            cursor.execute("SELECT id FROM machines WHERE machine_code = ?", (machine_code,))

        if cursor.fetchone():
            raise ValidationError(
                message="Duplicate machine code",
                detail=f"machine_code '{machine_code}' already exists"
            )
    return True


def validate_process_code_unique(db: SQLiteManager, process_code: str, exclude_id: Optional[int] = None) -> bool:
    """
    Validate that process_code is unique

    Args:
        db: Database manager
        process_code: Process code to check
        exclude_id: Optional ID to exclude (for updates)

    Returns:
        True if unique

    Raises:
        ValidationError: If process_code already exists
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        if exclude_id:
            cursor.execute(
                "SELECT id FROM processes WHERE process_code = ? AND id != ?",
                (process_code, exclude_id)
            )
        else:
            cursor.execute("SELECT id FROM processes WHERE process_code = ?", (process_code,))

        if cursor.fetchone():
            raise ValidationError(
                message="Duplicate process code",
                detail=f"process_code '{process_code}' already exists"
            )
    return True


def validate_plc_code_unique(db: SQLiteManager, plc_code: str, exclude_id: Optional[int] = None) -> bool:
    """
    Validate that plc_code is unique

    Args:
        db: Database manager
        plc_code: PLC code to check
        exclude_id: Optional ID to exclude (for updates)

    Returns:
        True if unique

    Raises:
        ValidationError: If plc_code already exists
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        if exclude_id:
            cursor.execute(
                "SELECT id FROM plc_connections WHERE plc_code = ? AND id != ?",
                (plc_code, exclude_id)
            )
        else:
            cursor.execute("SELECT id FROM plc_connections WHERE plc_code = ?", (plc_code,))

        if cursor.fetchone():
            raise ValidationError(
                message="Duplicate PLC code",
                detail=f"plc_code '{plc_code}' already exists"
            )
    return True


# ==============================================================================
# Polling Group Validation
# ==============================================================================

def validate_polling_mode(mode: str, trigger_bit_address: Optional[str]) -> bool:
    """
    Validate polling mode and trigger configuration

    Args:
        mode: Polling mode (FIXED or HANDSHAKE)
        trigger_bit_address: Trigger bit address (required for HANDSHAKE)

    Returns:
        True if valid

    Raises:
        ValidationError: If mode invalid or trigger missing for HANDSHAKE
    """
    if mode not in ['FIXED', 'HANDSHAKE']:
        raise ValidationError(
            message="Invalid polling mode",
            detail="mode must be 'FIXED' or 'HANDSHAKE'"
        )

    if mode == 'HANDSHAKE' and not trigger_bit_address:
        raise ValidationError(
            message="Trigger required for HANDSHAKE mode",
            detail="trigger_bit_address is required when mode is 'HANDSHAKE'"
        )

    return True
