# COMPLETE FILE MAPPING & SETUP GUIDE

## 📂 BACKEND FILES MAPPING

Copy each file content to the specified location:

### Root Backend Files
```
backend/.env                          → Copy from: backend_env.txt
backend/requirements.txt              → Copy from: backend_requirements.txt
backend/Dockerfile                    → Copy from: backend_Dockerfile.txt
backend/init_db.py                    → Copy from: backend_init_db.py
```

### App Directory Files
```
backend/app/__init__.py               → Create empty file
backend/app/config.py                 → Copy from: backend_config.py
backend/app/database.py               → Copy from: backend_database.py
backend/app/main.py                   → Copy from: backend_main.py
```

### Models Directory
```
backend/app/models/__init__.py        → Copy from: backend_models_init.py
backend/app/models/user.py            → Copy from: backend_model_user.py
backend/app/models/project.py         → Copy from: backend_model_project.py
backend/app/models/checklist.py       → Copy from: backend_model_checklist.py
backend/app/models/stakeholder.py     → Copy from: backend_model_stakeholder.py
backend/app/models/comment.py         → Copy from: backend_model_comment.py
backend/app/models/subscription.py    → Copy from: backend_model_subscription.py
backend/app/models/activity.py        → Copy from: backend_model_activity.py
```

### Schemas Directory
```
backend/app/schemas/__init__.py       → Copy from: backend_schemas.py
```

### Core Directory
```
backend/app/core/__init__.py          → Create empty file
backend/app/core/security.py          → Copy from: backend_security.py
```

### API Directory
```
backend/app/api/__init__.py           → Create empty file
backend/app/api/deps.py               → Copy from: backend_deps.py
backend/app/api/v1/__init__.py        → Create empty file
```
Note: All API endpoints are in main.py for POC simplicity

### Services Directory
```
backend/app/services/__init__.py      → Create empty file
```

### Celery Worker Directory
```
backend/celery_worker/__init__.py     → Create empty file
backend/celery_worker/celery_app.py   → Extract from: backend_celery.py (first part)
backend/celery_worker/tasks.py        → Extract from: backend_celery.py (second part)
```

---

## 📂 FRONTEND FILES MAPPING

### Root Frontend Files
```
frontend/.env                         → From frontend_code_part1.txt
frontend/package.json                 → Copy from: frontend_package.json
frontend/Dockerfile                   → From frontend_code_part1.txt
```

### Public Directory
```
frontend/public/index.html            → From frontend_code_part1.txt
```

### Src Root Files
```
frontend/src/index.jsx                → From frontend_code_part1.txt
frontend/src/index.css                → From frontend_code_part1.txt
frontend/src/App.jsx                  → From frontend_code_part2.txt
```

### Services Directory
```
frontend/src/services/api.js          → From frontend_code_part1.txt
```

### Pages Directory
```
frontend/src/pages/Login.jsx          → From frontend_code_part2.txt
frontend/src/pages/ProjectList.jsx    → From frontend_code_part2.txt
frontend/src/pages/ProjectDashboard.jsx → From frontend_code_part2.txt
```

### Components - Checklist
```
frontend/src/components/Checklist/ChecklistList.jsx → From frontend_code_part3.txt
frontend/src/components/Checklist/ChecklistItem.jsx → From frontend_code_part3.txt
frontend/src/components/Checklist/AddChecklistForm.jsx → From frontend_code_part3.txt
```

### Components - Comments
```
frontend/src/components/Comments/CommentSection.jsx → From frontend_code_part3.txt
frontend/src/components/Comments/Comment.jsx → From frontend_code_part3.txt
frontend/src/components/Comments/CommentForm.jsx → From frontend_code_part3.txt
```

### Components - Stakeholders
```
frontend/src/components/Stakeholders/StakeholderList.jsx → From frontend_code_part4.txt
frontend/src/components/Stakeholders/AddStakeholderModal.jsx → From frontend_code_part4.txt
```

### Components - Subscription
```
frontend/src/components/Subscription/SubscriptionToggle.jsx → From frontend_code_part4.txt
```

---

## 📂 ROOT FILES
```
docker-compose.yml                    → Copy from: docker-compose.yml
```

---

## 🔧 LARAVEL INTEGRATION FILES

### Laravel Service Class
File: `app/Services/ProjectManagementService.php`

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Firebase\JWT\JWT;

class ProjectManagementService
{
    private $baseUrl;
    private $secret;

    public function __construct()
    {
        $this->baseUrl = env('PROJECT_MANAGEMENT_URL', 'http://localhost:8000');
        $this->secret = env('JWT_SECRET', 'your-super-secret-jwt-key-change-this-in-production');
    }

    /**
     * Create project in PM system
     */
    public function createProject($project)
    {
        try {
            $token = $this->generateToken(auth()->user());
            
            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $token,
                'Content-Type' => 'application/json',
            ])->post($this->baseUrl . '/api/v1/projects', [
                'laravel_project_id' => $project->id,
                'name' => $project->name,
                'project_type_id' => $project->project_type_id ?? 1,
                'description' => $project->description,
            ]);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Failed to create project in PM system', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);

            return null;
        } catch (\Exception $e) {
            Log::error('Exception creating project in PM system', [
                'message' => $e->getMessage(),
            ]);
            return null;
        }
    }

    /**
     * Get project management URL
     */
    public function getProjectUrl($projectId)
    {
        $frontendUrl = env('FRONTEND_URL', 'http://localhost:3000');
        return $frontendUrl . '/projects/' . $projectId;
    }

    /**
     * Generate JWT token for user
     */
    public function generateToken($user)
    {
        $payload = [
            'sub' => $user->id,
            'email' => $user->email,
            'name' => $user->name,
            'iat' => time(),
            'exp' => time() + (60 * 60 * 24), // 24 hours
        ];

        return JWT::encode($payload, $this->secret, 'HS256');
    }

    /**
     * Create or sync user in PM system
     */
    public function syncUser($user)
    {
        try {
            $response = Http::post($this->baseUrl . '/api/v1/auth/register', [
                'email' => $user->email,
                'name' => $user->name,
                'password' => 'sync-' . uniqid(), // Random password for synced users
                'laravel_user_id' => $user->id,
            ]);

            return $response->successful();
        } catch (\Exception $e) {
            // User might already exist, that's okay
            return true;
        }
    }
}
```

### Laravel Controller Example
File: `app/Http/Controllers/ProjectController.php`

```php
<?php

namespace App\Http\Controllers;

use App\Models\Project;
use App\Services\ProjectManagementService;
use Illuminate\Http\Request;

class ProjectController extends Controller
{
    private $pmService;

    public function __construct(ProjectManagementService $pmService)
    {
        $this->pmService = $pmService;
    }

    /**
     * Store a newly created project
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'project_type_id' => 'nullable|integer',
            'description' => 'nullable|string',
        ]);

        // Create project in Laravel
        $project = Project::create($validated);

        // Sync user to PM system (if not already synced)
        $this->pmService->syncUser(auth()->user());

        // Create project in Python PM system
        $pmProject = $this->pmService->createProject($project);

        if ($pmProject) {
            // Store Python project ID reference
            $project->update([
                'pm_project_id' => $pmProject['id']
            ]);
        }

        return response()->json([
            'success' => true,
            'project' => $project,
            'pm_url' => $pmProject ? $this->pmService->getProjectUrl($pmProject['id']) : null,
        ]);
    }

    /**
     * Redirect to project management interface
     */
    public function openProjectManagement($id)
    {
        $project = Project::findOrFail($id);
        
        if (!$project->pm_project_id) {
            return redirect()->back()->with('error', 'Project management not initialized for this project');
        }

        // Generate JWT token
        $token = $this->pmService->generateToken(auth()->user());
        
        // Redirect to React app with token
        $pmUrl = $this->pmService->getProjectUrl($project->pm_project_id);
        
        return redirect()->away($pmUrl . '?token=' . $token);
    }
}
```

### Laravel Migration
File: `database/migrations/xxxx_xx_xx_add_pm_project_id_to_projects.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::table('projects', function (Blueprint $table) {
            $table->uuid('pm_project_id')->nullable()->index()->after('id');
        });
    }

    public function down()
    {
        Schema::table('projects', function (Blueprint $table) {
            $table->dropColumn('pm_project_id');
        });
    }
};
```

### Laravel Routes
Add to `routes/web.php`:

```php
use App\Http\Controllers\ProjectController;

Route::middleware(['auth'])->group(function () {
    Route::post('/projects', [ProjectController::class, 'store']);
    Route::get('/projects/{id}/management', [ProjectController::class, 'openProjectManagement']);
});
```

### Laravel .env additions
```
PROJECT_MANAGEMENT_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

### Install JWT Package in Laravel
```bash
composer require firebase/php-jwt
```

---

## 🚀 QUICK SETUP SCRIPT

Save this as `setup.sh` in the project root:

```bash
#!/bin/bash

echo "🚀 Setting up Project Management POC..."

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p backend/app/{models,schemas,api/v1,core,services}
mkdir -p backend/celery_worker
mkdir -p frontend/src/{components/{Checklist,Comments,Stakeholders,Subscription},pages,services}
mkdir -p frontend/public

echo "✅ Directory structure created!"
echo ""
echo "📝 Next steps:"
echo "1. Copy all files according to the mapping above"
echo "2. Run: docker-compose up -d"
echo "3. Wait 30 seconds for initialization"
echo "4. Access: http://localhost:3000"
echo ""
echo "🎉 Happy coding!"
```

Make it executable:
```bash
chmod +x setup.sh
./setup.sh
```

---

## ✅ VERIFICATION CHECKLIST

After copying all files, verify:

- [ ] Backend has 50+ files total
- [ ] Frontend has 20+ files total
- [ ] docker-compose.yml is in root
- [ ] All .env files are in place
- [ ] No empty directories (except as noted)
- [ ] All __init__.py files created

---

## 🧪 TESTING THE POC

```bash
# 1. Start all services
docker-compose up -d

# 2. Check logs
docker-compose logs -f backend

# 3. Initialize database (if not auto-initialized)
docker-compose exec backend python init_db.py

# 4. Access the app
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs

# 5. Login with demo credentials
# Email: demo@example.com
# Password: demo123
```

---

Your POC is now complete! All files are mapped and ready to use.
