import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [view, setView] = useState('dashboard'); // 'dashboard' or 'project'
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [checklist, setChecklist] = useState([]);
  const [comments, setComments] = useState([]);
  const [newChecklistItem, setNewChecklistItem] = useState('');
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '', status: 'active' });

  useEffect(() => {
    loadProjects();
    const interval = setInterval(loadProjects, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (currentProject && view === 'project') {
      loadChecklist(currentProject.id);
      loadComments(currentProject.id);
    }
  }, [currentProject, view]);

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API_URL}/projects/stats`);
      setProjects(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading projects:', error);
      setLoading(false);
    }
  };

  const loadChecklist = async (projectId) => {
    try {
      const response = await axios.get(`${API_URL}/projects/${projectId}/checklist`);
      setChecklist(response.data);
    } catch (error) {
      console.error('Error loading checklist:', error);
    }
  };

  const loadComments = async (projectId) => {
    try {
      const response = await axios.get(`${API_URL}/projects/${projectId}/comments`);
      setComments(response.data);
    } catch (error) {
      console.error('Error loading comments:', error);
    }
  };

  const createProject = async (e) => {
    e.preventDefault();
    if (!newProject.name.trim()) return;

    try {
      await axios.post(`${API_URL}/projects`, newProject);
      setNewProject({ name: '', description: '', status: 'active' });
      setShowCreateModal(false);
      loadProjects();
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const openProject = (project) => {
    setCurrentProject(project);
    setView('project');
  };

  const toggleChecklistItem = async (itemId, completed) => {
    try {
      await axios.patch(`${API_URL}/checklist/${itemId}`, null, {
        params: { completed: !completed }
      });
      loadChecklist(currentProject.id);
      loadProjects(); // Refresh to update stats
    } catch (error) {
      console.error('Error updating checklist:', error);
    }
  };

  const addChecklistItem = async (e) => {
    e.preventDefault();
    if (!newChecklistItem.trim()) return;

    try {
      await axios.post(`${API_URL}/checklist`, {
        project_id: currentProject.id,
        title: newChecklistItem,
        completed: false
      });
      setNewChecklistItem('');
      loadChecklist(currentProject.id);
      loadProjects(); // Refresh to update stats
    } catch (error) {
      console.error('Error adding checklist item:', error);
    }
  };

  const addComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await axios.post(`${API_URL}/comments`, {
        project_id: currentProject.id,
        user_name: 'Demo User',
        content: newComment
      });
      setNewComment('');
      loadComments(currentProject.id);
      loadProjects(); // Refresh to update stats
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Filter projects
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (project.description && project.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return <div className="loading">Loading Project Management System...</div>;
  }

  // Dashboard View
  if (view === 'dashboard') {
    return (
      <div className="app">
        <header className="header">
          <h1>🚀 Project Management Dashboard</h1>
          <p>Manage all your projects in one place</p>
        </header>

        <div className="container">
          <div className="toolbar">
            <div className="search-bar">
              <input
                type="text"
                placeholder="🔍 Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="on-hold">On Hold</option>
              </select>
            </div>
            <button className="create-btn" onClick={() => setShowCreateModal(true)}>
              + New Project
            </button>
          </div>

          <div className="project-stats-summary">
            <div className="summary-card">
              <div className="summary-value">{projects.length}</div>
              <div className="summary-label">Total Projects</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{projects.filter(p => p.status === 'active').length}</div>
              <div className="summary-label">Active</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">
                {Math.round(projects.reduce((sum, p) => sum + p.progress, 0) / projects.length || 0)}%
              </div>
              <div className="summary-label">Avg Progress</div>
            </div>
          </div>

          <div className="project-grid">
            {filteredProjects.map((project) => (
              <div key={project.id} className="project-card" onClick={() => openProject(project)}>
                <div className="project-card-header">
                  <h3>{project.name}</h3>
                  <span className={`status-badge ${project.status}`}>{project.status}</span>
                </div>
                <p className="project-description">{project.description}</p>

                <div className="progress-section">
                  <div className="progress-info">
                    <span>Progress</span>
                    <span className="progress-percentage">{project.progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${project.progress}%` }}></div>
                  </div>
                </div>

                <div className="project-meta">
                  <div className="meta-item">
                    <span>✅ {project.completed_tasks}/{project.total_tasks} Tasks</span>
                  </div>
                  <div className="meta-item">
                    <span>💬 {project.comment_count} Comments</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredProjects.length === 0 && (
            <div className="empty-state">
              <h3>No projects found</h3>
              <p>Try adjusting your filters or create a new project</p>
            </div>
          )}
        </div>

        {/* Create Project Modal */}
        {showCreateModal && (
          <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h2>Create New Project</h2>
              <form onSubmit={createProject}>
                <div className="form-group">
                  <label>Project Name *</label>
                  <input
                    type="text"
                    placeholder="Enter project name"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    placeholder="Project description"
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    rows="3"
                  />
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={newProject.status}
                    onChange={(e) => setNewProject({ ...newProject, status: e.target.value })}
                  >
                    <option value="active">Active</option>
                    <option value="on-hold">On Hold</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">Create Project</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Project Detail View
  const progress = checklist.length > 0
    ? Math.round((checklist.filter(item => item.completed).length / checklist.length) * 100)
    : 0;
  const completedCount = checklist.filter(item => item.completed).length;

  return (
    <div className="app">
      <header className="header">
        <div>
          <button className="back-btn" onClick={() => setView('dashboard')}>
            ← Back to Dashboard
          </button>
          <h1>📋 {currentProject.name}</h1>
          <p>{currentProject.description}</p>
        </div>
      </header>

      <div className="container">
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{progress}%</div>
            <div className="stat-label">Completion</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{completedCount}/{checklist.length}</div>
            <div className="stat-label">Tasks Done</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{comments.length}</div>
            <div className="stat-label">Comments</div>
          </div>
        </div>

        <div className="dashboard">
          <div className="card">
            <h2>✅ Project Checklist</h2>
            <div>
              {checklist.map((item) => (
                <div
                  key={item.id}
                  className={`checklist-item ${item.completed ? 'completed' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={item.completed}
                    onChange={() => toggleChecklistItem(item.id, item.completed)}
                  />
                  <span>{item.title}</span>
                </div>
              ))}
            </div>
            <form onSubmit={addChecklistItem} className="add-form">
              <input
                type="text"
                placeholder="Add new task..."
                value={newChecklistItem}
                onChange={(e) => setNewChecklistItem(e.target.value)}
              />
              <button type="submit">Add</button>
            </form>
          </div>

          <div className="card">
            <h2>💬 Comments & Discussion</h2>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {comments.map((comment) => (
                <div key={comment.id} className="comment">
                  <div className="comment-header">
                    <span className="comment-author">{comment.user_name}</span>
                    <span className="comment-date">
                      {comment.created_at ? formatDate(comment.created_at) : 'Just now'}
                    </span>
                  </div>
                  <div className="comment-content">{comment.content}</div>
                </div>
              ))}
            </div>
            <form onSubmit={addComment} className="add-form">
              <textarea
                placeholder="Add a comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                rows="2"
              />
              <button type="submit">Post</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
