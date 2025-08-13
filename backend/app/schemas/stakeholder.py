from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class StakeholderBase(BaseModel):
    client_id: int
    name: str
    role: str
    tone: str
    priority_1: Optional[str] = None
    priority_2: Optional[str] = None
    priority_3: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ['direct', 'collaborative', 'analytical', 'strategic']
        if v not in valid_tones:
            raise ValueError(f'tone must be one of {valid_tones}')
        return v

class StakeholderCreate(StakeholderBase):
    pass

class StakeholderUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    tone: Optional[str] = None
    priority_1: Optional[str] = None
    priority_2: Optional[str] = None
    priority_3: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @validator('tone')
    def validate_tone(cls, v):
        if v is not None:
            valid_tones = ['direct', 'collaborative', 'analytical', 'strategic']
            if v not in valid_tones:
                raise ValueError(f'tone must be one of {valid_tones}')
        return v

class Stakeholder(StakeholderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True