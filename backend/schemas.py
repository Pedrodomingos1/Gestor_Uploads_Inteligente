from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    image_path: str
    caption: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    status: str
    attempts: int
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
