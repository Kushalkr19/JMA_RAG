from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class KnowledgeEntryBase(BaseModel):
    client_id: int
    engagement_id: Optional[int] = None
    stakeholder_id: Optional[int] = None
    entry_type: str
    title: str
    content: str
    source_url: Optional[str] = None
    meeting_date: Optional[datetime] = None

    @validator('entry_type')
    def validate_entry_type(cls, v):
        valid_types = ['meeting_transcript', 'email', 'document', 'note']
        if v not in valid_types:
            raise ValueError(f'entry_type must be one of {valid_types}')
        return v

class KnowledgeEntryCreate(KnowledgeEntryBase):
    pass

class KnowledgeEntryUpdate(BaseModel):
    engagement_id: Optional[int] = None
    stakeholder_id: Optional[int] = None
    entry_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    meeting_date: Optional[datetime] = None

    @validator('entry_type')
    def validate_entry_type(cls, v):
        if v is not None:
            valid_types = ['meeting_transcript', 'email', 'document', 'note']
            if v not in valid_types:
                raise ValueError(f'entry_type must be one of {valid_types}')
        return v

class KnowledgeEntry(KnowledgeEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class KnowledgeEntryWithEmbedding(KnowledgeEntry):
    has_embedding: bool = False