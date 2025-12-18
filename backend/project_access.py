from typing import List, Dict, Any
import sqlite3
import os
from auth_models import User

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'demo.db')

def filter_projects_by_access(user: User, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter projects:
    - Admins: ALL projects
    - Non-admins: Created by user + Stakeholder projects
    """
    if user.is_admin:
        return projects

    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    accessible_ids = set()

    # Projects created by user
    c.execute('SELECT id FROM projects WHERE created_by_email = ?', (user.email,))
    accessible_ids.update(row[0] for row in c.fetchall())

    # Projects where user is stakeholder
    c.execute('SELECT project_id FROM stakeholders WHERE email = ?', (user.email,))
    accessible_ids.update(row[0] for row in c.fetchall())

    conn.close()

    return [p for p in projects if p.get('id') in accessible_ids]

def can_access_project(user: User, project_id: int) -> bool:
    """Check if user can access specific project"""
    if user.is_admin:
        return True

    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    # Check creator
    c.execute('SELECT id FROM projects WHERE id = ? AND created_by_email = ?',
              (project_id, user.email))
    if c.fetchone():
        conn.close()
        return True

    # Check stakeholder
    c.execute('SELECT id FROM stakeholders WHERE project_id = ? AND email = ?',
              (project_id, user.email))
    result = c.fetchone() is not None
    conn.close()
    return result
