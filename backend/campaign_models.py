"""
Pydantic models for campaigns
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class Campaign(BaseModel):
    """Campaign model"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=500, description="Campaign name")
    description: Optional[str] = Field(None, max_length=5000, description="Campaign description")
    status: str = Field(default="active", description="Campaign status: active, completed, cancelled")
    source_system: Optional[str] = Field(None, description="Source system if from webhook")
    source_id: Optional[str] = Field(None, description="Source system ID")
    source_reference: Optional[str] = Field(None, description="Human-readable reference")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Ensure status is one of the allowed values"""
        allowed_statuses = ['active', 'completed', 'cancelled', 'on-hold']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class CampaignCreate(BaseModel):
    """Model for creating a campaign"""
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    status: str = Field(default="active")
    metadata: Optional[Dict[str, Any]] = None


class CampaignUpdate(BaseModel):
    """Model for updating a campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CampaignWithProjects(Campaign):
    """Campaign model with associated projects"""
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="Projects in this campaign")
    project_count: int = Field(default=0, description="Number of projects in campaign")
    completed_projects: int = Field(default=0, description="Number of completed projects")


class WebhookCampaignData(BaseModel):
    """Campaign data within webhook payload"""
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    status: str = Field(default="active")
    metadata: Optional[Dict[str, Any]] = None


class WebhookPayloadWithCampaign(BaseModel):
    """Webhook payload with optional campaign"""
    source_system: str
    source_id: str
    source_reference: str
    event_type: str
    timestamp: str
    project: Dict[str, Any]
    campaign: Optional[WebhookCampaignData] = Field(None, description="Optional campaign to group projects")
    webhook_signature: str
