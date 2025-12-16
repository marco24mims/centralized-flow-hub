from pydantic import BaseModel, Field
from typing import List, Optional

class TemplateItem(BaseModel):
    id: Optional[int] = None
    template_id: Optional[int] = None
    title: str
    order_index: int = 0
    created_at: Optional[str] = None

class ChecklistTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ChecklistTemplateWithItems(ChecklistTemplate):
    items: List[TemplateItem] = Field(default_factory=list)
    item_count: int = Field(default=0)

class ChecklistTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    items: List[str] = Field(default_factory=list)  # List of item titles

class ChecklistTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    items: Optional[List[str]] = None  # List of item titles
