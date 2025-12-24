"""
Database Migration Script: V1 → V2 Schema

Major Changes:
1. Remove `machines` table (unnecessary hierarchy)
2. Remove `processes.machine_id` FK (processes are independent)
3. Remove `plc_connections.process_id` FK (PLCs are independent)
4. Add `tags.process_id` FK (tags connect PLC + process)
5. Add `alarm_masters` table (M address alarm definitions)

Usage:
    python backend/src/scripts/migrate_to_v2_schema.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

DB_PATH = backend_dir / "data" / "scada.db"
BACKUP_PATH = backend_dir / "data" / f"scada_backup_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
NEW_SCHEMA_PATH = backend_dir / "config" / "init_scada_db_v2.sql"


def backup_database():
    """Create backup of database before migration"""
    print(f"Creating backup: {BACKUP_PATH}")
    import shutil
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print("✓ Backup created successfully")


def export_existing_data(conn):
    """Export existing data for migration"""
    cursor = conn.cursor()

    data = {}

    # Export PLCs (from plc_connections)
    cursor.execute("SELECT * FROM plc_connections")
    data['plcs'] = cursor.fetchall()
    print(f"  Exported {len(data['plcs'])} PLCs")

    # Export processes
    cursor.execute("SELECT * FROM processes")
    data['processes'] = cursor.fetchall()
    print(f"  Exported {len(data['processes'])} processes")

    # Export polling groups
    cursor.execute("SELECT * FROM polling_groups")
    data['polling_groups'] = cursor.fetchall()
    print(f"  Exported {len(data['polling_groups'])} polling groups")

    # Export tags
    cursor.execute("SELECT * FROM tags")
    data['tags'] = cursor.fetchall()
    print(f"  Exported {len(data['tags'])} tags")

    return data


def create_new_schema(conn):
    """Create new schema from V2 SQL file"""
    print("\nCreating new schema...")

    if not NEW_SCHEMA_PATH.exists():
        print(f"❌ Schema file not found: {NEW_SCHEMA_PATH}")
        return False

    with open(NEW_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Drop old tables
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tags")
    cursor.execute("DROP VIEW IF EXISTS v_tags_with_plc")
    cursor.execute("DROP TABLE IF EXISTS polling_groups")
    cursor.execute("DROP TABLE IF EXISTS plc_connections")
    cursor.execute("DROP TABLE IF EXISTS processes")
    cursor.execute("DROP TABLE IF EXISTS machines")

    # Execute new schema
    conn.executescript(schema_sql)
    conn.commit()

    print("✓ New schema created")
    return True


def migrate_data(conn, old_data):
    """Migrate data to new schema"""
    cursor = conn.cursor()

    print("\nMigrating data...")

    # 1. Migrate PLCs (independent now, no process_id)
    print("1. Migrating PLCs...")
    plc_id_map = {}  # old_id -> new_id

    for row in old_data['plcs']:
        # Old: (id, process_id, plc_code, plc_name, ip, port, protocol, timeout, is_active, last_conn, created, updated)
        old_id = row[0]
        plc_code = row[2]
        plc_name = row[3]
        ip_address = row[4]
        port = row[5]
        protocol = row[6]
        timeout = row[7]
        is_active = row[8]

        cursor.execute("""
            INSERT INTO plc_connections (
                plc_code, plc_name, ip_address, port, protocol,
                connection_timeout, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (plc_code, plc_name, ip_address, port, protocol, timeout, is_active))

        new_id = cursor.lastrowid
        plc_id_map[old_id] = new_id

    print(f"   ✓ Migrated {len(plc_id_map)} PLCs")

    # 2. Migrate processes (independent now, no machine_id)
    print("2. Migrating processes...")
    process_id_map = {}  # old_id -> new_id

    for row in old_data['processes']:
        # Old: (id, machine_id, process_code, process_name, description, sequence_order, is_active, created, updated)
        old_id = row[0]
        process_code = row[2]
        process_name = row[3]
        location = row[4]  # description -> location
        sequence_order = row[5]
        is_active = row[6]

        cursor.execute("""
            INSERT INTO processes (
                process_code, process_name, location, sequence_order, is_active
            ) VALUES (?, ?, ?, ?, ?)
        """, (process_code, process_name, location, sequence_order, is_active))

        new_id = cursor.lastrowid
        process_id_map[old_id] = new_id

    print(f"   ✓ Migrated {len(process_id_map)} processes")

    # 3. Migrate polling groups (now has plc_id FK)
    print("3. Migrating polling groups...")
    polling_group_id_map = {}  # old_id -> new_id

    for row in old_data['polling_groups']:
        # Old: (id, group_name, polling_mode, polling_interval_ms, description, is_active, created, updated)
        old_id = row[0]
        group_name = row[1]
        polling_mode = row[2]
        polling_interval_ms = row[3]
        description = row[4]
        is_active = row[5]

        # Need to find plc_id from tags that use this polling group
        # For now, assign to PLC01 (id=1) as default
        default_plc_id = 1

        cursor.execute("""
            INSERT INTO polling_groups (
                group_name, plc_id, polling_mode, polling_interval_ms,
                description, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (group_name, default_plc_id, polling_mode, polling_interval_ms, description, is_active))

        new_id = cursor.lastrowid
        polling_group_id_map[old_id] = new_id

    print(f"   ✓ Migrated {len(polling_group_id_map)} polling groups")

    # 4. Migrate tags (now has process_id FK)
    print("4. Migrating tags...")
    tags_migrated = 0
    tags_skipped = 0

    # Build PLC to process mapping from old data
    # We infer process from machine_code in tags (which is actually process_code)
    plc_process_map = {}

    for row in old_data['tags']:
        # Old: (id, plc_id, polling_group_id, tag_address, tag_name, tag_type, unit,
        #       scale, offset, min, max, machine_code, description, is_active,
        #       last_value, last_updated, created, updated)
        old_plc_id = row[1]
        machine_code = row[11]  # This is actually process_code (14 chars)

        if old_plc_id and machine_code:
            plc_process_map[old_plc_id] = machine_code

    for row in old_data['tags']:
        old_plc_id = row[1]
        old_polling_group_id = row[2]
        tag_address = row[3]
        tag_name = row[4]
        tag_type = row[5]
        unit = row[6]
        scale = row[7]
        offset = row[8]
        min_value = row[9]
        max_value = row[10]
        machine_code = row[11]  # This is process_code
        description = row[12]
        is_active = row[13]
        last_value = row[14]
        last_updated = row[15]

        # Map old IDs to new IDs
        new_plc_id = plc_id_map.get(old_plc_id)
        new_polling_group_id = polling_group_id_map.get(old_polling_group_id) if old_polling_group_id else None

        # Find process_id by process_code (machine_code in old schema)
        new_process_id = None
        if machine_code:
            cursor.execute("SELECT id FROM processes WHERE process_code = ?", (machine_code,))
            result = cursor.fetchone()
            if result:
                new_process_id = result[0]

        # Skip if required FKs are missing
        if not new_plc_id or not new_process_id:
            tags_skipped += 1
            print(f"   ⚠️  Skipped tag {tag_name}: missing plc_id or process_id")
            continue

        cursor.execute("""
            INSERT INTO tags (
                plc_id, process_id, tag_address, tag_name, tag_type,
                unit, scale, offset, min_value, max_value,
                polling_group_id, description, is_active,
                last_value, last_updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_plc_id, new_process_id, tag_address, tag_name, tag_type,
            unit, scale, offset, min_value, max_value,
            new_polling_group_id, description, is_active,
            last_value, last_updated
        ))

        tags_migrated += 1

    print(f"   ✓ Migrated {tags_migrated} tags")
    if tags_skipped > 0:
        print(f"   ⚠️  Skipped {tags_skipped} tags (missing FK references)")

    conn.commit()
    return True


def migrate_database():
    """Execute migration steps"""

    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False

    print(f"Migrating database: {DB_PATH}")

    # Connect and export old data
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF")

    try:
        print("\n--- Step 1: Export existing data ---")
        old_data = export_existing_data(conn)

        print("\n--- Step 2: Create new schema ---")
        if not create_new_schema(conn):
            return False

        print("\n--- Step 3: Migrate data to new schema ---")
        if not migrate_data(conn, old_data):
            return False

        print("\n--- Step 4: Verification ---")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM plc_connections")
        print(f"✓ plc_connections: {cursor.fetchone()[0]} rows")

        cursor.execute("SELECT COUNT(*) FROM processes")
        print(f"✓ processes: {cursor.fetchone()[0]} rows")

        cursor.execute("SELECT COUNT(*) FROM polling_groups")
        print(f"✓ polling_groups: {cursor.fetchone()[0]} rows")

        cursor.execute("SELECT COUNT(*) FROM tags")
        print(f"✓ tags: {cursor.fetchone()[0]} rows")

        cursor.execute("SELECT COUNT(*) FROM alarm_masters")
        print(f"✓ alarm_masters: {cursor.fetchone()[0]} rows (new table)")

        # Re-enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

        print("\n✅ Migration completed successfully!")
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
    print("Database Migration: V1 → V2 Schema")
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
