"""
Database Migration Script: Rename 'lines' table to 'machines'

This script migrates the existing database schema from:
- lines table → machines table
- line_id columns → machine_id columns
- line_code columns → machine_code columns
- line_name columns → machine_name columns

Usage:
    python backend/src/scripts/migrate_lines_to_machines.py
"""

import sqlite3
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

DB_PATH = backend_dir / "data" / "scada.db"
BACKUP_PATH = backend_dir / "data" / "scada_backup_before_migration.db"


def backup_database():
    """Create backup of database before migration"""
    print(f"Creating backup: {BACKUP_PATH}")
    import shutil
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print("✓ Backup created successfully")


def migrate_database():
    """Execute migration steps"""

    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False

    print(f"Migrating database: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF")  # Disable FK checks during migration
    cursor = conn.cursor()

    try:
        # Step 1: Check if 'lines' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lines'")
        if not cursor.fetchone():
            print("ℹ️  'lines' table not found. Already migrated or fresh database.")
            conn.close()
            return True

        print("\n--- Migration Steps ---")

        # Step 2: Drop view that references 'lines' table
        print("1. Dropping view v_tags_with_plc...")
        cursor.execute("DROP VIEW IF EXISTS v_tags_with_plc")
        print("   ✓ View dropped")

        # Step 3: Rename 'lines' table to 'machines'
        print("2. Renaming table: lines → machines...")
        cursor.execute("ALTER TABLE lines RENAME TO machines")
        print("   ✓ Table renamed")

        # Step 4: Rename column in 'machines' table: line_code → machine_code
        print("3. Renaming column: line_code → machine_code...")
        cursor.execute("ALTER TABLE machines RENAME COLUMN line_code TO machine_code")
        print("   ✓ Column renamed")

        # Step 5: Rename column in 'machines' table: line_name → machine_name
        print("4. Renaming column: line_name → machine_name...")
        cursor.execute("ALTER TABLE machines RENAME COLUMN line_name TO machine_name")
        print("   ✓ Column renamed")

        # Step 6: Update 'machines' table: description → location
        print("5. Renaming column: description → location...")
        cursor.execute("ALTER TABLE machines RENAME COLUMN description TO location")
        print("   ✓ Column renamed")

        # Step 7: Rename column in 'processes' table: line_id → machine_id
        print("6. Renaming column in processes: line_id → machine_id...")
        cursor.execute("ALTER TABLE processes RENAME COLUMN line_id TO machine_id")
        print("   ✓ Column renamed")

        # Step 8: Drop old index and create new one
        print("7. Updating index: idx_processes_line_id → idx_processes_machine_id...")
        cursor.execute("DROP INDEX IF EXISTS idx_processes_line_id")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processes_machine_id ON processes(machine_id)")
        print("   ✓ Index updated")

        # Step 9: Recreate view with new table/column names
        print("8. Recreating view v_tags_with_plc with new schema...")
        cursor.execute("""
            CREATE VIEW v_tags_with_plc AS
            SELECT
                t.id AS tag_id,
                t.tag_address,
                t.tag_name,
                t.tag_type,
                t.unit,
                t.scale,
                t.offset,
                t.machine_code,
                t.is_active AS tag_active,
                t.last_value,
                t.last_updated_at,
                plc.id AS plc_id,
                plc.plc_code,
                plc.plc_name,
                plc.ip_address,
                plc.port,
                plc.is_active AS plc_active,
                p.id AS process_id,
                p.process_code,
                p.process_name,
                m.id AS machine_id,
                m.machine_code,
                m.machine_name,
                pg.id AS polling_group_id,
                pg.group_name,
                pg.polling_mode,
                pg.polling_interval_ms
            FROM tags t
            INNER JOIN plc_connections plc ON t.plc_id = plc.id
            INNER JOIN processes p ON plc.process_id = p.id
            INNER JOIN machines m ON p.machine_id = m.id
            LEFT JOIN polling_groups pg ON t.polling_group_id = pg.id
        """)
        print("   ✓ View recreated")

        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")

        # Re-enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Verify migration
        print("\n--- Verification ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machines'")
        if cursor.fetchone():
            print("✓ 'machines' table exists")

        cursor.execute("PRAGMA table_info(machines)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"✓ 'machines' columns: {', '.join(columns)}")

        cursor.execute("PRAGMA table_info(processes)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'machine_id' in columns:
            print(f"✓ 'processes' has 'machine_id' column")

        cursor.execute("SELECT COUNT(*) FROM machines")
        count = cursor.fetchone()[0]
        print(f"✓ 'machines' table has {count} rows")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        conn.close()
        print(f"\nTo restore backup: copy {BACKUP_PATH} to {DB_PATH}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Database Migration: lines → machines")
    print("=" * 70)

    # Create backup first
    backup_database()

    # Execute migration
    success = migrate_database()

    if success:
        print("\n" + "=" * 70)
        print("Migration completed successfully!")
        print(f"Backup saved at: {BACKUP_PATH}")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("Migration failed. Database unchanged.")
        print("=" * 70)
        sys.exit(1)
