"""
Campaign handler for CRUD operations
"""
from fastapi import HTTPException
from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime
import json
import os


def get_db_path() -> str:
    """Get the database file path"""
    return os.path.join(os.path.dirname(__file__), 'demo.db')


def get_all_campaigns() -> List[Dict[str, Any]]:
    """Get all campaigns with project counts"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute('''SELECT c.id, c.name, c.description, c.status, c.source_system,
                            c.source_id, c.source_reference, c.metadata, c.created_at, c.updated_at,
                            COUNT(p.id) as project_count,
                            SUM(CASE WHEN p.status = 'completed' THEN 1 ELSE 0 END) as completed_projects
                     FROM campaigns c
                     LEFT JOIN projects p ON c.id = p.campaign_id
                     GROUP BY c.id
                     ORDER BY c.created_at DESC''')

        campaigns = []
        for row in c.fetchall():
            campaigns.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'status': row[3],
                'source_system': row[4],
                'source_id': row[5],
                'source_reference': row[6],
                'metadata': json.loads(row[7]) if row[7] else None,
                'created_at': row[8],
                'updated_at': row[9],
                'project_count': row[10],
                'completed_projects': row[11] or 0
            })

        return campaigns
    finally:
        conn.close()


def get_campaign_by_id(campaign_id: int, include_projects: bool = False) -> Dict[str, Any]:
    """Get a specific campaign by ID"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute('''SELECT id, name, description, status, source_system, source_id,
                            source_reference, metadata, created_at, updated_at
                     FROM campaigns WHERE id = ?''', (campaign_id,))
        row = c.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        campaign = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'status': row[3],
            'source_system': row[4],
            'source_id': row[5],
            'source_reference': row[6],
            'metadata': json.loads(row[7]) if row[7] else None,
            'created_at': row[8],
            'updated_at': row[9]
        }

        if include_projects:
            # Get projects in this campaign
            c.execute('''SELECT id, name, description, status, created_at
                         FROM projects WHERE campaign_id = ?
                         ORDER BY created_at DESC''', (campaign_id,))
            projects = []
            for p_row in c.fetchall():
                projects.append({
                    'id': p_row[0],
                    'name': p_row[1],
                    'description': p_row[2],
                    'status': p_row[3],
                    'created_at': p_row[4]
                })

            campaign['projects'] = projects
            campaign['project_count'] = len(projects)
            campaign['completed_projects'] = sum(1 for p in projects if p['status'] == 'completed')

        return campaign
    finally:
        conn.close()


def create_campaign(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new campaign"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        current_time = datetime.now().isoformat()

        c.execute('''INSERT INTO campaigns
                     (name, description, status, metadata, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (data['name'],
                   data.get('description', ''),
                   data.get('status', 'active'),
                   json.dumps(data.get('metadata', {})),
                   current_time,
                   current_time))

        campaign_id = c.lastrowid
        conn.commit()

        print(f"[OK] Created campaign {campaign_id}: {data['name']}")

        return {
            'id': campaign_id,
            'name': data['name'],
            'description': data.get('description'),
            'status': data.get('status', 'active'),
            'metadata': data.get('metadata'),
            'created_at': current_time,
            'updated_at': current_time
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()


def update_campaign(campaign_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing campaign"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Check if campaign exists
        c.execute('SELECT id FROM campaigns WHERE id = ?', (campaign_id,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        current_time = datetime.now().isoformat()
        update_fields = []
        params = []

        if 'name' in data and data['name'] is not None:
            update_fields.append('name = ?')
            params.append(data['name'])

        if 'description' in data:
            update_fields.append('description = ?')
            params.append(data['description'])

        if 'status' in data and data['status'] is not None:
            update_fields.append('status = ?')
            params.append(data['status'])

        if 'metadata' in data:
            update_fields.append('metadata = ?')
            params.append(json.dumps(data['metadata']))

        update_fields.append('updated_at = ?')
        params.append(current_time)
        params.append(campaign_id)

        query = f"UPDATE campaigns SET {', '.join(update_fields)} WHERE id = ?"
        c.execute(query, params)
        conn.commit()

        print(f"[OK] Updated campaign {campaign_id}")

        return get_campaign_by_id(campaign_id)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()


def delete_campaign(campaign_id: int) -> Dict[str, str]:
    """Delete a campaign (and optionally unlink projects)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Check if campaign exists
        c.execute('SELECT id FROM campaigns WHERE id = ?', (campaign_id,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        # Unlink projects from this campaign
        c.execute('UPDATE projects SET campaign_id = NULL WHERE campaign_id = ?', (campaign_id,))

        # Delete campaign
        c.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
        conn.commit()

        print(f"[OK] Deleted campaign {campaign_id}")

        return {"message": f"Campaign {campaign_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()


def find_or_create_campaign(source_system: str, source_id: str, campaign_data: Dict[str, Any]) -> int:
    """
    Find existing campaign by source system/ID or create new one
    Returns campaign_id
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Try to find existing campaign
        c.execute('SELECT id FROM campaigns WHERE source_system = ? AND source_id = ?',
                  (source_system, source_id))
        existing = c.fetchone()

        if existing:
            return existing[0]

        # Create new campaign
        current_time = datetime.now().isoformat()
        c.execute('''INSERT INTO campaigns
                     (name, description, status, source_system, source_id, source_reference,
                      metadata, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (campaign_data['name'],
                   campaign_data.get('description', ''),
                   campaign_data.get('status', 'active'),
                   source_system,
                   source_id,
                   campaign_data.get('source_reference', ''),
                   json.dumps(campaign_data.get('metadata', {})),
                   current_time,
                   current_time))

        campaign_id = c.lastrowid
        conn.commit()

        print(f"[OK] Created campaign {campaign_id} from webhook: {campaign_data['name']}")
        return campaign_id

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()
