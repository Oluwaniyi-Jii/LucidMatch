"""
Add test_metadata column to existing database.
Run this once to migrate the schema.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'lucidmatch.db')

def add_test_metadata_column():
    """Add test_metadata column to analysis table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(analysis)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'test_metadata' in columns:
            print("✓ Column 'test_metadata' already exists")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE analysis 
                ADD COLUMN test_metadata TEXT
            """)
            conn.commit()
            print("✅ Successfully added 'test_metadata' column to analysis table")
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        exit(1)
    
    add_test_metadata_column()
