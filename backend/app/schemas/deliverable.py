from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class DeliverableBase(BaseModel):
    client_id: int
    engagement_id: Optional[int] = None
    title: str
    deliverable_type: str
    status: str = "draft"
    ai_generated_content: Optional[str] = None
    final_content: Optional[str] = None
    file_path: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['draft', 'review', 'approved', 'final']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v

class DeliverableCreate(DeliverableBase):
    pass

class DeliverableUpdate(BaseModel):
    title: Optional[str] = None
    deliverable_type: Optional[str] = None
    status: Optional[str] = None
    ai_generated_content: Optional[str] = None
    final_content: Optional[str] = None
    file_path: Optional[str] = None
    approved_at: Optional[datetime] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['draft', 'review', 'approved', 'final']
            if v not in valid_statuses:
                raise ValueError(f'status must be one of {valid_statuses}')
        return v

class Deliverable(DeliverableBase):
    id: int
    generated_at: datetime
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeliverableGenerate(BaseModel):
    client_id: int
    engagement_id: Optional[int] = None
    title: str
    deliverable_type: str
    target_stakeholder_id: Optional[int] = None
    sections: list[str] = ["executive_summary", "key_recommendations"]