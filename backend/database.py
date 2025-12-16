"""
Database migration utilities for cfh-project webhook integration
"""
import sqlite3
from typing import Optional
import os


def get_db_path() -> str:
    """Get the database file path"""
    return os.path.join(os.path.dirname(__file__), 'demo.db')


def migrate_projects_table():
    """Add webhook integration fields to projects table"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("Starting migration: Adding webhook integration fields to projects table...")

    # Check and add columns if they don't exist
    columns_to_add = [
        ("source_system", "TEXT"),
        ("source_id", "TEXT"),
        ("source_reference", "TEXT"),
        ("metadata", "TEXT"),
        ("webhook_received_at", "TEXT"),
        ("last_synced_at", "TEXT")
    ]

    for column_name, column_type in columns_to_add:
        try:
            c.execute(f'ALTER TABLE projects ADD COLUMN {column_name} {column_type}')
            print(f"  [OK] Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"  - Column already exists: {column_name}")
            else:
                print(f"  ✗ Error adding column {column_name}: {e}")

    # Create unique index to prevent duplicates
    try:
        c.execute('''CREATE UNIQUE INDEX idx_projects_source
                     ON projects(source_system, source_id)''')
        print("  [OK] Created unique index: idx_projects_source")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("  - Index already exists: idx_projects_source")
        else:
            print(f"  ✗ Error creating index: {e}")

    conn.commit()
    conn.close()

    print("Migration completed successfully!")


def rollback_migration():
    """Remove webhook integration fields from projects table"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("Starting rollback: Removing webhook integration fields...")

    # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
    # For now, just drop the index
    try:
        c.execute('DROP INDEX IF EXISTS idx_projects_source')
        print("  [OK] Dropped index: idx_projects_source")
    except sqlite3.OperationalError as e:
        print(f"  ✗ Error dropping index: {e}")

    conn.commit()
    conn.close()

    print("Rollback completed!")
    print("Note: Columns cannot be dropped in SQLite. To fully rollback, delete and recreate the database.")


if __name__ == "__main__":
    # Run migration when script is executed directly
    migrate_projects_table()
