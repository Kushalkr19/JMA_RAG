from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

class KnowledgeEmbedding(Base):
    __tablename__ = "knowledge_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_entry_id = Column(Integer, ForeignKey("knowledge_entries.id"), nullable=False)
    embedding = Column(Vector(384))  # Using sentence-transformers all-MiniLM-L6-v2
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    knowledge_entry = relationship("KnowledgeEntry", back_populates="embedding")