from pydantic import BaseModel, EmailStr
from typing import Optional, List

class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    source_system: str  # laravel11 or laravel9
    is_admin: bool
    department: Optional[str] = None
    roles: Optional[List[str]] = None
