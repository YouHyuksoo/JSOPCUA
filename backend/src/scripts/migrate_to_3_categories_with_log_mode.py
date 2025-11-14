"""
Migration: Add STATE category and log_mode field

Changes:
1. polling_groups.group_category: OPERATION or ALARM → OPERATION, STATE, or ALARM
2. tags.log_mode: NEW field (ALWAYS, ON_CHANGE, NEVER)

실행: python src/scripts/migrate_to_3_categories_with_log_mode.py
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


def check_log_mode_exists(db_path: str) -> bool:
    """Check if log_mode column already exists in tags table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tags)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        exists = 'log_mode' in column_names
        conn.close()
        return exists
    except Exception as e:
        logger.error(f"Failed to check log_mode column: {e}")
        return False


def add_log_mode_column(db_path: str) -> bool:
    """Add log_mode column to tags table"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("Adding log_mode column to tags table...")

        # Add log_mode column with default value 'ALWAYS'
        manager.execute_update("""
            ALTER TABLE tags
            ADD COLUMN log_mode VARCHAR(20) NOT NULL DEFAULT 'ALWAYS'
        """)

        logger.info("✓ log_mode column added successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to add log_mode column: {e}")
        return False


def update_group_category_constraint(db_path: str) -> bool:
    """
    Update group_category constraint to allow STATE

    Note: SQLite doesn't support ALTER COLUMN for CHECK constraints.
    We need to:
    1. Create new table with updated constraint
    2. Copy data
    3. Drop old table
    4. Rename new table
    """
    try:
        manager = SQLiteManager(db_path)

        logger.info("Updating polling_groups.group_category constraint...")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # 0. Drop views that reference old tables
            logger.info("Dropping views that may reference old tables...")
            cursor.execute("DROP VIEW IF EXISTS v_tags_with_plc")

            # 1. Create new table with updated constraint
            cursor.execute("""
                CREATE TABLE polling_groups_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name VARCHAR(50) NOT NULL UNIQUE,
                    plc_id INTEGER NOT NULL,
                    polling_mode VARCHAR(20) NOT NULL CHECK(polling_mode IN ('FIXED', 'HANDSHAKE')),
                    polling_interval_ms INTEGER NOT NULL DEFAULT 1000,
                    group_category VARCHAR(20) NOT NULL DEFAULT 'OPERATION' CHECK(group_category IN ('OPERATION', 'STATE', 'ALARM')),
                    trigger_bit_address VARCHAR(20),
                    trigger_bit_offset INTEGER DEFAULT 0,
                    auto_reset_trigger BOOLEAN DEFAULT 1,
                    priority VARCHAR(20) DEFAULT 'NORMAL',
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE
                )
            """)

            # 2. Copy data from old table (add default 'OPERATION' for group_category)
            cursor.execute("""
                INSERT INTO polling_groups_new (
                    id, group_name, plc_id, polling_mode, polling_interval_ms,
                    group_category, trigger_bit_address, trigger_bit_offset,
                    auto_reset_trigger, priority, description, is_active,
                    created_at, updated_at
                )
                SELECT
                    id, group_name, plc_id, polling_mode, polling_interval_ms,
                    'OPERATION' as group_category, trigger_bit_address, trigger_bit_offset,
                    auto_reset_trigger, priority, description, is_active,
                    created_at, updated_at
                FROM polling_groups
            """)

            # 3. Drop old table
            cursor.execute("DROP TABLE polling_groups")

            # 4. Rename new table
            cursor.execute("ALTER TABLE polling_groups_new RENAME TO polling_groups")

            # 5. Recreate views with correct table references
            logger.info("Recreating v_tags_with_plc view...")
            cursor.execute("""
                CREATE VIEW v_tags_with_plc AS
                SELECT
                    t.*,
                    p.plc_name,
                    p.ip_address,
                    p.port
                FROM tags t
                LEFT JOIN plc_connections p ON t.plc_id = p.id
            """)

            conn.commit()

        logger.info("✓ group_category constraint updated successfully")
        logger.info("✓ v_tags_with_plc view recreated")
        return True

    except Exception as e:
        logger.error(f"Failed to update group_category constraint: {e}")
        return False


def set_default_log_modes(db_path: str) -> bool:
    """
    Set intelligent default log_modes based on group category

    Rules:
    - OPERATION groups: log_mode = ALWAYS (모든 변화 기록)
    - STATE/ALARM groups: log_mode = ON_CHANGE (변화 시만 기록)
    """
    try:
        manager = SQLiteManager(db_path)

        logger.info("Setting intelligent default log_modes...")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Get all tags with their group categories
            cursor.execute("""
                SELECT t.id, pg.group_category
                FROM tags t
                LEFT JOIN polling_groups pg ON t.polling_group_id = pg.id
            """)

            tags = cursor.fetchall()

            operation_count = 0
            state_alarm_count = 0
            no_group_count = 0

            for tag_id, group_category in tags:
                if group_category == 'OPERATION':
                    # OPERATION: Always log
                    cursor.execute("""
                        UPDATE tags
                        SET log_mode = 'ALWAYS'
                        WHERE id = ?
                    """, (tag_id,))
                    operation_count += 1

                elif group_category in ('STATE', 'ALARM'):
                    # STATE/ALARM: Log on change only
                    cursor.execute("""
                        UPDATE tags
                        SET log_mode = 'ON_CHANGE'
                        WHERE id = ?
                    """, (tag_id,))
                    state_alarm_count += 1

                else:
                    # No group assigned: Default to ALWAYS
                    cursor.execute("""
                        UPDATE tags
                        SET log_mode = 'ALWAYS'
                        WHERE id = ?
                    """, (tag_id,))
                    no_group_count += 1

            conn.commit()

        logger.info(f"✓ Default log_modes set:")
        logger.info(f"  - OPERATION tags: {operation_count} → ALWAYS")
        logger.info(f"  - STATE/ALARM tags: {state_alarm_count} → ON_CHANGE")
        logger.info(f"  - No group tags: {no_group_count} → ALWAYS")

        return True

    except Exception as e:
        logger.error(f"Failed to set default log_modes: {e}")
        return False


def validate_migration(db_path: str) -> bool:
    """Validate the migration was successful"""
    try:
        manager = SQLiteManager(db_path)

        logger.info("\nValidating migration...")

        with manager.get_connection() as conn:
            cursor = conn.cursor()

            # Check tags.log_mode
            cursor.execute("PRAGMA table_info(tags)")
            tags_columns = [col[1] for col in cursor.fetchall()]

            if 'log_mode' not in tags_columns:
                logger.error("✗ tags.log_mode column not found")
                return False

            logger.info("✓ tags.log_mode column exists")

            # Check log_mode distribution
            cursor.execute("""
                SELECT log_mode, COUNT(*) as count
                FROM tags
                GROUP BY log_mode
            """)

            log_mode_stats = cursor.fetchall()
            logger.info("Log mode distribution:")
            for mode, count in log_mode_stats:
                logger.info(f"  - {mode}: {count} tags")

            # Check group_category constraint (try to insert invalid value)
            try:
                cursor.execute("""
                    INSERT INTO polling_groups (group_name, plc_id, polling_mode, group_category)
                    VALUES ('TEST_INVALID', 1, 'FIXED', 'INVALID')
                """)
                logger.error("✗ group_category constraint not working (allowed invalid value)")
                return False
            except sqlite3.IntegrityError:
                logger.info("✓ group_category constraint working (STATE allowed, INVALID rejected)")

            # Test STATE category (should work)
            try:
                cursor.execute("""
                    INSERT INTO polling_groups (group_name, plc_id, polling_mode, group_category)
                    VALUES ('TEST_STATE', 1, 'FIXED', 'STATE')
                """)
                cursor.execute("DELETE FROM polling_groups WHERE group_name = 'TEST_STATE'")
                conn.commit()
                logger.info("✓ STATE category accepted")
            except Exception as e:
                logger.error(f"✗ STATE category rejected: {e}")
                return False

        return True

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("Migration: 3 Categories (OPERATION, STATE, ALARM) + log_mode")
    logger.info("=" * 60)

    db_path = str(DB_PATH)
    logger.info(f"Database: {db_path}")

    # Check if database exists
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False

    # Step 1: Add log_mode column to tags
    if check_log_mode_exists(db_path):
        logger.warning("log_mode column already exists - skipping")
    else:
        if not add_log_mode_column(db_path):
            logger.error("✗ Failed to add log_mode column")
            return False

    # Step 2: Update group_category constraint
    if not update_group_category_constraint(db_path):
        logger.error("✗ Failed to update group_category constraint")
        return False

    # Step 3: Set intelligent default log_modes
    if not set_default_log_modes(db_path):
        logger.error("✗ Failed to set default log_modes")
        return False

    # Step 4: Validate
    if not validate_migration(db_path):
        logger.error("\n" + "=" * 60)
        logger.error("✗ Migration validation failed")
        logger.error("=" * 60)
        return False

    logger.info("\n" + "=" * 60)
    logger.info("✓ Migration completed successfully!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Restart the polling engine")
    logger.info("2. Create STATE and ALARM polling groups")
    logger.info("3. Assign tags to appropriate groups")
    logger.info("4. Verify Oracle writes go to correct tables:")
    logger.info("   - OPERATION → XSCADA_OPERATION")
    logger.info("   - STATE/ALARM → XSCADA_DATATAG_LOG")
    logger.info("5. Test ON_CHANGE behavior for STATE/ALARM tags")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
