"""
Migration: polling_groups.plc_id (INTEGER) → polling_groups.plc_code (VARCHAR)

Changes:
1. Add plc_code column to polling_groups table
2. Populate plc_code from plc_connections using plc_id
3. Drop old plc_id column

실행: python src/scripts/migrate_polling_groups_plc_id_to_code.py
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.sqlite_manager import SQLiteManager
from src.api.dependencies import DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_plc_id_to_code(db_path: str) -> bool:
    """
    Migrate polling_groups table from plc_id (INTEGER FK) to plc_code (VARCHAR)
    """
    try:
        manager = SQLiteManager(db_path)

        logger.info("Starting migration: polling_groups.plc_id → plc_code")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Step 1: Create new polling_groups table with plc_code
            logger.info("Creating new polling_groups table with plc_code...")
            cursor.execute("""
                CREATE TABLE polling_groups_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name VARCHAR(200) NOT NULL,
                    plc_code VARCHAR(50) NOT NULL,
                    polling_mode VARCHAR(20) NOT NULL DEFAULT 'FIXED',
                    polling_interval_ms INTEGER NOT NULL DEFAULT 1000,
                    group_category VARCHAR(50) NOT NULL DEFAULT 'OPERATION',
                    trigger_bit_address VARCHAR(20),
                    trigger_bit_offset INTEGER DEFAULT 0,
                    auto_reset_trigger BOOLEAN DEFAULT 1,
                    priority VARCHAR(20) DEFAULT 'NORMAL',
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Step 2: Copy data, converting plc_id → plc_code
            logger.info("Copying data and converting plc_id to plc_code...")
            cursor.execute("""
                INSERT INTO polling_groups_new (
                    id, group_name, plc_code, polling_mode, polling_interval_ms, group_category,
                    trigger_bit_address, trigger_bit_offset, auto_reset_trigger, priority,
                    description, is_active, created_at, updated_at
                )
                SELECT
                    pg.id,
                    pg.group_name,
                    p.plc_code,
                    pg.polling_mode,
                    pg.polling_interval_ms,
                    pg.group_category,
                    pg.trigger_bit_address,
                    pg.trigger_bit_offset,
                    pg.auto_reset_trigger,
                    pg.priority,
                    pg.description,
                    pg.is_active,
                    pg.created_at,
                    pg.updated_at
                FROM polling_groups pg
                LEFT JOIN plc_connections p ON pg.plc_id = p.id
            """)

            rows_copied = cursor.rowcount
            logger.info(f"Copied {rows_copied} rows")

            # Step 3: Drop old table
            logger.info("Dropping old polling_groups table...")
            cursor.execute("DROP TABLE polling_groups")

            # Step 4: Rename new table
            logger.info("Renaming polling_groups_new to polling_groups...")
            cursor.execute("ALTER TABLE polling_groups_new RENAME TO polling_groups")

            conn.commit()

        logger.info("✓ Migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def validate_migration(db_path: str) -> bool:
    """Validate the migration"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("\nValidating migration...")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Check schema
            cursor.execute("PRAGMA table_info(polling_groups)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}

            if 'plc_id' in columns:
                logger.error("✗ plc_id column still exists!")
                return False

            if 'plc_code' not in columns:
                logger.error("✗ plc_code column not found!")
                return False

            logger.info("✓ Schema is correct")

            # Sample data
            cursor.execute("SELECT id, group_name, plc_code, polling_mode, group_category FROM polling_groups LIMIT 5")
            samples = cursor.fetchall()

            logger.info("Sample data:")
            for row in samples:
                logger.info(f"  ID={row[0]}, name={row[1]}, plc_code={row[2]}, mode={row[3]}, category={row[4]}")

        return True

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


def main():
    """Main migration function"""
    logger.info("=" * 80)
    logger.info("Migration: polling_groups.plc_id → plc_code")
    logger.info("=" * 80)

    db_path = str(DB_PATH)
    logger.info(f"Database: {db_path}")

    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False

    # Run migration
    if not migrate_plc_id_to_code(db_path):
        logger.error("\n✗ Migration failed")
        return False

    # Validate
    if not validate_migration(db_path):
        logger.error("\n✗ Validation failed")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✓ Migration completed successfully!")
    logger.info("=" * 80)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
