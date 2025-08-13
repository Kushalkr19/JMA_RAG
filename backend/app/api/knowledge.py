from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.knowledge_entry import KnowledgeEntry
from app.models.knowledge_embedding import KnowledgeEmbedding
from app.schemas.knowledge import KnowledgeEntryCreate, KnowledgeEntryUpdate, KnowledgeEntry as KnowledgeEntrySchema, KnowledgeEntryWithEmbedding
from app.utils.embeddings import embedding_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[KnowledgeEntryWithEmbedding])
def get_knowledge_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all knowledge entries"""
    entries = db.query(KnowledgeEntry).offset(skip).limit(limit).all()
    result = []
    for entry in entries:
        has_embedding = db.query(KnowledgeEmbedding).filter(KnowledgeEmbedding.knowledge_entry_id == entry.id).first() is not None
        entry_data = KnowledgeEntryWithEmbedding.from_orm(entry)
        entry_data.has_embedding = has_embedding
        result.append(entry_data)
    return result

@router.get("/client/{client_id}", response_model=List[KnowledgeEntryWithEmbedding])
def get_knowledge_entries_by_client(client_id: int, db: Session = Depends(get_db)):
    """Get all knowledge entries for a specific client"""
    entries = db.query(KnowledgeEntry).filter(KnowledgeEntry.client_id == client_id).all()
    result = []
    for entry in entries:
        has_embedding = db.query(KnowledgeEmbedding).filter(KnowledgeEmbedding.knowledge_entry_id == entry.id).first() is not None
        entry_data = KnowledgeEntryWithEmbedding.from_orm(entry)
        entry_data.has_embedding = has_embedding
        result.append(entry_data)
    return result

@router.get("/{entry_id}", response_model=KnowledgeEntryWithEmbedding)
def get_knowledge_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific knowledge entry"""
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    has_embedding = db.query(KnowledgeEmbedding).filter(KnowledgeEmbedding.knowledge_entry_id == entry.id).first() is not None
    entry_data = KnowledgeEntryWithEmbedding.from_orm(entry)
    entry_data.has_embedding = has_embedding
    return entry_data

@router.post("/", response_model=KnowledgeEntrySchema)
def create_knowledge_entry(entry: KnowledgeEntryCreate, db: Session = Depends(get_db)):
    """Create a new knowledge entry"""
    db_entry = KnowledgeEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.post("/{entry_id}/embed", response_model=dict)
def generate_embedding(entry_id: int, db: Session = Depends(get_db)):
    """Generate vector embedding for a knowledge entry"""
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    # Check if embedding already exists
    existing_embedding = db.query(KnowledgeEmbedding).filter(KnowledgeEmbedding.knowledge_entry_id == entry_id).first()
    if existing_embedding:
        return {"message": "Embedding already exists", "entry_id": entry_id}
    
    try:
        # Generate embedding
        embedding_vector = embedding_service.generate_embedding(entry.content)
        
        # Save embedding
        db_embedding = KnowledgeEmbedding(
            knowledge_entry_id=entry_id,
            embedding=embedding_vector
        )
        db.add(db_embedding)
        db.commit()
        
        return {"message": "Embedding generated successfully", "entry_id": entry_id}
        
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

@router.post("/ingest", response_model=KnowledgeEntrySchema)
def ingest_knowledge_entry(entry: KnowledgeEntryCreate, generate_embedding_flag: bool = True, db: Session = Depends(get_db)):
    """Ingest a new knowledge entry with optional embedding generation"""
    # Create knowledge entry
    db_entry = KnowledgeEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # Generate embedding if requested
    if generate_embedding_flag:
        try:
            embedding_vector = embedding_service.generate_embedding(entry.content)
            db_embedding = KnowledgeEmbedding(
                knowledge_entry_id=db_entry.id,
                embedding=embedding_vector
            )
            db.add(db_embedding)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to generate embedding during ingestion: {e}")
            # Continue without embedding
    
    return db_entry

@router.put("/{entry_id}", response_model=KnowledgeEntrySchema)
def update_knowledge_entry(entry_id: int, entry: KnowledgeEntryUpdate, db: Session = Depends(get_db)):
    """Update a knowledge entry"""
    db_entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    update_data = entry.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entry, field, value)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/{entry_id}")
def delete_knowledge_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a knowledge entry"""
    db_entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    db.delete(db_entry)
    db.commit()
    return {"message": "Knowledge entry deleted successfully"}