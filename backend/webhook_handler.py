"""
Core webhook handling logic for processing project data from Laravel systems
"""
from fastapi import HTTPException
from typing import Dict, Any, Optional
import sqlite3
from datetime import datetime
import json
import os


def get_db_path() -> str:
    """Get the database file path"""
    return os.path.join(os.path.dirname(__file__), 'demo.db')


def handle_webhook_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process incoming webhook and create/update project

    Args:
        payload: Webhook payload dictionary

    Returns:
        Dictionary with project_id, action, source_system, source_id

    Raises:
        HTTPException: If database operation fails
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        source_system = payload['source_system']
        source_id = payload['source_id']
        source_reference = payload.get('source_reference', '')
        project_data = payload['project']
        campaign_data = payload.get('campaign')

        # Handle campaign if provided
        campaign_id = None
        if campaign_data:
            campaign_id = find_or_create_campaign_inline(
                c, source_system, campaign_data, conn
            )

        # Check if project already exists (idempotency)
        c.execute('''SELECT id FROM projects
                     WHERE source_system = ? AND source_id = ?''',
                  (source_system, source_id))
        existing = c.fetchone()

        current_time = datetime.now().isoformat()

        if existing:
            # Update existing project
            project_id = existing[0]

            c.execute('''UPDATE projects
                         SET name = ?, description = ?, status = ?,
                             metadata = ?, last_synced_at = ?, campaign_id = ?
                         WHERE source_system = ? AND source_id = ?''',
                      (project_data['name'],
                       project_data.get('description', ''),
                       project_data.get('status', 'active'),
                       json.dumps(project_data.get('metadata', {})),
                       current_time,
                       campaign_id,
                       source_system,
                       source_id))

            action = "updated"

            print(f"[OK] Updated project {project_id} from {source_system}/{source_id}")

        else:
            # Create new project
            c.execute('''INSERT INTO projects
                         (name, description, status, source_system, source_id,
                          source_reference, metadata, webhook_received_at, last_synced_at,
                          created_at, campaign_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (project_data['name'],
                       project_data.get('description', ''),
                       project_data.get('status', 'active'),
                       source_system,
                       source_id,
                       source_reference,
                       json.dumps(project_data.get('metadata', {})),
                       current_time,
                       current_time,
                       current_time,
                       campaign_id))

            project_id = c.lastrowid
            action = "created"

            print(f"[OK] Created project {project_id} from {source_system}/{source_id}")

        conn.commit()

        return {
            "project_id": project_id,
            "action": action,
            "source_system": source_system,
            "source_id": source_id,
            "source_reference": source_reference
        }

    except sqlite3.IntegrityError as e:
        conn.rollback()
        error_msg = str(e).lower()

        # Handle duplicate entry (should not happen due to check above, but just in case)
        if "unique" in error_msg or "duplicate" in error_msg:
            # Try to get the existing project
            c.execute('''SELECT id FROM projects
                         WHERE source_system = ? AND source_id = ?''',
                      (source_system, source_id))
            existing = c.fetchone()

            if existing:
                return {
                    "project_id": existing[0],
                    "action": "already_exists",
                    "source_system": source_system,
                    "source_id": source_id
                }

        raise HTTPException(
            status_code=500,
            detail=f"Database integrity error: {str(e)}"
        )

    except Exception as e:
        conn.rollback()
        print(f"✗ Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        conn.close()


def get_webhook_stats() -> Dict[str, Any]:
    """
    Get statistics about webhook-created projects

    Returns:
        Dictionary with statistics
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Total projects from webhooks
        c.execute('''SELECT COUNT(*) FROM projects
                     WHERE source_system IS NOT NULL''')
        total_webhook_projects = c.fetchone()[0]

        # Projects by source system
        c.execute('''SELECT source_system, COUNT(*) as count
                     FROM projects
                     WHERE source_system IS NOT NULL
                     GROUP BY source_system''')
        by_source = dict(c.fetchall())

        # Recent webhook activity (last 24 hours)
        c.execute('''SELECT COUNT(*) FROM projects
                     WHERE webhook_received_at > datetime('now', '-1 day')''')
        recent_count = c.fetchone()[0]

        # Last webhook received
        c.execute('''SELECT source_system, source_reference, webhook_received_at
                     FROM projects
                     WHERE webhook_received_at IS NOT NULL
                     ORDER BY webhook_received_at DESC
                     LIMIT 1''')
        last_webhook = c.fetchone()

        return {
            "total_webhook_projects": total_webhook_projects,
            "by_source_system": by_source,
            "last_24h_count": recent_count,
            "last_webhook": {
                "source_system": last_webhook[0] if last_webhook else None,
                "source_reference": last_webhook[1] if last_webhook else None,
                "received_at": last_webhook[2] if last_webhook else None
            } if last_webhook else None
        }

    finally:
        conn.close()


def find_or_create_campaign_inline(cursor, source_system: str, campaign_data: Dict[str, Any],
                                   connection) -> Optional[int]:
    """
    Find existing campaign or create new one inline during webhook processing

    Args:
        cursor: Database cursor
        source_system: Source system identifier
        campaign_data: Campaign data from webhook
        connection: Database connection for commit

    Returns:
        campaign_id or None
    """
    # Generate a campaign source_id based on campaign name and source system
    # This allows campaigns with the same name from different systems
    campaign_source_id = f"{campaign_data.get('name', 'Unknown')}"

    # Try to find existing campaign
    cursor.execute('''SELECT id FROM campaigns
                      WHERE source_system = ? AND source_reference = ?''',
                   (source_system, campaign_source_id))
    existing = cursor.fetchone()

    if existing:
        return existing[0]

    # Create new campaign
    current_time = datetime.now().isoformat()
    cursor.execute('''INSERT INTO campaigns
                      (name, description, status, source_system, source_reference,
                       metadata, created_at, updated_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (campaign_data['name'],
                    campaign_data.get('description', ''),
                    campaign_data.get('status', 'active'),
                    source_system,
                    campaign_source_id,
                    json.dumps(campaign_data.get('metadata', {})),
                    current_time,
                    current_time))

    campaign_id = cursor.lastrowid
    connection.commit()

    print(f"  [OK] Created campaign {campaign_id}: {campaign_data['name']}")
    return campaign_id
