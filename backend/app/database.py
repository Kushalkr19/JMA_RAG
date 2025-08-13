from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jma_user:jma_password@localhost:5432/jma_knowledge_base")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models to ensure they are registered
from app.models.client import Client
from app.models.stakeholder import Stakeholder
from app.models.engagement import Engagement
from app.models.knowledge_entry import KnowledgeEntry
from app.models.knowledge_embedding import KnowledgeEmbedding
from app.models.deliverable import Deliverable
from app.models.audit_log import AuditLog