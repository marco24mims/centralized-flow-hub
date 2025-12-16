import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

def get_all_templates() -> List[Dict[str, Any]]:
    """Get all checklist templates with their item counts"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    c.execute('SELECT id, name, description, created_at, updated_at FROM checklist_templates ORDER BY created_at DESC')
    templates = []

    for row in c.fetchall():
        template_id = row[0]

        # Count template items
        c.execute('SELECT COUNT(*) FROM template_items WHERE template_id = ?', (template_id,))
        item_count = c.fetchone()[0]

        templates.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "created_at": row[3],
            "updated_at": row[4],
            "item_count": item_count
        })

    conn.close()
    return templates

def get_template_by_id(template_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific template with all its items"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Get template
    c.execute('SELECT id, name, description, created_at, updated_at FROM checklist_templates WHERE id = ?', (template_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    # Get template items
    c.execute('SELECT id, template_id, title, order_index, created_at FROM template_items WHERE template_id = ? ORDER BY order_index, id', (template_id,))
    items = []
    for item_row in c.fetchall():
        items.append({
            "id": item_row[0],
            "template_id": item_row[1],
            "title": item_row[2],
            "order_index": item_row[3],
            "created_at": item_row[4]
        })

    conn.close()

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "created_at": row[3],
        "updated_at": row[4],
        "items": items,
        "item_count": len(items)
    }

def create_template(name: str, description: Optional[str], items: List[str]) -> Dict[str, Any]:
    """Create a new checklist template with items"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Create template
    c.execute('INSERT INTO checklist_templates (name, description) VALUES (?, ?)', (name, description))
    template_id = c.lastrowid

    # Create template items
    for index, item_title in enumerate(items):
        c.execute('INSERT INTO template_items (template_id, title, order_index) VALUES (?, ?, ?)',
                  (template_id, item_title, index))

    conn.commit()

    # Get the created template with items
    result = get_template_by_id(template_id)
    conn.close()

    print(f"[OK] Created checklist template {template_id}: {name}")
    return result

def update_template(template_id: int, name: Optional[str], description: Optional[str], items: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """Update a checklist template"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Check if template exists
    c.execute('SELECT id FROM checklist_templates WHERE id = ?', (template_id,))
    if not c.fetchone():
        conn.close()
        return None

    # Update template fields
    if name is not None or description is not None:
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)

        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())

        params.append(template_id)

        c.execute(f'UPDATE checklist_templates SET {", ".join(updates)} WHERE id = ?', params)

    # Update items if provided
    if items is not None:
        # Delete old items
        c.execute('DELETE FROM template_items WHERE template_id = ?', (template_id,))

        # Insert new items
        for index, item_title in enumerate(items):
            c.execute('INSERT INTO template_items (template_id, title, order_index) VALUES (?, ?, ?)',
                      (template_id, item_title, index))

    conn.commit()

    # Get the updated template
    result = get_template_by_id(template_id)
    conn.close()

    print(f"[OK] Updated checklist template {template_id}")
    return result

def delete_template(template_id: int) -> bool:
    """Delete a checklist template and its items"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Check if template exists
    c.execute('SELECT id FROM checklist_templates WHERE id = ?', (template_id,))
    if not c.fetchone():
        conn.close()
        return False

    # Delete template items (should cascade, but let's be explicit)
    c.execute('DELETE FROM template_items WHERE template_id = ?', (template_id,))

    # Delete template
    c.execute('DELETE FROM checklist_templates WHERE id = ?', (template_id,))

    conn.commit()
    conn.close()

    print(f"[OK] Deleted checklist template {template_id}")
    return True

def apply_template_to_project(template_id: int, project_id: int) -> List[Dict[str, Any]]:
    """Apply a checklist template to a project by creating checklist items"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Check if template exists
    c.execute('SELECT id FROM checklist_templates WHERE id = ?', (template_id,))
    if not c.fetchone():
        conn.close()
        return []

    # Check if project exists
    c.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
    if not c.fetchone():
        conn.close()
        return []

    # Get template items
    c.execute('SELECT title, order_index FROM template_items WHERE template_id = ? ORDER BY order_index, id', (template_id,))
    template_items = c.fetchall()

    # Create checklist items from template
    created_items = []
    for item in template_items:
        title = item[0]
        c.execute('INSERT INTO checklist_items (project_id, title, completed) VALUES (?, ?, ?)',
                  (project_id, title, 0))
        item_id = c.lastrowid

        created_items.append({
            "id": item_id,
            "project_id": project_id,
            "title": title,
            "completed": False
        })

    conn.commit()
    conn.close()

    print(f"[OK] Applied template {template_id} to project {project_id} ({len(created_items)} items)")
    return created_items
