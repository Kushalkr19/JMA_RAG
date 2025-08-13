from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    tone = Column(String(50), nullable=False)  # direct, collaborative, analytical, strategic
    priority_1 = Column(String(255))
    priority_2 = Column(String(255))
    priority_3 = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="stakeholders")
    knowledge_entries = relationship("KnowledgeEntry", back_populates="stakeholder")