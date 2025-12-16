# CFH Project - Frontend Setup Guide

The CFH Project includes a React-based frontend UI for managing projects, checklists, comments, and campaigns.

## Prerequisites

- Node.js 16+ and npm
- Backend API running (http://localhost:8000 or your server IP)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API Endpoint (Optional)

If your backend is running on a different host/port, you may need to update the API endpoint in the React app.

Edit `frontend/src/App.js` and look for the API base URL (usually around line 10-15):

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Change it to your server IP if needed:

```javascript
const API_BASE_URL = 'http://10.50.10.68:8000';
```

### 3. Start Development Server

```bash
npm start
```

The app will open at http://localhost:3000

### 4. Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Features

### Project Management
- View all projects with statistics
- See project progress (tasks completed vs total)
- View comment counts
- Filter projects by status and campaign
- Create new projects with campaign assignment

### Checklist Management
- View project checklists
- Toggle task completion
- Add new checklist items

### Comments
- View project comments
- Add new comments with user name
- Real-time updates (5-second polling)

### Campaign Grouping
- Create and manage campaigns
- Group related projects into campaigns
- View campaign statistics (project count, completion rate)
- Filter projects by campaign
- View all projects within a campaign
- Assign projects to campaigns during creation

## Deployment Options

### Option 1: Serve with Node.js

```bash
# Install serve globally
npm install -g serve

# Build the app
npm run build

# Serve the build folder
serve -s build -p 3000
```

### Option 2: Serve with Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /opt/lampp/htdocs/MIMS/centralized-flow-hub/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to FastAPI backend
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 3: Serve with Apache

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /opt/lampp/htdocs/MIMS/centralized-flow-hub/frontend/build

    <Directory /opt/lampp/htdocs/MIMS/centralized-flow-hub/frontend/build>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted

        # Enable React Router
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # Proxy API requests
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
</VirtualHost>
```

## Production Systemd Service (Recommended for Linux)

If you want the frontend to run as a background service that starts automatically on boot:

### Prerequisites

1. Build the React app:
```bash
npm run build
```

2. Install `serve` globally:
```bash
sudo npm install -g serve
```

### Automated Installation

```bash
cd frontend
chmod +x install-frontend-service.sh
sudo ./install-frontend-service.sh
```

This will:
- Install the systemd service
- Enable auto-start on boot
- Start the frontend service
- Set up logging to `/var/log/cfh-project/frontend-*.log`

### Manual Installation

1. Copy the service file:
```bash
sudo cp cfh-frontend.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/cfh-frontend.service
```

2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cfh-frontend
sudo systemctl start cfh-frontend
```

3. Check status:
```bash
sudo systemctl status cfh-frontend
```

### Useful Commands

```bash
sudo systemctl status cfh-frontend    # Check status
sudo systemctl start cfh-frontend     # Start service
sudo systemctl stop cfh-frontend      # Stop service
sudo systemctl restart cfh-frontend   # Restart service
sudo journalctl -u cfh-frontend -f    # Follow logs in real-time
```

## CORS Configuration

If you're running the frontend on a different domain/port than the backend, make sure CORS is configured in the backend `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://10.50.10.68:3000",
        "http://your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Cannot connect to backend API

1. Check if backend is running: `curl http://localhost:8000/`
2. Check CORS settings in backend
3. Update API_BASE_URL in `App.js` if backend is on different host

### Port 3000 already in use

```bash
# Use a different port
PORT=3001 npm start
```

### npm install fails

```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## UI Screenshots

The UI includes:
- **Dashboard**: Overview of all projects with stats
- **Project Detail**: View individual project with checklist and comments
- **Campaign View**: Group and manage related projects

For more information, see the main README.md
