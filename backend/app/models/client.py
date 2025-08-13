from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    stakeholders = relationship("Stakeholder", back_populates="client", cascade="all, delete-orphan")
    engagements = relationship("Engagement", back_populates="client", cascade="all, delete-orphan")
    knowledge_entries = relationship("KnowledgeEntry", back_populates="client", cascade="all, delete-orphan")
    deliverables = relationship("Deliverable", back_populates="client", cascade="all, delete-orphan")