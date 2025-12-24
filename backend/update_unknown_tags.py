"""
Update unknown tags to is_active=0
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.api.dependencies import DB_PATH
from src.database.sqlite_manager import SQLiteManager

def main():
    print(f"Using database: {DB_PATH}")

    db = SQLiteManager(DB_PATH)

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Count tags before update
        cursor.execute("SELECT COUNT(*) FROM tags WHERE LOWER(tag_name) = 'unknown'")
        count_before = cursor.fetchone()[0]
        print(f"Found {count_before} tags with name='unknown'")

        # Update tags
        cursor.execute("UPDATE tags SET is_active = 0 WHERE LOWER(tag_name) = 'unknown'")
        affected = cursor.rowcount
        conn.commit()

        print(f"✓ Updated {affected} tags to is_active=0")

        # Verify
        cursor.execute("SELECT COUNT(*) FROM tags WHERE LOWER(tag_name) = 'unknown' AND is_active = 1")
        still_active = cursor.fetchone()[0]

        if still_active == 0:
            print("✓ All 'unknown' tags are now inactive")
        else:
            print(f"⚠ Warning: {still_active} 'unknown' tags are still active")

if __name__ == "__main__":
    main()
