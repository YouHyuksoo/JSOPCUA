"""
Migration: tags.plc_id (INTEGER) → tags.plc_code (VARCHAR)

Changes:
1. Add plc_code column to tags table (already exists from previous addition)
2. Populate plc_code from plc_connections using plc_id
3. Drop old plc_id column
4. Recreate table without plc_id foreign key

실행: python src/scripts/migrate_tags_plc_id_to_code.py
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


def migrate_plc_id_to_code(db_path: str) -> bool:
    """
    Migrate tags table from plc_id (INTEGER FK) to plc_code (VARCHAR)

    Steps:
    1. Create new tags table with plc_code instead of plc_id
    2. Copy all data, converting plc_id → plc_code via JOIN
    3. Drop old table
    4. Rename new table
    """
    try:
        manager = SQLiteManager(db_path)

        logger.info("Starting migration: plc_id → plc_code")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Step 0: Drop views that reference tags table
            logger.info("Dropping views that reference tags table...")
            cursor.execute("DROP VIEW IF EXISTS v_tags_with_plc")

            # Step 1: Create new tags table with plc_code
            logger.info("Creating new tags table with plc_code...")
            cursor.execute("""
                CREATE TABLE tags_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plc_code VARCHAR(50) NOT NULL,
                    process_id INTEGER,
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

            # Step 2: Copy data from old table, converting plc_id → plc_code
            logger.info("Copying data and converting plc_id to plc_code...")
            cursor.execute("""
                INSERT INTO tags_new (
                    id, plc_code, process_id, tag_address, tag_name, tag_type,
                    unit, scale, offset, min_value, max_value, polling_group_id,
                    description, is_active, last_value, last_updated_at,
                    created_at, updated_at, tag_category, log_mode, machine_code
                )
                SELECT
                    t.id,
                    p.plc_code,
                    t.process_id,
                    t.tag_address,
                    t.tag_name,
                    t.tag_type,
                    t.unit,
                    t.scale,
                    t.offset,
                    t.min_value,
                    t.max_value,
                    t.polling_group_id,
                    t.description,
                    t.is_active,
                    t.last_value,
                    t.last_updated_at,
                    t.created_at,
                    t.updated_at,
                    t.tag_category,
                    t.log_mode,
                    t.machine_code
                FROM tags t
                LEFT JOIN plc_connections p ON t.plc_id = p.id
            """)

            rows_copied = cursor.rowcount
            logger.info(f"Copied {rows_copied} rows")

            # Step 3: Drop old table
            logger.info("Dropping old tags table...")
            cursor.execute("DROP TABLE tags")

            # Step 4: Rename new table
            logger.info("Renaming tags_new to tags...")
            cursor.execute("ALTER TABLE tags_new RENAME TO tags")

            # Step 5: Recreate views
            logger.info("Recreating v_tags_with_plc view...")
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

        logger.info("✓ Migration completed successfully")
        logger.info("✓ v_tags_with_plc view recreated")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def validate_migration(db_path: str) -> bool:
    """Validate the migration was successful"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("\nValidating migration...")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Check schema
            cursor.execute("PRAGMA table_info(tags)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}

            if 'plc_id' in columns:
                logger.error("✗ plc_id column still exists!")
                return False

            if 'plc_code' not in columns:
                logger.error("✗ plc_code column not found!")
                return False

            if columns.get('plc_code') != 'VARCHAR(50)':
                logger.error(f"✗ plc_code type is {columns.get('plc_code')}, expected VARCHAR(50)")
                return False

            logger.info("✓ Schema is correct")

            # Check data
            cursor.execute("SELECT COUNT(*) FROM tags WHERE plc_code IS NULL")
            null_count = cursor.fetchone()[0]

            if null_count > 0:
                logger.warning(f"⚠ {null_count} tags have NULL plc_code")

            # Sample data
            cursor.execute("SELECT id, plc_code, tag_address, tag_name FROM tags LIMIT 5")
            samples = cursor.fetchall()

            logger.info("Sample data:")
            for row in samples:
                logger.info(f"  ID={row[0]}, plc_code={row[1]}, address={row[2]}, name={row[3]}")

            # Check unique constraint
            cursor.execute("""
                SELECT plc_code, tag_address, COUNT(*) as cnt
                FROM tags
                GROUP BY plc_code, tag_address
                HAVING cnt > 1
            """)
            duplicates = cursor.fetchall()

            if duplicates:
                logger.error(f"✗ Found {len(duplicates)} duplicate (plc_code, tag_address) combinations!")
                for dup in duplicates:
                    logger.error(f"  {dup[0]}/{dup[1]}: {dup[2]} occurrences")
                return False

            logger.info("✓ No duplicate (plc_code, tag_address) found")

        return True

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


def main():
    """Main migration function"""
    logger.info("=" * 80)
    logger.info("Migration: tags.plc_id (INTEGER) → tags.plc_code (VARCHAR)")
    logger.info("=" * 80)

    db_path = str(DB_PATH)
    logger.info(f"Database: {db_path}")

    # Check if database exists
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False

    # Run migration
    if not migrate_plc_id_to_code(db_path):
        logger.error("\n" + "=" * 80)
        logger.error("✗ Migration failed")
        logger.error("=" * 80)
        return False

    # Validate
    if not validate_migration(db_path):
        logger.error("\n" + "=" * 80)
        logger.error("✗ Migration validation failed")
        logger.error("=" * 80)
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✓ Migration completed and validated successfully!")
    logger.info("=" * 80)
    logger.info("\nNext steps:")
    logger.info("1. Update backend API code (tags_routes.py, polling_groups_routes.py)")
    logger.info("2. Update frontend types (lib/types/tag.ts)")
    logger.info("3. Test tag creation, update, and Oracle sync")
    logger.info("4. Restart backend server")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
