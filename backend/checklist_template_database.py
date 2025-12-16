import sqlite3

def migrate_checklist_templates():
    """Create checklist templates and template items tables"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    print("Starting checklist templates migration...")

    # Create checklist_templates table
    c.execute('''CREATE TABLE IF NOT EXISTS checklist_templates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    print("  [OK] Created checklist_templates table")

    # Create template_items table
    c.execute('''CREATE TABLE IF NOT EXISTS template_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  template_id INTEGER NOT NULL,
                  title TEXT NOT NULL,
                  order_index INTEGER DEFAULT 0,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (template_id) REFERENCES checklist_templates(id) ON DELETE CASCADE)''')
    print("  [OK] Created template_items table")

    # Create index on template_id
    c.execute('''CREATE INDEX IF NOT EXISTS idx_template_items_template_id
                 ON template_items(template_id)''')
    print("  [OK] Created index on template_items.template_id")

    conn.commit()
    conn.close()

    print("Checklist templates migration completed successfully!")

if __name__ == "__main__":
    migrate_checklist_templates()
