"""
Database Migration Script: Change processes.machine_id to processes.machine_code

This script migrates the processes table to use machine_code (TEXT) 
instead of machine_id (INTEGER) to reference machines.machine_code directly.

Usage:
    python backend/src/scripts/migrate_machine_id_to_machine_code.py
"""

import sqlite3
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

DB_PATH = backend_dir / "data" / "scada.db"
BACKUP_PATH = backend_dir / "data" / "scada_backup_before_machine_code_migration.db"


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
        print("\n--- Migration Steps ---")

        # Step 1: Check current schema
        print("1. Checking current schema...")
        cursor.execute("PRAGMA table_info(processes)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        if 'machine_code' in columns:
            print("   ℹ️  'machine_code' column already exists. Migration may have been done.")
            # Check if machine_id still exists
            if 'machine_id' in columns:
                print("   ⚠️  Both 'machine_id' and 'machine_code' exist. Proceeding with cleanup...")
            else:
                print("   ✓ Migration already completed.")
                conn.close()
                return True

        # Step 2: Add machine_code column if it doesn't exist
        if 'machine_code' not in columns:
            print("2. Adding machine_code column to processes table...")
            cursor.execute("ALTER TABLE processes ADD COLUMN machine_code TEXT")
            print("   ✓ Column added")

        # Step 3: Migrate data: convert machine_id to machine_code
        print("3. Migrating data: machine_id → machine_code...")
        cursor.execute("""
            UPDATE processes 
            SET machine_code = (
                SELECT machine_code 
                FROM machines 
                WHERE machines.id = processes.machine_id
            )
            WHERE machine_id IS NOT NULL
        """)
        updated_count = cursor.rowcount
        print(f"   ✓ Updated {updated_count} records")

        # Step 4: Drop old foreign key constraint (by recreating table)
        print("4. Recreating processes table with new schema...")
        
        # Get current data
        cursor.execute("""
            SELECT id, process_code, process_name, machine_code, plc_id, 
                   description, is_active, created_at, updated_at, sequence_order
            FROM processes
        """)
        data = cursor.fetchall()

        # Drop old table
        cursor.execute("DROP TABLE IF EXISTS processes_old")
        cursor.execute("ALTER TABLE processes RENAME TO processes_old")

        # Create new table with machine_code instead of machine_id
        cursor.execute("""
            CREATE TABLE processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_code TEXT NOT NULL UNIQUE,
                process_name TEXT NOT NULL,
                machine_code TEXT,
                plc_id INTEGER NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sequence_order INTEGER DEFAULT 0,
                FOREIGN KEY (machine_code) REFERENCES machines(machine_code) ON DELETE SET NULL,
                FOREIGN KEY (plc_id) REFERENCES plc_connections(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ New table created")

        # Step 5: Copy data back
        print("5. Copying data to new table...")
        cursor.executemany("""
            INSERT INTO processes (
                id, process_code, process_name, machine_code, plc_id,
                description, is_active, created_at, updated_at, sequence_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        print(f"   ✓ Copied {len(data)} records")

        # Step 6: Drop old table
        print("6. Dropping old table...")
        cursor.execute("DROP TABLE processes_old")
        print("   ✓ Old table dropped")

        # Step 7: Recreate indexes
        print("7. Recreating indexes...")
        cursor.execute("DROP INDEX IF EXISTS idx_processes_machine_id")
        cursor.execute("DROP INDEX IF EXISTS idx_processes_machine_code")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processes_machine_code ON processes(machine_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processes_code ON processes(process_code)")
        print("   ✓ Indexes recreated")

        # Step 8: Update views that reference processes.machine_id
        print("8. Updating views...")
        cursor.execute("DROP VIEW IF EXISTS v_tags_with_plc")
        
        # Check if machines table exists and has machine_code
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machines'")
        if cursor.fetchone():
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
                    p.machine_code AS process_machine_code,
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
                LEFT JOIN machines m ON p.machine_code = m.machine_code
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
        cursor.execute("PRAGMA table_info(processes)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"✓ 'processes' columns: {', '.join(columns)}")
        
        if 'machine_code' in columns and 'machine_id' not in columns:
            print("✓ 'machine_code' column exists, 'machine_id' removed")
        else:
            print("⚠️  Column check: machine_code={}, machine_id={}".format(
                'machine_code' in columns, 'machine_id' in columns
            ))

        cursor.execute("SELECT COUNT(*) FROM processes")
        count = cursor.fetchone()[0]
        print(f"✓ 'processes' table has {count} rows")

        # Check foreign key relationship
        cursor.execute("""
            SELECT COUNT(*) 
            FROM processes p
            LEFT JOIN machines m ON p.machine_code = m.machine_code
            WHERE p.machine_code IS NOT NULL AND m.machine_code IS NULL
        """)
        orphaned = cursor.fetchone()[0]
        if orphaned > 0:
            print(f"⚠️  Warning: {orphaned} processes have machine_code that doesn't exist in machines table")
        else:
            print("✓ All machine_code references are valid")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        print(f"\nTo restore backup: copy {BACKUP_PATH} to {DB_PATH}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Database Migration: processes.machine_id → processes.machine_code")
    print("=" * 70)

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

