"""
Pydantic models for webhook payloads and database schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class WebhookProjectData(BaseModel):
    """Project data within the webhook payload"""
    name: str = Field(..., min_length=1, max_length=500, description="Project name")
    description: Optional[str] = Field(None, max_length=5000, description="Project description")
    status: str = Field(default="active", description="Project status: active, completed, cancelled")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata as JSON")

    @validator('status')
    def validate_status(cls, v):
        """Ensure status is one of the allowed values"""
        allowed_statuses = ['active', 'completed', 'cancelled', 'on-hold']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class WebhookPayload(BaseModel):
    """Complete webhook payload structure"""
    source_system: str = Field(..., description="Source system identifier: laravel11 or laravel9")
    source_id: str = Field(..., description="Original ID from source system")
    source_reference: str = Field(..., description="Human-readable reference (booking_key or ruid)")
    event_type: str = Field(..., description="Event type: created, updated, status_changed")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    project: WebhookProjectData = Field(..., description="Project data")
    webhook_signature: str = Field(..., description="HMAC-SHA256 signature for verification")

    @validator('source_system')
    def validate_source_system(cls, v):
        """Ensure source_system is valid"""
        allowed_systems = ['laravel11', 'laravel9', 'test']
        if v not in allowed_systems:
            raise ValueError(f"Source system must be one of: {', '.join(allowed_systems)}")
        return v

    @validator('event_type')
    def validate_event_type(cls, v):
        """Ensure event_type is valid"""
        allowed_events = ['created', 'updated', 'status_changed', 'deleted']
        if v not in allowed_events:
            raise ValueError(f"Event type must be one of: {', '.join(allowed_events)}")
        return v

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate ISO 8601 timestamp format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Timestamp must be in ISO 8601 format")
        return v


class WebhookResponse(BaseModel):
    """Response model for webhook endpoints"""
    status: str = Field(..., description="Response status: success or error")
    message: str = Field(..., description="Human-readable response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional response data")
