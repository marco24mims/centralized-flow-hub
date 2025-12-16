import sqlite3
from typing import List, Dict, Any, Optional

def get_project_stakeholders(project_id: int) -> List[Dict[str, Any]]:
    """Get all stakeholders for a project"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    c.execute('''SELECT id, project_id, name, email, role, access_level, created_at
                 FROM stakeholders
                 WHERE project_id = ?
                 ORDER BY created_at DESC''', (project_id,))

    stakeholders = []
    for row in c.fetchall():
        stakeholders.append({
            "id": row[0],
            "project_id": row[1],
            "name": row[2],
            "email": row[3],
            "role": row[4],
            "access_level": row[5],
            "created_at": row[6]
        })

    conn.close()
    return stakeholders

def get_stakeholder_by_id(stakeholder_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific stakeholder"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    c.execute('''SELECT id, project_id, name, email, role, access_level, created_at
                 FROM stakeholders
                 WHERE id = ?''', (stakeholder_id,))

    row = c.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "project_id": row[1],
        "name": row[2],
        "email": row[3],
        "role": row[4],
        "access_level": row[5],
        "created_at": row[6]
    }

def create_stakeholder(project_id: int, name: str, email: str, role: Optional[str], access_level: str) -> Dict[str, Any]:
    """Add a stakeholder to a project"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    try:
        c.execute('''INSERT INTO stakeholders (project_id, name, email, role, access_level)
                     VALUES (?, ?, ?, ?, ?)''',
                  (project_id, name, email, role, access_level))
        stakeholder_id = c.lastrowid
        conn.commit()

        print(f"[OK] Created stakeholder {stakeholder_id}: {name} ({email}) for project {project_id}")

        # Return the created stakeholder
        result = get_stakeholder_by_id(stakeholder_id)
        conn.close()
        return result

    except sqlite3.IntegrityError:
        conn.close()
        # Duplicate email for this project
        return None

def update_stakeholder(stakeholder_id: int, name: Optional[str], role: Optional[str], access_level: Optional[str]) -> Optional[Dict[str, Any]]:
    """Update a stakeholder"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Check if stakeholder exists
    c.execute('SELECT id FROM stakeholders WHERE id = ?', (stakeholder_id,))
    if not c.fetchone():
        conn.close()
        return None

    # Build update query
    updates = []
    params = []

    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if role is not None:
        updates.append("role = ?")
        params.append(role)
    if access_level is not None:
        updates.append("access_level = ?")
        params.append(access_level)

    if not updates:
        conn.close()
        return get_stakeholder_by_id(stakeholder_id)

    params.append(stakeholder_id)
    c.execute(f'UPDATE stakeholders SET {", ".join(updates)} WHERE id = ?', params)
    conn.commit()

    print(f"[OK] Updated stakeholder {stakeholder_id}")

    result = get_stakeholder_by_id(stakeholder_id)
    conn.close()
    return result

def delete_stakeholder(stakeholder_id: int) -> bool:
    """Remove a stakeholder from a project"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Check if stakeholder exists
    c.execute('SELECT id FROM stakeholders WHERE id = ?', (stakeholder_id,))
    if not c.fetchone():
        conn.close()
        return False

    c.execute('DELETE FROM stakeholders WHERE id = ?', (stakeholder_id,))
    conn.commit()
    conn.close()

    print(f"[OK] Deleted stakeholder {stakeholder_id}")
    return True

def get_stakeholder_count(project_id: int) -> int:
    """Get the number of stakeholders for a project"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM stakeholders WHERE project_id = ?', (project_id,))
    count = c.fetchone()[0]

    conn.close()
    return count
