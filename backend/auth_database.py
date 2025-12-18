import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'demo.db')

def migrate_auth_schema():
    """Add authentication and creator tracking"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    # Add creator tracking to projects
    columns = [
        ("created_by_email", "TEXT"),
        ("created_by_name", "TEXT"),
        ("created_by_source", "TEXT"),
    ]

    for col_name, col_type in columns:
        try:
            c.execute(f'ALTER TABLE projects ADD COLUMN {col_name} {col_type}')
            print(f"Added column {col_name} to projects table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists, skipping")
            else:
                raise

    conn.commit()
    conn.close()
    print("Auth schema migration completed successfully")

if __name__ == "__main__":
    migrate_auth_schema()
