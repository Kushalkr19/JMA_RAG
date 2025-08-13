from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Deliverable(Base):
    __tablename__ = "deliverables"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    title = Column(String(255), nullable=False)
    deliverable_type = Column(String(100), nullable=False)
    status = Column(String(50), default="draft")  # draft, review, approved, final
    ai_generated_content = Column(Text)
    final_content = Column(Text)
    file_path = Column(String(500))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="deliverables")
    engagement = relationship("Engagement", back_populates="deliverables")