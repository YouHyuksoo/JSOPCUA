"""
Remove alarm_masters table from database

This script removes the alarm_masters table and all related indexes.
"""

import sqlite3
import shutil
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
db_path = backend_dir / "data" / "scada.db"
backup_path = backend_dir / "data" / "scada_backup_before_remove_alarm_masters.db"

def remove_alarm_masters():
    """Remove alarm_masters table"""
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"Removing alarm_masters table from: {db_path}")
    
    # Create backup
    print("\n1. Creating backup...")
    shutil.copy2(db_path, backup_path)
    print(f"   ✓ Backup created: {backup_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alarm_masters'")
        if not cursor.fetchone():
            print("\nℹ️  alarm_masters table does not exist. Nothing to remove.")
            conn.close()
            return True
        
        print("\n2. Dropping table (indexes will be automatically dropped)...")
        cursor.execute("DROP TABLE IF EXISTS alarm_masters")
        print("   ✓ Dropped alarm_masters table and all related indexes")
        
        # Commit changes
        conn.commit()
        print("\n✅ alarm_masters table removed successfully!")
        
        # Verify
        print("\n--- Verification ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alarm_masters'")
        if not cursor.fetchone():
            print("✓ alarm_masters table no longer exists")
        else:
            print("⚠️  Warning: alarm_masters table still exists")
        
        # List remaining tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n✓ Remaining tables: {', '.join(tables)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        print(f"\nTo restore backup: copy {backup_path} to {db_path}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Remove alarm_masters Table")
    print("=" * 70)
    
    success = remove_alarm_masters()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Removal completed successfully!")
        print(f"Backup saved at: {backup_path}")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ Removal failed.")
        print("=" * 70)

