from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    industry: Optional[str] = None
    description: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    name: Optional[str] = None

class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClientWithRelations(Client):
    stakeholders: List["Stakeholder"] = []
    engagements: List["Engagement"] = []
    knowledge_entries: List["KnowledgeEntry"] = []
    deliverables: List["Deliverable"] = []

    class Config:
        from_attributes = True