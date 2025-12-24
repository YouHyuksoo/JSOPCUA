"""
Add group_category column to polling_groups table

Migration script to add group_category field to existing polling_groups table.
This allows polling groups to determine whether data goes to XSCADA_OPERATION
or XSCADA_DATATAG_LOG based on group-level configuration.

실행: python src/scripts/add_group_category_migration.py
"""
import sys
from pathlib import Path
import logging
import sqlite3

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.sqlite_manager import SQLiteManager
from src.api.dependencies import DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_column_exists(db_path: str) -> bool:
    """
    Check if group_category column already exists

    Args:
        db_path: Path to SQLite database

    Returns:
        True if column exists, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get table info
        cursor.execute("PRAGMA table_info(polling_groups)")
        columns = cursor.fetchall()

        # Check if group_category exists
        column_names = [col[1] for col in columns]
        exists = 'group_category' in column_names

        conn.close()
        return exists

    except Exception as e:
        logger.error(f"Failed to check column existence: {e}")
        return False


def add_group_category_column(db_path: str) -> bool:
    """
    Add group_category column to polling_groups table

    Args:
        db_path: Path to SQLite database

    Returns:
        True if successful, False otherwise
    """
    try:
        manager = SQLiteManager(db_path)

        logger.info("Adding group_category column to polling_groups table...")

        # Add column with default value 'OPERATION'
        manager.execute_update("""
            ALTER TABLE polling_groups
            ADD COLUMN group_category VARCHAR(20) NOT NULL DEFAULT 'OPERATION'
        """)

        logger.info("✓ Column added successfully")

        # Verify the column was added
        with manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(polling_groups)")
            columns = cursor.fetchall()

            logger.info("\nUpdated polling_groups table schema:")
            for col in columns:
                logger.info(f"  {col[1]} {col[2]}")

        return True

    except Exception as e:
        logger.error(f"Failed to add column: {e}")
        return False


def validate_migration(db_path: str) -> bool:
    """
    Validate the migration was successful

    Args:
        db_path: Path to SQLite database

    Returns:
        True if validation passed, False otherwise
    """
    try:
        manager = SQLiteManager(db_path)

        logger.info("\nValidating migration...")

        # Check that all existing groups have OPERATION as default
        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Count total groups
            cursor.execute("SELECT COUNT(*) FROM polling_groups")
            total_count = cursor.fetchone()[0]

            # Count groups with OPERATION category
            cursor.execute("SELECT COUNT(*) FROM polling_groups WHERE group_category = 'OPERATION'")
            operation_count = cursor.fetchone()[0]

            logger.info(f"Total polling groups: {total_count}")
            logger.info(f"Groups with OPERATION category: {operation_count}")

            if total_count == operation_count:
                logger.info("✓ All existing groups have OPERATION category (default)")
                return True
            else:
                logger.warning(f"✗ Some groups have different category values")
                return False

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("Migration: Add group_category to polling_groups")
    logger.info("=" * 60)

    db_path = str(DB_PATH)
    logger.info(f"Database: {db_path}")

    # Check if database exists
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False

    # Check if column already exists
    if check_column_exists(db_path):
        logger.warning("Column 'group_category' already exists in polling_groups table")
        logger.info("Migration skipped - no changes needed")
        return True

    # Add the column
    success = add_group_category_column(db_path)

    if not success:
        logger.error("✗ Migration failed")
        return False

    # Validate
    validation_success = validate_migration(db_path)

    if validation_success:
        logger.info("\n" + "=" * 60)
        logger.info("✓ Migration completed successfully!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Restart the polling engine to pick up the new schema")
        logger.info("2. Update polling groups to set group_category='ALARM' for alarm groups")
        logger.info("3. Verify Oracle writes go to correct tables based on group_category")
        return True
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ Migration validation failed")
        logger.error("=" * 60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
