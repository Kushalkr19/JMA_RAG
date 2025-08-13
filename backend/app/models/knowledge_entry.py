from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"))
    entry_type = Column(String(50), nullable=False)  # meeting_transcript, email, document, note
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(500))
    meeting_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="knowledge_entries")
    engagement = relationship("Engagement", back_populates="knowledge_entries")
    stakeholder = relationship("Stakeholder", back_populates="knowledge_entries")
    embedding = relationship("KnowledgeEmbedding", back_populates="knowledge_entry", uselist=False)