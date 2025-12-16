import sqlite3

def migrate_stakeholders():
    """Create stakeholders table for project collaboration"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    print("Starting stakeholders migration...")

    # Create stakeholders table
    c.execute('''CREATE TABLE IF NOT EXISTS stakeholders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  role TEXT,
                  access_level TEXT DEFAULT 'viewer',
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE)''')
    print("  [OK] Created stakeholders table")

    # Create index on project_id
    c.execute('''CREATE INDEX IF NOT EXISTS idx_stakeholders_project_id
                 ON stakeholders(project_id)''')
    print("  [OK] Created index on stakeholders.project_id")

    # Create unique index to prevent duplicate stakeholders
    c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_stakeholders_unique
                 ON stakeholders(project_id, email)''')
    print("  [OK] Created unique index on (project_id, email)")

    conn.commit()
    conn.close()

    print("Stakeholders migration completed successfully!")

if __name__ == "__main__":
    migrate_stakeholders()
