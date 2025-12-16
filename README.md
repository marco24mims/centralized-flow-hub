# Centralized Flow Hub (CFH Project)

A centralized project management system that receives project data from multiple Laravel applications via webhooks.

## Overview

CFH Project is a FastAPI-based project management system that integrates with:
- **Laravel 11 (AdMe CMS)** - Banner booking and deployment management
- **Laravel 9 (Digital Operations)** - Digital product delivery requests (eDM, CME, Webinars, etc.)

## Features

✅ **Project Management** - Track projects with checklists, comments, and stakeholders
✅ **Campaign Grouping** - Group related projects into campaigns
✅ **Webhook Integration** - Receive project data from Laravel applications
✅ **RESTful API** - Complete CRUD operations for projects and campaigns
✅ **Real-time Updates** - 5-second polling for live data

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLite (development) / PostgreSQL (production)
- Pydantic for validation
- Uvicorn ASGI server

**Frontend:**
- React 18.2.0
- Axios for API calls
- Modern responsive UI

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload --port 8000
```

The server will run at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will run at: http://localhost:3000

## API Documentation

Interactive API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Key Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create a project
- `GET /api/projects/stats` - Get projects with statistics
- `GET /api/projects/{id}/checklist` - Get checklist items
- `GET /api/projects/{id}/comments` - Get comments

### Campaigns
- `GET /api/campaigns` - List all campaigns
- `GET /api/campaigns/{id}` - Get specific campaign with projects
- `POST /api/campaigns` - Create a new campaign
- `PUT /api/campaigns/{id}` - Update a campaign
- `DELETE /api/campaigns/{id}` - Delete a campaign

### Webhooks
- `POST /api/webhooks/project` - Receive project data (requires authentication)
- `GET /api/webhooks/health` - Webhook health statistics

## Webhook Integration

### Authentication

All webhook requests require a shared secret token in the Authorization header:

```bash
Authorization: Bearer your-secret-key
```

Configure the secret in `.env`:
```env
WEBHOOK_SECRET=your-secret-key
```

### Webhook Payload Format

```json
{
  "source_system": "laravel11|laravel9",
  "source_id": "123",
  "source_reference": "BK-2025-001",
  "event_type": "created|updated|status_changed",
  "timestamp": "2025-12-16T10:00:00Z",
  "project": {
    "name": "Project Name",
    "description": "Description",
    "status": "active|completed|cancelled",
    "metadata": {}
  },
  "campaign": {
    "name": "Campaign Name",
    "description": "Campaign Description",
    "status": "active"
  }
}
```

## Database Schema

### Projects Table
- Project details (name, description, status)
- Webhook tracking (source_system, source_id, source_reference)
- Campaign grouping (campaign_id)
- Metadata (JSON)
- Timestamps

### Campaigns Table
- Campaign details (name, description, status)
- Source tracking for webhook-created campaigns
- Metadata (JSON)
- Timestamps

### Supporting Tables
- `checklist_items` - Todo items for projects
- `comments` - Discussion threads

## Configuration

Create a `.env` file in the `backend` directory:

```env
WEBHOOK_SECRET=your-secret-key-change-this
DATABASE_URL=demo.db
APP_ENV=development
DEBUG=True
```

## Production Deployment

For production, consider:
- Use PostgreSQL instead of SQLite
- Add Redis for Celery background tasks
- Use Docker Compose for orchestration
- Enable HTTPS with proper SSL certificates
- Configure CORS for production domains

## Integration with Laravel Applications

This system is designed to work with:

1. **Laravel 11 (AdMe CMS)** - Sends banner booking data
2. **Laravel 9 (Digital Operations)** - Sends request data (eDM, CME, etc.)

Both Laravel applications send webhooks when:
- New projects are created
- Project status changes
- Important updates occur

## License

Internal MIMS Digital Operations Tool

## Support

For issues or questions, contact the MIMS Digital Operations team.
