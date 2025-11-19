"""
Migration: Rename process → workstage

Changes:
1. tags.process_code → tags.workstage_code
2. processes table → workstages table
3. processes.process_code → workstages.workstage_code

실행: python src/scripts/migrate_process_to_workstage.py
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


def migrate_tags_table(db_path: str) -> bool:
    """Migrate tags table: process_code → workstage_code"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("Step 1: Migrating tags table (process_code → workstage_code)")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Drop views
            logger.info("Dropping views...")
            cursor.execute("DROP VIEW IF EXISTS v_tags_with_plc")

            # Create new tags table with workstage_code
            logger.info("Creating new tags table with workstage_code...")
            cursor.execute("""
                CREATE TABLE tags_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plc_code VARCHAR(50) NOT NULL,
                    workstage_code VARCHAR(50),
                    tag_address VARCHAR(50) NOT NULL,
                    tag_name VARCHAR(100) NOT NULL,
                    tag_type VARCHAR(20) NOT NULL DEFAULT 'INT',
                    unit VARCHAR(20),
                    scale REAL DEFAULT 1.0,
                    offset REAL DEFAULT 0.0,
                    min_value REAL,
                    max_value REAL,
                    polling_group_id INTEGER,
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    last_value TEXT,
                    last_updated_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tag_category VARCHAR(50),
                    log_mode VARCHAR(20) NOT NULL DEFAULT 'ALWAYS',
                    machine_code VARCHAR(50),
                    UNIQUE(plc_code, tag_address),
                    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id)
                )
            """)

            # Copy data: process_code → workstage_code
            logger.info("Copying data (process_code → workstage_code)...")
            cursor.execute("""
                INSERT INTO tags_new
                SELECT
                    id, plc_code, process_code as workstage_code, tag_address, tag_name, tag_type,
                    unit, scale, offset, min_value, max_value, polling_group_id,
                    description, is_active, last_value, last_updated_at,
                    created_at, updated_at, tag_category, log_mode, machine_code
                FROM tags
            """)

            rows = cursor.rowcount
            logger.info(f"Copied {rows} rows")

            # Drop old, rename new
            cursor.execute("DROP TABLE tags")
            cursor.execute("ALTER TABLE tags_new RENAME TO tags")

            # Recreate view
            logger.info("Recreating view...")
            cursor.execute("""
                CREATE VIEW v_tags_with_plc AS
                SELECT
                    t.*,
                    p.plc_name,
                    p.ip_address,
                    p.port
                FROM tags t
                LEFT JOIN plc_connections p ON t.plc_code = p.plc_code
            """)

            conn.commit()

        logger.info("✓ Tags table migrated")
        return True

    except Exception as e:
        logger.error(f"Failed to migrate tags table: {e}")
        return False


def migrate_processes_table(db_path: str) -> bool:
    """Rename processes → workstages, process_code → workstage_code"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("Step 2: Migrating processes → workstages")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Create workstages table
            logger.info("Creating workstages table...")
            cursor.execute("""
                CREATE TABLE workstages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workstage_code VARCHAR(50) NOT NULL UNIQUE,
                    workstage_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    sequence_order INTEGER DEFAULT 0,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Copy data: process_code → workstage_code
            logger.info("Copying data from processes...")
            cursor.execute("""
                INSERT INTO workstages (
                    id, workstage_code, workstage_name, description,
                    sequence_order, is_active, created_at, updated_at
                )
                SELECT
                    id, process_code, process_name, description,
                    sequence_order, is_active, created_at, updated_at
                FROM processes
            """)

            rows = cursor.rowcount
            logger.info(f"Copied {rows} rows")

            # Drop old processes table
            logger.info("Dropping old processes table...")
            cursor.execute("DROP TABLE processes")

            conn.commit()

        logger.info("✓ Processes table renamed to workstages")
        return True

    except Exception as e:
        logger.error(f"Failed to migrate processes table: {e}")
        return False


def validate_migration(db_path: str) -> bool:
    """Validate migration"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("\nValidating migration...")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Check tags table
            cursor.execute("PRAGMA table_info(tags)")
            tag_columns = {col[1] for col in cursor.fetchall()}

            if 'process_code' in tag_columns:
                logger.error("✗ tags.process_code still exists!")
                return False

            if 'workstage_code' not in tag_columns:
                logger.error("✗ tags.workstage_code not found!")
                return False

            logger.info("✓ tags table schema correct")

            # Check workstages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workstages'")
            if not cursor.fetchone():
                logger.error("✗ workstages table not found!")
                return False

            logger.info("✓ workstages table exists")

            # Check processes table dropped
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processes'")
            if cursor.fetchone():
                logger.error("✗ processes table still exists!")
                return False

            logger.info("✓ processes table dropped")

            # Sample data
            cursor.execute("SELECT id, plc_code, workstage_code, machine_code, tag_address FROM tags LIMIT 3")
            samples = cursor.fetchall()

            logger.info("\nSample tags:")
            for row in samples:
                logger.info(f"  ID={row[0]}, plc={row[1]}, workstage={row[2]}, machine={row[3]}, addr={row[4]}")

            cursor.execute("SELECT id, workstage_code, workstage_name FROM workstages LIMIT 3")
            samples = cursor.fetchall()

            logger.info("\nSample workstages:")
            for row in samples:
                logger.info(f"  ID={row[0]}, code={row[1]}, name={row[2]}")

        return True

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


def main():
    """Main migration"""
    logger.info("=" * 80)
    logger.info("Migration: process → workstage")
    logger.info("=" * 80)

    db_path = str(DB_PATH)
    logger.info(f"Database: {db_path}")

    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False

    # Step 1: Migrate tags table
    if not migrate_tags_table(db_path):
        logger.error("\n✗ Tags migration failed")
        return False

    # Step 2: Migrate processes table
    if not migrate_processes_table(db_path):
        logger.error("\n✗ Processes migration failed")
        return False

    # Validate
    if not validate_migration(db_path):
        logger.error("\n✗ Validation failed")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✓ Migration completed successfully!")
    logger.info("=" * 80)
    logger.info("\nChanges:")
    logger.info("  - tags.process_code → tags.workstage_code")
    logger.info("  - processes table → workstages table")
    logger.info("  - process_code → workstage_code")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
