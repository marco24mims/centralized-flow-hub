import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AuthProvider, useAuth } from './AuthContext';
import LoginPrompt from './LoginPrompt';

// Dynamically construct API URL based on current hostname
const getApiUrl = () => {
  const hostname = window.location.hostname;
  // If accessing via IP address, use that IP for API
  // Otherwise use localhost (for local development)
  const apiHost = hostname === 'localhost' || hostname === '127.0.0.1'
    ? 'localhost'
    : hostname;
  return `http://${apiHost}:8000/api`;
};

const API_URL = getApiUrl();

// Wrapper component with AuthProvider
function AppWithAuth() {
  return (
    <AuthProvider apiUrl={API_URL}>
      <App />
    </AuthProvider>
  );
}

function App() {
  const { user, loading: authLoading, authError } = useAuth();
  const [view, setView] = useState('dashboard'); // 'dashboard', 'project', 'campaigns', 'campaign', 'templates'
  const [projects, setProjects] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [currentCampaign, setCurrentCampaign] = useState(null);
  const [checklist, setChecklist] = useState([]);
  const [comments, setComments] = useState([]);
  const [stakeholders, setStakeholders] = useState([]);
  const [newChecklistItem, setNewChecklistItem] = useState('');
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [campaignFilter, setCampaignFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCreateCampaignModal, setShowCreateCampaignModal] = useState(false);
  const [showCreateTemplateModal, setShowCreateTemplateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showStakeholderModal, setShowStakeholderModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '', status: 'active', campaign_id: null });
  const [newCampaign, setNewCampaign] = useState({ name: '', description: '', status: 'active' });
  const [newTemplate, setNewTemplate] = useState({ name: '', description: '', items: [''] });
  const [newStakeholder, setNewStakeholder] = useState({ name: '', email: '', role: '', access_level: 'viewer' });
  const [editedProject, setEditedProject] = useState(null);

  useEffect(() => {
    loadProjects();
    loadCampaigns();
    const interval = setInterval(() => {
      loadProjects();
      loadCampaigns();
    }, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (currentProject && view === 'project') {
      loadChecklist(currentProject.id);
      loadComments(currentProject.id);
      loadStakeholders(currentProject.id);
    }
  }, [currentProject, view]);

  useEffect(() => {
    if (currentCampaign && view === 'campaign') {
      loadCampaignDetails(currentCampaign.id);
    }
  }, [currentCampaign, view]);

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>Loading...</div>
          <div style={{ fontSize: '14px', color: '#666' }}>Checking authentication...</div>
        </div>
      </div>
    );
  }

  // Show login prompt if not authenticated
  if (!user) {
    return <LoginPrompt authError={authError} />;
  }

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API_URL}/projects/stats`, {
        withCredentials: true
      });
      setProjects(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading projects:', error);
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await axios.get(`${API_URL}/campaigns`);
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    }
  };

  const loadCampaignDetails = async (campaignId) => {
    try {
      const response = await axios.get(`${API_URL}/campaigns/${campaignId}`);
      setCurrentCampaign(response.data);
    } catch (error) {
      console.error('Error loading campaign details:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_URL}/checklist-templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadStakeholders = async (projectId) => {
    try {
      const response = await axios.get(`${API_URL}/projects/${projectId}/stakeholders`);
      setStakeholders(response.data);
    } catch (error) {
      console.error('Error loading stakeholders:', error);
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
      setNewProject({ name: '', description: '', status: 'active', campaign_id: null });
      setShowCreateModal(false);
      loadProjects();
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const createCampaign = async (e) => {
    e.preventDefault();
    if (!newCampaign.name.trim()) return;

    try {
      await axios.post(`${API_URL}/campaigns`, newCampaign);
      setNewCampaign({ name: '', description: '', status: 'active' });
      setShowCreateCampaignModal(false);
      loadCampaigns();
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
  };

  const openEditModal = (project) => {
    setEditedProject({ ...project });
    setShowEditModal(true);
  };

  const updateProject = async (e) => {
    e.preventDefault();
    if (!editedProject || !editedProject.name.trim()) return;

    try {
      await axios.put(`${API_URL}/projects/${editedProject.id}`, editedProject);
      setShowEditModal(false);
      setEditedProject(null);
      loadProjects();
      // Update current project if we're viewing it
      if (currentProject && currentProject.id === editedProject.id) {
        setCurrentProject(editedProject);
      }
    } catch (error) {
      console.error('Error updating project:', error);
    }
  };

  const openProject = (project) => {
    setCurrentProject(project);
    setView('project');
  };

  const openCampaign = (campaign) => {
    setCurrentCampaign(campaign);
    setView('campaign');
  };

  const deleteProject = async (projectId) => {
    if (!window.confirm('Are you sure you want to delete this project? This will also delete all checklists and comments.')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/projects/${projectId}`);
      loadProjects();
      setView('dashboard');
    } catch (error) {
      console.error('Error deleting project:', error);
      alert('Failed to delete project');
    }
  };

  const deleteCampaign = async (campaignId) => {
    if (!window.confirm('Are you sure you want to delete this campaign? Projects will be unlinked but not deleted.')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/campaigns/${campaignId}`);
      loadCampaigns();
      setView('campaigns');
    } catch (error) {
      console.error('Error deleting campaign:', error);
      alert('Failed to delete campaign');
    }
  };

  const addStakeholder = async (e) => {
    e.preventDefault();
    if (!newStakeholder.name.trim() || !newStakeholder.email.trim()) return;

    try {
      await axios.post(`${API_URL}/stakeholders`, {
        ...newStakeholder,
        project_id: currentProject.id
      });
      setNewStakeholder({ name: '', email: '', role: '', access_level: 'viewer' });
      setShowStakeholderModal(false);
      loadStakeholders(currentProject.id);
    } catch (error) {
      console.error('Error adding stakeholder:', error);
      alert(error.response?.data?.detail || 'Failed to add stakeholder');
    }
  };

  const removeStakeholder = async (stakeholderId) => {
    if (!window.confirm('Are you sure you want to remove this stakeholder?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/stakeholders/${stakeholderId}`);
      loadStakeholders(currentProject.id);
    } catch (error) {
      console.error('Error removing stakeholder:', error);
    }
  };

  const applyTemplateToProject = async (templateId) => {
    try {
      await axios.post(`${API_URL}/projects/${currentProject.id}/apply-template/${templateId}`);
      setShowTemplateModal(false);
      loadChecklist(currentProject.id);
      loadProjects();
    } catch (error) {
      console.error('Error applying template:', error);
      alert('Failed to apply template');
    }
  };

  const createTemplate = async (e) => {
    e.preventDefault();
    if (!newTemplate.name.trim()) return;

    // Filter out empty items
    const items = newTemplate.items.filter(item => item.trim() !== '');
    if (items.length === 0) {
      alert('Please add at least one checklist item');
      return;
    }

    try {
      await axios.post(`${API_URL}/checklist-templates`, {
        name: newTemplate.name,
        description: newTemplate.description,
        items: items
      });
      setNewTemplate({ name: '', description: '', items: [''] });
      setShowCreateTemplateModal(false);
      loadTemplates();
    } catch (error) {
      console.error('Error creating template:', error);
      alert('Failed to create template');
    }
  };

  const deleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/checklist-templates/${templateId}`);
      loadTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Failed to delete template');
    }
  };

  const addTemplateItem = () => {
    setNewTemplate({ ...newTemplate, items: [...newTemplate.items, ''] });
  };

  const updateTemplateItem = (index, value) => {
    const updatedItems = [...newTemplate.items];
    updatedItems[index] = value;
    setNewTemplate({ ...newTemplate, items: updatedItems });
  };

  const removeTemplateItem = (index) => {
    if (newTemplate.items.length <= 1) {
      alert('Template must have at least one item');
      return;
    }
    const updatedItems = newTemplate.items.filter((_, i) => i !== index);
    setNewTemplate({ ...newTemplate, items: updatedItems });
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
    const matchesCampaign = campaignFilter === 'all' ||
                           (campaignFilter === 'none' && !project.campaign_id) ||
                           (project.campaign_id && project.campaign_id.toString() === campaignFilter);
    return matchesSearch && matchesStatus && matchesCampaign;
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
          <div style={{ marginTop: '10px' }}>
            <button
              className="nav-btn"
              onClick={() => setView('campaigns')}
              style={{ marginRight: '10px', padding: '8px 16px', cursor: 'pointer' }}
            >
              📁 View Campaigns
            </button>
            <button
              className="nav-btn"
              onClick={() => { setView('templates'); loadTemplates(); }}
              style={{ marginRight: '10px', padding: '8px 16px', cursor: 'pointer' }}
            >
              📋 Manage Templates
            </button>
          </div>
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
              <select value={campaignFilter} onChange={(e) => setCampaignFilter(e.target.value)}>
                <option value="all">All Campaigns</option>
                <option value="none">No Campaign</option>
                {campaigns.map(campaign => (
                  <option key={campaign.id} value={campaign.id.toString()}>{campaign.name}</option>
                ))}
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
                <div className="form-group">
                  <label>Campaign (Optional)</label>
                  <select
                    value={newProject.campaign_id || ''}
                    onChange={(e) => setNewProject({ ...newProject, campaign_id: e.target.value ? parseInt(e.target.value) : null })}
                  >
                    <option value="">No Campaign</option>
                    {campaigns.map(campaign => (
                      <option key={campaign.id} value={campaign.id}>{campaign.name}</option>
                    ))}
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

  // Campaigns View
  if (view === 'campaigns') {
    return (
      <div className="app">
        <header className="header">
          <div>
            <button className="back-btn" onClick={() => setView('dashboard')}>
              ← Back to Dashboard
            </button>
            <h1>📁 Campaign Management</h1>
            <p>Organize projects into campaigns</p>
          </div>
        </header>

        <div className="container">
          <div className="toolbar">
            <button className="create-btn" onClick={() => setShowCreateCampaignModal(true)}>
              + New Campaign
            </button>
          </div>

          <div className="project-grid">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="project-card" onClick={() => openCampaign(campaign)}>
                <div className="project-card-header">
                  <h3>{campaign.name}</h3>
                  <span className={`status-badge ${campaign.status}`}>{campaign.status}</span>
                </div>
                <p className="project-description">{campaign.description}</p>

                <div className="project-meta">
                  <div className="meta-item">
                    <span>📊 {campaign.project_count || 0} Projects</span>
                  </div>
                  <div className="meta-item">
                    <span>✅ {campaign.completed_projects || 0} Completed</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {campaigns.length === 0 && (
            <div className="empty-state">
              <h3>No campaigns yet</h3>
              <p>Create your first campaign to organize projects</p>
            </div>
          )}
        </div>

        {/* Create Campaign Modal */}
        {showCreateCampaignModal && (
          <div className="modal-overlay" onClick={() => setShowCreateCampaignModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h2>Create New Campaign</h2>
              <form onSubmit={createCampaign}>
                <div className="form-group">
                  <label>Campaign Name *</label>
                  <input
                    type="text"
                    placeholder="Enter campaign name"
                    value={newCampaign.name}
                    onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    placeholder="Campaign description"
                    value={newCampaign.description}
                    onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                    rows="3"
                  />
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={newCampaign.status}
                    onChange={(e) => setNewCampaign({ ...newCampaign, status: e.target.value })}
                  >
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn-secondary" onClick={() => setShowCreateCampaignModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">Create Campaign</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Campaign Detail View
  if (view === 'campaign' && currentCampaign) {
    return (
      <div className="app">
        <header className="header">
          <div>
            <button className="back-btn" onClick={() => setView('campaigns')}>
              ← Back to Campaigns
            </button>
            <button
              onClick={() => deleteCampaign(currentCampaign.id)}
              style={{ marginLeft: '10px', padding: '8px 16px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              🗑️ Delete Campaign
            </button>
            <h1>📁 {currentCampaign.name}</h1>
            <p>{currentCampaign.description}</p>
          </div>
        </header>

        <div className="container">
          <div className="stats">
            <div className="stat-card">
              <div className="stat-value">{currentCampaign.project_count || 0}</div>
              <div className="stat-label">Total Projects</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{currentCampaign.completed_projects || 0}</div>
              <div className="stat-label">Completed</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {currentCampaign.project_count > 0
                  ? Math.round((currentCampaign.completed_projects / currentCampaign.project_count) * 100)
                  : 0}%
              </div>
              <div className="stat-label">Progress</div>
            </div>
          </div>

          <h2 style={{ marginTop: '30px', marginBottom: '20px' }}>Campaign Projects</h2>
          <div className="project-grid">
            {currentCampaign.projects && currentCampaign.projects.map((project) => (
              <div key={project.id} className="project-card" onClick={() => openProject(project)}>
                <div className="project-card-header">
                  <h3>{project.name}</h3>
                  <span className={`status-badge ${project.status}`}>{project.status}</span>
                </div>
                <p className="project-description">{project.description}</p>

                <div className="progress-section">
                  <div className="progress-info">
                    <span>Progress</span>
                    <span className="progress-percentage">{project.progress || 0}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${project.progress || 0}%` }}></div>
                  </div>
                </div>

                <div className="project-meta">
                  <div className="meta-item">
                    <span>✅ {project.completed_tasks || 0}/{project.total_tasks || 0} Tasks</span>
                  </div>
                  <div className="meta-item">
                    <span>💬 {project.comment_count || 0} Comments</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {(!currentCampaign.projects || currentCampaign.projects.length === 0) && (
            <div className="empty-state">
              <h3>No projects in this campaign</h3>
              <p>Add projects to this campaign from the project creation form</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Templates Management View
  if (view === 'templates') {
    return (
      <div className="app">
        <header className="header">
          <div>
            <button className="back-btn" onClick={() => setView('dashboard')}>
              ← Back to Dashboard
            </button>
            <h1>📋 Checklist Template Management</h1>
            <p>Create and manage reusable checklist templates</p>
          </div>
        </header>

        <div className="container">
          <div className="toolbar">
            <button className="create-btn" onClick={() => setShowCreateTemplateModal(true)}>
              + New Template
            </button>
          </div>

          <div className="project-grid">
            {templates.map((template) => (
              <div key={template.id} className="project-card">
                <div className="project-card-header">
                  <h3>{template.name}</h3>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteTemplate(template.id); }}
                    style={{ padding: '4px 12px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Delete
                  </button>
                </div>
                <p className="project-description">{template.description || 'No description'}</p>

                <div style={{ marginTop: '15px' }}>
                  <strong style={{ fontSize: '0.9em', color: '#666' }}>Checklist Items ({template.item_count}):</strong>
                  <ul style={{ marginTop: '8px', marginLeft: '20px', fontSize: '0.9em', color: '#555' }}>
                    {template.items && template.items.map((item, idx) => (
                      <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="project-meta" style={{ marginTop: '15px' }}>
                  <div className="meta-item">
                    <span>Created: {template.created_at ? new Date(template.created_at).toLocaleDateString() : 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {templates.length === 0 && (
            <div className="empty-state">
              <h3>No templates yet</h3>
              <p>Create your first checklist template to get started</p>
            </div>
          )}
        </div>

        {/* Create Template Modal */}
        {showCreateTemplateModal && (
          <div className="modal-overlay" onClick={() => setShowCreateTemplateModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h2>Create New Template</h2>
              <form onSubmit={createTemplate}>
                <div className="form-group">
                  <label>Template Name *</label>
                  <input
                    type="text"
                    placeholder="e.g., Standard Project Checklist"
                    value={newTemplate.name}
                    onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    placeholder="Template description"
                    value={newTemplate.description}
                    onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                    rows="2"
                  />
                </div>
                <div className="form-group">
                  <label>Checklist Items *</label>
                  {newTemplate.items.map((item, index) => (
                    <div key={index} style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                      <input
                        type="text"
                        placeholder={`Item ${index + 1}`}
                        value={item}
                        onChange={(e) => updateTemplateItem(index, e.target.value)}
                        style={{ flex: 1 }}
                      />
                      {newTemplate.items.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeTemplateItem(index)}
                          style={{ padding: '8px 12px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={addTemplateItem}
                    style={{ marginTop: '8px', padding: '8px 16px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    + Add Item
                  </button>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn-secondary" onClick={() => { setShowCreateTemplateModal(false); setNewTemplate({ name: '', description: '', items: [''] }); }}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">Create Template</button>
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
          <button
            className="create-btn"
            onClick={() => openEditModal(currentProject)}
            style={{ marginLeft: '10px', padding: '8px 16px' }}
          >
            ✏️ Edit Project
          </button>
          <button
            className="create-btn"
            onClick={() => { loadTemplates(); setShowTemplateModal(true); }}
            style={{ marginLeft: '10px', padding: '8px 16px', backgroundColor: '#2196F3' }}
          >
            📋 Apply Template
          </button>
          <button
            onClick={() => deleteProject(currentProject.id)}
            style={{ marginLeft: '10px', padding: '8px 16px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            🗑️ Delete Project
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
          <div className="stat-card">
            <div className="stat-value">{stakeholders.length}</div>
            <div className="stat-label">Stakeholders</div>
          </div>
        </div>

        <div className="dashboard">
          <div className="card">
            <h2>👥 Project Stakeholders</h2>
            <div style={{ marginBottom: '15px' }}>
              {stakeholders.map((stakeholder) => (
                <div key={stakeholder.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', border: '1px solid #e0e0e0', borderRadius: '4px', marginBottom: '8px' }}>
                  <div>
                    <strong>{stakeholder.name}</strong>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      {stakeholder.email} • {stakeholder.role || 'No role'} • {stakeholder.access_level}
                    </div>
                  </div>
                  <button
                    onClick={() => removeStakeholder(stakeholder.id)}
                    style={{ padding: '4px 8px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Remove
                  </button>
                </div>
              ))}
              {stakeholders.length === 0 && (
                <p style={{ color: '#666', textAlign: 'center' }}>No stakeholders yet</p>
              )}
            </div>
            <button
              onClick={() => setShowStakeholderModal(true)}
              style={{ width: '100%', padding: '10px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              + Add Stakeholder
            </button>
          </div>

          {/* Webhook Details Card */}
          {currentProject.source_system && (
            <div className="card">
              <h2>🔗 Webhook Integration Details</h2>
              <div style={{ maxHeight: '300px', overflowY: 'auto', fontSize: '0.9em' }}>
                <div style={{ marginBottom: '15px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '12px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontWeight: 'bold', color: '#555' }}>Source System:</div>
                    <div style={{ color: '#333' }}>
                      <span style={{
                        padding: '4px 12px',
                        backgroundColor: currentProject.source_system === 'laravel11' ? '#4CAF50' : '#2196F3',
                        color: 'white',
                        borderRadius: '12px',
                        fontSize: '0.85em',
                        fontWeight: 'bold'
                      }}>
                        {currentProject.source_system === 'laravel11' ? 'Laravel 11 (AdMe CMS)' : 'Laravel 9 (Digital Products)'}
                      </span>
                    </div>

                    <div style={{ fontWeight: 'bold', color: '#555' }}>Source ID:</div>
                    <div style={{ fontFamily: 'monospace', color: '#333' }}>{currentProject.source_id}</div>

                    <div style={{ fontWeight: 'bold', color: '#555' }}>Reference:</div>
                    <div style={{ fontFamily: 'monospace', color: '#333', fontWeight: 'bold' }}>
                      {currentProject.source_reference}
                    </div>

                    {currentProject.webhook_received_at && (
                      <>
                        <div style={{ fontWeight: 'bold', color: '#555' }}>Received At:</div>
                        <div style={{ color: '#333' }}>{formatDate(currentProject.webhook_received_at)}</div>
                      </>
                    )}

                    {currentProject.last_synced_at && (
                      <>
                        <div style={{ fontWeight: 'bold', color: '#555' }}>Last Synced:</div>
                        <div style={{ color: '#333' }}>{formatDate(currentProject.last_synced_at)}</div>
                      </>
                    )}
                  </div>
                </div>

                {/* Metadata Section */}
                {currentProject.metadata && currentProject.metadata !== '{}' && (
                  <div style={{ marginTop: '15px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#555', fontSize: '0.95em' }}>
                      📦 Additional Metadata:
                    </div>
                    <div style={{
                      backgroundColor: '#f8f9fa',
                      padding: '12px',
                      borderRadius: '6px',
                      border: '1px solid #e0e0e0',
                      maxHeight: '150px',
                      overflowY: 'auto'
                    }}>
                      <pre style={{
                        margin: 0,
                        fontSize: '0.85em',
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        color: '#333'
                      }}>
                        {JSON.stringify(JSON.parse(currentProject.metadata), null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
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

      {/* Edit Project Modal */}
      {showEditModal && editedProject && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Edit Project</h2>
            <form onSubmit={updateProject}>
              <div className="form-group">
                <label>Project Name *</label>
                <input
                  type="text"
                  placeholder="Enter project name"
                  value={editedProject.name}
                  onChange={(e) => setEditedProject({ ...editedProject, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  placeholder="Project description"
                  value={editedProject.description || ''}
                  onChange={(e) => setEditedProject({ ...editedProject, description: e.target.value })}
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Status</label>
                <select
                  value={editedProject.status}
                  onChange={(e) => setEditedProject({ ...editedProject, status: e.target.value })}
                >
                  <option value="active">Active</option>
                  <option value="on-hold">On Hold</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div className="form-group">
                <label>Campaign</label>
                <select
                  value={editedProject.campaign_id || ''}
                  onChange={(e) => setEditedProject({ ...editedProject, campaign_id: e.target.value ? parseInt(e.target.value) : null })}
                >
                  <option value="">No Campaign</option>
                  {campaigns.map(campaign => (
                    <option key={campaign.id} value={campaign.id}>{campaign.name}</option>
                  ))}
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowEditModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Stakeholder Modal */}
      {showStakeholderModal && (
        <div className="modal-overlay" onClick={() => setShowStakeholderModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add Stakeholder</h2>
            <form onSubmit={addStakeholder}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  placeholder="Stakeholder name"
                  value={newStakeholder.name}
                  onChange={(e) => setNewStakeholder({ ...newStakeholder, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  placeholder="stakeholder@example.com"
                  value={newStakeholder.email}
                  onChange={(e) => setNewStakeholder({ ...newStakeholder, email: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Role</label>
                <input
                  type="text"
                  placeholder="e.g. Project Manager, Developer"
                  value={newStakeholder.role}
                  onChange={(e) => setNewStakeholder({ ...newStakeholder, role: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Access Level</label>
                <select
                  value={newStakeholder.access_level}
                  onChange={(e) => setNewStakeholder({ ...newStakeholder, access_level: e.target.value })}
                >
                  <option value="viewer">Viewer</option>
                  <option value="editor">Editor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowStakeholderModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Add Stakeholder</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Apply Template Modal */}
      {showTemplateModal && (
        <div className="modal-overlay" onClick={() => setShowTemplateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Apply Checklist Template</h2>
            <div style={{ marginBottom: '20px' }}>
              <p style={{ color: '#666', marginBottom: '15px' }}>
                Select a template to add its checklist items to this project
              </p>
              {templates.map((template) => (
                <div
                  key={template.id}
                  onClick={() => applyTemplateToProject(template.id)}
                  style={{
                    padding: '15px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    marginBottom: '10px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{template.name}</div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>
                    {template.description || 'No description'}
                  </div>
                  <div style={{ fontSize: '0.85em', color: '#999', marginTop: '5px' }}>
                    {template.item_count} items
                  </div>
                </div>
              ))}
              {templates.length === 0 && (
                <p style={{ color: '#999', textAlign: 'center' }}>No templates available</p>
              )}
            </div>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setShowTemplateModal(false)}
              style={{ width: '100%' }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AppWithAuth;
