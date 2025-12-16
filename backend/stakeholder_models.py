from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Stakeholder(BaseModel):
    id: Optional[int] = None
    project_id: int
    name: str
    email: EmailStr
    role: Optional[str] = None
    access_level: str = "viewer"  # viewer, editor, admin
    created_at: Optional[str] = None

class StakeholderCreate(BaseModel):
    project_id: int
    name: str
    email: EmailStr
    role: Optional[str] = None
    access_level: str = Field(default="viewer", description="viewer, editor, or admin")

class StakeholderUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    access_level: Optional[str] = None
