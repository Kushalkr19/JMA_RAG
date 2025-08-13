from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.deliverable import Deliverable
from app.models.client import Client
from app.models.stakeholder import Stakeholder
from app.models.knowledge_entry import KnowledgeEntry
from app.models.knowledge_embedding import KnowledgeEmbedding
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate, Deliverable as DeliverableSchema, DeliverableGenerate
from app.utils.ai_service import ai_service
from app.utils.document_generator import document_generator
from app.utils.embeddings import embedding_service
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[DeliverableSchema])
def get_deliverables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all deliverables"""
    deliverables = db.query(Deliverable).offset(skip).limit(limit).all()
    return deliverables

@router.get("/client/{client_id}", response_model=List[DeliverableSchema])
def get_deliverables_by_client(client_id: int, db: Session = Depends(get_db)):
    """Get all deliverables for a specific client"""
    deliverables = db.query(Deliverable).filter(Deliverable.client_id == client_id).all()
    return deliverables

@router.get("/{deliverable_id}", response_model=DeliverableSchema)
def get_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    """Get a specific deliverable"""
    deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return deliverable

@router.post("/generate", response_model=DeliverableSchema)
def generate_deliverable(request: DeliverableGenerate, db: Session = Depends(get_db)):
    """Generate a new deliverable using RAG pipeline"""
    try:
        # Get client information
        client = db.query(Client).filter(Client.id == request.client_id).first()
        if client is None:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get stakeholder information (if specified)
        stakeholder_info = {}
        if request.target_stakeholder_id:
            stakeholder = db.query(Stakeholder).filter(Stakeholder.id == request.target_stakeholder_id).first()
            if stakeholder is None:
                raise HTTPException(status_code=404, detail="Stakeholder not found")
            stakeholder_info = {
                'name': stakeholder.name,
                'role': stakeholder.role,
                'tone': stakeholder.tone,
                'priority_1': stakeholder.priority_1,
                'priority_2': stakeholder.priority_2,
                'priority_3': stakeholder.priority_3
            }
        else:
            # Default stakeholder info
            stakeholder_info = {
                'name': 'General Stakeholder',
                'role': 'Decision Maker',
                'tone': 'professional',
                'priority_1': 'Efficiency',
                'priority_2': 'Cost Optimization',
                'priority_3': 'Quality'
            }
        
        # Get knowledge context using semantic search
        knowledge_context = _get_relevant_knowledge(
            db, request.client_id, request.engagement_id, 
            stakeholder_info, request.sections
        )
        
        # Generate content using AI service
        content_sections = ai_service.generate_deliverable_content(
            client_info={
                'name': client.name,
                'industry': client.industry,
                'description': client.description
            },
            stakeholder_info=stakeholder_info,
            knowledge_context=knowledge_context,
            deliverable_type=request.deliverable_type,
            sections=request.sections
        )
        
        # Create deliverable record
        ai_content = "\n\n".join([f"{section}: {content}" for section, content in content_sections.items()])
        
        db_deliverable = Deliverable(
            client_id=request.client_id,
            engagement_id=request.engagement_id,
            title=request.title,
            deliverable_type=request.deliverable_type,
            status="draft",
            ai_generated_content=ai_content
        )
        db.add(db_deliverable)
        db.commit()
        db.refresh(db_deliverable)
        
        # Generate MS Word document
        file_path = document_generator.create_deliverable(
            client_name=client.name,
            deliverable_type=request.deliverable_type,
            content_sections=content_sections,
            stakeholder_name=stakeholder_info.get('name')
        )
        
        # Update deliverable with file path
        db_deliverable.file_path = file_path
        db.commit()
        db.refresh(db_deliverable)
        
        return db_deliverable
        
    except Exception as e:
        logger.error(f"Failed to generate deliverable: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate deliverable: {str(e)}")

@router.post("/", response_model=DeliverableSchema)
def create_deliverable(deliverable: DeliverableCreate, db: Session = Depends(get_db)):
    """Create a new deliverable manually"""
    db_deliverable = Deliverable(**deliverable.dict())
    db.add(db_deliverable)
    db.commit()
    db.refresh(db_deliverable)
    return db_deliverable

@router.put("/{deliverable_id}", response_model=DeliverableSchema)
def update_deliverable(deliverable_id: int, deliverable: DeliverableUpdate, db: Session = Depends(get_db)):
    """Update a deliverable"""
    db_deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    if db_deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    update_data = deliverable.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_deliverable, field, value)
    
    db.commit()
    db.refresh(db_deliverable)
    return db_deliverable

@router.post("/{deliverable_id}/approve", response_model=DeliverableSchema)
def approve_deliverable(deliverable_id: int, final_content: str, db: Session = Depends(get_db)):
    """Approve a deliverable and save final content for enrichment"""
    from datetime import datetime
    
    db_deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    if db_deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    # Update deliverable status and final content
    db_deliverable.status = "approved"
    db_deliverable.final_content = final_content
    db_deliverable.approved_at = datetime.now()
    
    # Save approved content as knowledge entry for enrichment
    approved_entry = KnowledgeEntry(
        client_id=db_deliverable.client_id,
        engagement_id=db_deliverable.engagement_id,
        entry_type="document",
        title=f"Approved {db_deliverable.deliverable_type}: {db_deliverable.title}",
        content=final_content,
        source_url=f"deliverable_id:{deliverable_id}"
    )
    db.add(approved_entry)
    db.commit()
    db.refresh(approved_entry)
    
    # Generate embedding for the approved content
    try:
        embedding_vector = embedding_service.generate_embedding(final_content)
        db_embedding = KnowledgeEmbedding(
            knowledge_entry_id=approved_entry.id,
            embedding=embedding_vector
        )
        db.add(db_embedding)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to generate embedding for approved deliverable: {e}")
    
    db.commit()
    db.refresh(db_deliverable)
    return db_deliverable

@router.delete("/{deliverable_id}")
def delete_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    """Delete a deliverable"""
    db_deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    if db_deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    # Delete associated file if it exists
    if db_deliverable.file_path and os.path.exists(db_deliverable.file_path):
        try:
            os.remove(db_deliverable.file_path)
        except Exception as e:
            logger.error(f"Failed to delete file {db_deliverable.file_path}: {e}")
    
    db.delete(db_deliverable)
    db.commit()
    return {"message": "Deliverable deleted successfully"}

def _get_relevant_knowledge(
    db: Session, 
    client_id: int, 
    engagement_id: int = None, 
    stakeholder_info: Dict[str, Any] = None,
    sections: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Get relevant knowledge context using semantic search
    """
    # Get all knowledge entries for the client
    query = db.query(KnowledgeEntry).filter(KnowledgeEntry.client_id == client_id)
    
    if engagement_id:
        query = query.filter(KnowledgeEntry.engagement_id == engagement_id)
    
    entries = query.all()
    
    if not entries:
        return []
    
    # If we have stakeholder priorities, use them for semantic search
    if stakeholder_info and stakeholder_info.get('priority_1'):
        priority_text = f"{stakeholder_info.get('priority_1', '')} {stakeholder_info.get('priority_2', '')} {stakeholder_info.get('priority_3', '')}"
        
        # Generate embedding for priority text
        try:
            priority_embedding = embedding_service.generate_embedding(priority_text)
            
            # Find entries with embeddings and calculate similarity
            relevant_entries = []
            for entry in entries:
                embedding = db.query(KnowledgeEmbedding).filter(KnowledgeEmbedding.knowledge_entry_id == entry.id).first()
                if embedding:
                    similarity = embedding_service.cosine_similarity(priority_embedding, embedding.embedding)
                    if similarity > 0.3:  # Threshold for relevance
                        relevant_entries.append({
                            'id': entry.id,
                            'title': entry.title,
                            'content': entry.content,
                            'entry_type': entry.entry_type,
                            'meeting_date': entry.meeting_date,
                            'similarity': similarity
                        })
            
            # Sort by similarity and return top 5
            relevant_entries.sort(key=lambda x: x['similarity'], reverse=True)
            return relevant_entries[:5]
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
    
    # Fallback: return recent entries
    recent_entries = []
    for entry in entries[-5:]:  # Last 5 entries
        recent_entries.append({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'entry_type': entry.entry_type,
            'meeting_date': entry.meeting_date,
            'similarity': 0.0
        })
    
    return recent_entries