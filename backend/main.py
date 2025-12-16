from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
import json

# Import webhook integration modules
from models import WebhookPayload, WebhookResponse
from auth import verify_webhook_signature
from webhook_handler import handle_webhook_project, get_webhook_stats
from database import migrate_projects_table

# Import campaign modules
from campaign_models import Campaign, CampaignCreate, CampaignUpdate, CampaignWithProjects
from campaign_handler import (
    get_all_campaigns, get_campaign_by_id, create_campaign,
    update_campaign, delete_campaign
)
from campaign_database import migrate_campaigns

# Import checklist template modules
from checklist_template_models import (
    ChecklistTemplate, ChecklistTemplateWithItems,
    ChecklistTemplateCreate, ChecklistTemplateUpdate
)
from checklist_template_handler import (
    get_all_templates, get_template_by_id, create_template,
    update_template, delete_template, apply_template_to_project
)
from checklist_template_database import migrate_checklist_templates

app = FastAPI(title="Project Management Demo")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://10.50.10.68:3000",
        "http://10.50.10.68:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
def init_db():
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  status TEXT DEFAULT 'active',
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    # Checklist items table
    c.execute('''CREATE TABLE IF NOT EXISTS checklist_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER,
                  title TEXT NOT NULL,
                  completed INTEGER DEFAULT 0,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (project_id) REFERENCES projects (id))''')

    # Comments table
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER,
                  user_name TEXT DEFAULT 'Demo User',
                  content TEXT NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (project_id) REFERENCES projects (id))''')

    # Insert demo data if empty
    c.execute('SELECT COUNT(*) FROM projects')
    if c.fetchone()[0] == 0:
        # Project 1: Construction
        c.execute("INSERT INTO projects (name, description, status) VALUES (?, ?, ?)",
                  ("Construction Project Alpha", "Building renovation and modernization", "active"))
        project_id = c.lastrowid
        checklist_items = [
            "Site survey and assessment",
            "Obtain building permits",
            "Foundation work",
            "Structural framework",
            "Electrical installation",
            "Plumbing systems",
            "Final inspection"
        ]
        for item in checklist_items:
            c.execute("INSERT INTO checklist_items (project_id, title) VALUES (?, ?)",
                      (project_id, item))
        c.execute("INSERT INTO comments (project_id, user_name, content) VALUES (?, ?, ?)",
                  (project_id, "John Manager", "Project kickoff meeting scheduled for Monday"))
        c.execute("INSERT INTO comments (project_id, user_name, content) VALUES (?, ?, ?)",
                  (project_id, "Sarah Engineer", "Permits have been submitted to the city"))

        # Project 2: Software Development
        c.execute("INSERT INTO projects (name, description, status) VALUES (?, ?, ?)",
                  ("Mobile App Development", "E-commerce mobile application for iOS and Android", "active"))
        project_id2 = c.lastrowid
        checklist_items2 = [
            "Requirements gathering",
            "UI/UX design mockups",
            "Backend API development",
            "Frontend development",
            "Testing and QA",
            "App store submission"
        ]
        for item in checklist_items2:
            c.execute("INSERT INTO checklist_items (project_id, title) VALUES (?, ?)",
                      (project_id2, item))
        c.execute("INSERT INTO comments (project_id, user_name, content) VALUES (?, ?, ?)",
                  (project_id2, "Alice Developer", "Sprint planning completed for iteration 1"))

        # Project 3: Marketing Campaign
        c.execute("INSERT INTO projects (name, description, status) VALUES (?, ?, ?)",
                  ("Q1 Marketing Campaign", "Social media and digital marketing initiative", "active"))
        project_id3 = c.lastrowid
        checklist_items3 = [
            "Market research",
            "Content strategy development",
            "Design assets creation",
            "Campaign launch",
            "Performance monitoring"
        ]
        for item in checklist_items3:
            c.execute("INSERT INTO checklist_items (project_id, title) VALUES (?, ?)",
                      (project_id3, item))
        c.execute("INSERT INTO comments (project_id, user_name, content) VALUES (?, ?, ?)",
                  (project_id3, "Bob Marketing", "Target audience analysis complete"))

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Run webhook integration migration
print("Running webhook integration migration...")
migrate_projects_table()
print("Migration complete!")

# Run campaign migration
print("Running campaign migration...")
migrate_campaigns()
print("Campaign migration complete!")

# Run checklist templates migration
print("Running checklist templates migration...")
migrate_checklist_templates()
print("Checklist templates migration complete!")

# Pydantic models
class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: str = "active"
    campaign_id: Optional[int] = None
    created_at: Optional[str] = None

class ChecklistItem(BaseModel):
    id: Optional[int] = None
    project_id: int
    title: str
    completed: bool = False
    created_at: Optional[str] = None

class Comment(BaseModel):
    id: Optional[int] = None
    project_id: int
    user_name: str = "Demo User"
    content: str
    created_at: Optional[str] = None

# API Endpoints
@app.get("/")
def read_root():
    return {"status": "Project Management System API - Running", "version": "1.0 Demo"}

@app.get("/api/projects", response_model=List[Project])
def get_projects():
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('SELECT id, name, description, status, created_at FROM projects')
    projects = []
    for row in c.fetchall():
        projects.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "created_at": row[4]
        })
    conn.close()
    return projects

@app.post("/api/projects", response_model=Project)
def create_project(project: Project):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('INSERT INTO projects (name, description, status, campaign_id) VALUES (?, ?, ?, ?)',
              (project.name, project.description, project.status, project.campaign_id))
    project.id = c.lastrowid
    conn.commit()
    conn.close()
    return project

@app.put("/api/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project: Project):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('''UPDATE projects
                 SET name = ?, description = ?, status = ?, campaign_id = ?
                 WHERE id = ?''',
              (project.name, project.description, project.status, project.campaign_id, project_id))
    conn.commit()

    # Fetch updated project
    c.execute('SELECT id, name, description, status, campaign_id, created_at FROM projects WHERE id = ?', (project_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Project not found")

    return Project(
        id=row[0],
        name=row[1],
        description=row[2],
        status=row[3],
        campaign_id=row[4],
        created_at=row[5]
    )

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # Check if project exists
    c.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete related records first (foreign key constraints)
    c.execute('DELETE FROM checklist_items WHERE project_id = ?', (project_id,))
    c.execute('DELETE FROM comments WHERE project_id = ?', (project_id,))

    # Delete the project
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

    return {"status": "deleted", "id": project_id}

@app.get("/api/projects/stats")
def get_projects_stats():
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('SELECT id, name, description, status, campaign_id, created_at FROM projects ORDER BY created_at DESC')
    projects = []
    for row in c.fetchall():
        project_id = row[0]

        # Get checklist stats
        c.execute('SELECT COUNT(*) FROM checklist_items WHERE project_id = ?', (project_id,))
        total_tasks = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM checklist_items WHERE project_id = ? AND completed = 1', (project_id,))
        completed_tasks = c.fetchone()[0]

        # Get comment count
        c.execute('SELECT COUNT(*) FROM comments WHERE project_id = ?', (project_id,))
        comment_count = c.fetchone()[0]

        progress = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

        projects.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "campaign_id": row[4],
            "created_at": row[5],
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress": progress,
            "comment_count": comment_count
        })
    conn.close()
    return projects

@app.get("/api/projects/{project_id}/checklist", response_model=List[ChecklistItem])
def get_checklist(project_id: int):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('SELECT id, project_id, title, completed, created_at FROM checklist_items WHERE project_id = ?', (project_id,))
    items = []
    for row in c.fetchall():
        items.append({
            "id": row[0],
            "project_id": row[1],
            "title": row[2],
            "completed": bool(row[3]),
            "created_at": row[4]
        })
    conn.close()
    return items

@app.post("/api/checklist", response_model=ChecklistItem)
def create_checklist_item(item: ChecklistItem):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('INSERT INTO checklist_items (project_id, title, completed) VALUES (?, ?, ?)',
              (item.project_id, item.title, int(item.completed)))
    item.id = c.lastrowid
    conn.commit()
    conn.close()
    return item

@app.patch("/api/checklist/{item_id}")
def update_checklist_item(item_id: int, completed: bool):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('UPDATE checklist_items SET completed = ? WHERE id = ?', (int(completed), item_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.get("/api/projects/{project_id}/comments", response_model=List[Comment])
def get_comments(project_id: int):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('SELECT id, project_id, user_name, content, created_at FROM comments WHERE project_id = ? ORDER BY created_at DESC', (project_id,))
    comments = []
    for row in c.fetchall():
        comments.append({
            "id": row[0],
            "project_id": row[1],
            "user_name": row[2],
            "content": row[3],
            "created_at": row[4]
        })
    conn.close()
    return comments

@app.post("/api/comments", response_model=Comment)
def create_comment(comment: Comment):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('INSERT INTO comments (project_id, user_name, content) VALUES (?, ?, ?)',
              (comment.project_id, comment.user_name, comment.content))
    comment.id = c.lastrowid
    conn.commit()
    conn.close()
    return comment

# Campaign endpoints
@app.get("/api/campaigns", response_model=List[CampaignWithProjects])
def list_campaigns():
    """Get all campaigns with project counts"""
    campaigns = get_all_campaigns()
    return campaigns

@app.get("/api/campaigns/{campaign_id}", response_model=CampaignWithProjects)
def get_campaign(campaign_id: int, include_projects: bool = True):
    """Get a specific campaign with optional project list"""
    campaign = get_campaign_by_id(campaign_id, include_projects=include_projects)
    return campaign

@app.post("/api/campaigns", response_model=Campaign)
def create_new_campaign(campaign: CampaignCreate):
    """Create a new campaign"""
    result = create_campaign(campaign.dict())
    return result

@app.put("/api/campaigns/{campaign_id}", response_model=Campaign)
def update_existing_campaign(campaign_id: int, campaign: CampaignUpdate):
    """Update an existing campaign"""
    result = update_campaign(campaign_id, campaign.dict(exclude_unset=True))
    return result

@app.delete("/api/campaigns/{campaign_id}")
def delete_existing_campaign(campaign_id: int):
    """Delete a campaign (projects will be unlinked)"""
    result = delete_campaign(campaign_id)
    return result

# Webhook endpoints
@app.post("/api/webhooks/project", response_model=WebhookResponse)
async def receive_project_webhook(
    payload: WebhookPayload,
    authenticated: bool = Depends(verify_webhook_signature)
):
    """
    Receive project data from Laravel applications via webhook
    Requires Bearer token authentication

    Args:
        payload: Webhook payload containing project data
        authenticated: Authentication dependency injection

    Returns:
        WebhookResponse with status and result data
    """
    try:
        result = handle_webhook_project(payload.dict())
        return WebhookResponse(
            status="success",
            message=f"Project {result['action']} successfully",
            data=result
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/webhooks/health")
def webhook_health():
    """
    Get webhook integration health statistics

    Returns:
        Dictionary with webhook statistics
    """
    try:
        stats = get_webhook_stats()
        return {
            "status": "healthy",
            "webhook_integration": "enabled",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Checklist Template endpoints
@app.get("/api/checklist-templates", response_model=List[ChecklistTemplateWithItems])
def list_checklist_templates():
    """Get all checklist templates with item counts"""
    templates = get_all_templates()
    return templates

@app.get("/api/checklist-templates/{template_id}", response_model=ChecklistTemplateWithItems)
def get_checklist_template(template_id: int):
    """Get a specific checklist template with all its items"""
    template = get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/api/checklist-templates", response_model=ChecklistTemplateWithItems)
def create_checklist_template(template: ChecklistTemplateCreate):
    """Create a new checklist template"""
    result = create_template(template.name, template.description, template.items)
    return result

@app.put("/api/checklist-templates/{template_id}", response_model=ChecklistTemplateWithItems)
def update_checklist_template(template_id: int, template: ChecklistTemplateUpdate):
    """Update a checklist template"""
    result = update_template(
        template_id,
        template.name,
        template.description,
        template.items
    )
    if not result:
        raise HTTPException(status_code=404, detail="Template not found")
    return result

@app.delete("/api/checklist-templates/{template_id}")
def delete_checklist_template(template_id: int):
    """Delete a checklist template"""
    success = delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "deleted", "id": template_id}

@app.post("/api/projects/{project_id}/apply-template/{template_id}")
def apply_template(project_id: int, template_id: int):
    """Apply a checklist template to a project"""
    items = apply_template_to_project(template_id, project_id)
    if not items:
        raise HTTPException(status_code=404, detail="Template or project not found")
    return {
        "status": "success",
        "project_id": project_id,
        "template_id": template_id,
        "items_created": len(items),
        "items": items
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
