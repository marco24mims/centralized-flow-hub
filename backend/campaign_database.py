"""
Campaign database migration for cfh-project
"""
import sqlite3
import os


def get_db_path() -> str:
    """Get the database file path"""
    return os.path.join(os.path.dirname(__file__), 'demo.db')


def migrate_campaigns():
    """Create campaigns table and add campaign_id to projects table"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("Starting campaign migration...")

    # Create campaigns table
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS campaigns
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      description TEXT,
                      status TEXT DEFAULT 'active',
                      source_system TEXT,
                      source_id TEXT,
                      source_reference TEXT,
                      metadata TEXT,
                      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                      updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        print("  [OK] Created campaigns table")
    except sqlite3.OperationalError as e:
        print(f"  - Campaigns table already exists or error: {e}")

    # Add campaign_id column to projects table
    try:
        c.execute('ALTER TABLE projects ADD COLUMN campaign_id INTEGER')
        print("  [OK] Added campaign_id column to projects table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("  - Column campaign_id already exists in projects table")
        else:
            print(f"  ✗ Error adding campaign_id column: {e}")

    # Create index on campaign_id for faster lookups
    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_projects_campaign ON projects(campaign_id)')
        print("  [OK] Created index on projects.campaign_id")
    except sqlite3.OperationalError as e:
        print(f"  - Index already exists or error: {e}")

    # Create unique index for campaigns source system tracking
    try:
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_campaigns_source
                     ON campaigns(source_system, source_id)''')
        print("  [OK] Created unique index on campaigns(source_system, source_id)")
    except sqlite3.OperationalError as e:
        print(f"  - Index already exists or error: {e}")

    conn.commit()
    conn.close()

    print("Campaign migration completed successfully!")


def create_demo_campaign():
    """Create a demo campaign with sample data"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check if demo campaign already exists
    c.execute('SELECT COUNT(*) FROM campaigns WHERE name = ?', ('Demo Campaign 2025',))
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO campaigns
                     (name, description, status)
                     VALUES (?, ?, ?)''',
                  ('Demo Campaign 2025',
                   'Sample campaign for demonstration purposes',
                   'active'))
        campaign_id = c.lastrowid

        # Update existing demo projects to belong to this campaign
        c.execute('UPDATE projects SET campaign_id = ? WHERE id <= 3', (campaign_id,))

        conn.commit()
        print(f"[OK] Created demo campaign (ID: {campaign_id}) and linked 3 projects to it")
    else:
        print("  - Demo campaign already exists")

    conn.close()


if __name__ == "__main__":
    # Run migration when script is executed directly
    migrate_campaigns()
    create_demo_campaign()
