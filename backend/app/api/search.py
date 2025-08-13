from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.models.knowledge_entry import KnowledgeEntry
from app.models.knowledge_embedding import KnowledgeEmbedding
from app.utils.embeddings import embedding_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/semantic")
def semantic_search(
    query: str = Query(..., description="Search query"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    limit: int = Query(5, description="Number of results to return"),
    threshold: float = Query(0.3, description="Similarity threshold"),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search on knowledge entries
    """
    try:
        # Generate embedding for the query
        query_embedding = embedding_service.generate_embedding(query)
        
        # Build query
        db_query = db.query(KnowledgeEntry, KnowledgeEmbedding)
        
        # Join with embeddings
        db_query = db_query.join(KnowledgeEmbedding, KnowledgeEntry.id == KnowledgeEmbedding.knowledge_entry_id)
        
        # Filter by client if specified
        if client_id:
            db_query = db_query.filter(KnowledgeEntry.client_id == client_id)
        
        # Get all entries with embeddings
        results = db_query.all()
        
        # Calculate similarities
        search_results = []
        for entry, embedding in results:
            similarity = embedding_service.cosine_similarity(query_embedding, embedding.embedding)
            
            if similarity >= threshold:
                search_results.append({
                    'id': entry.id,
                    'title': entry.title,
                    'content': entry.content[:500] + "..." if len(entry.content) > 500 else entry.content,
                    'entry_type': entry.entry_type,
                    'meeting_date': entry.meeting_date,
                    'client_id': entry.client_id,
                    'similarity': round(similarity, 4)
                })
        
        # Sort by similarity and limit results
        search_results.sort(key=lambda x: x['similarity'], reverse=True)
        search_results = search_results[:limit]
        
        return {
            'query': query,
            'results': search_results,
            'total_found': len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/by-stakeholder-priority")
def search_by_stakeholder_priority(
    stakeholder_id: int = Query(..., description="Stakeholder ID"),
    limit: int = Query(5, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Search knowledge entries based on stakeholder priorities
    """
    try:
        from app.models.stakeholder import Stakeholder
        
        # Get stakeholder information
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
        if stakeholder is None:
            raise HTTPException(status_code=404, detail="Stakeholder not found")
        
        # Build priority text
        priority_text = f"{stakeholder.priority_1 or ''} {stakeholder.priority_2 or ''} {stakeholder.priority_3 or ''}".strip()
        
        if not priority_text:
            raise HTTPException(status_code=400, detail="Stakeholder has no priorities defined")
        
        # Generate embedding for priorities
        priority_embedding = embedding_service.generate_embedding(priority_text)
        
        # Get knowledge entries for the stakeholder's client
        db_query = db.query(KnowledgeEntry, KnowledgeEmbedding)
        db_query = db_query.join(KnowledgeEmbedding, KnowledgeEntry.id == KnowledgeEmbedding.knowledge_entry_id)
        db_query = db_query.filter(KnowledgeEntry.client_id == stakeholder.client_id)
        
        results = db_query.all()
        
        # Calculate similarities
        search_results = []
        for entry, embedding in results:
            similarity = embedding_service.cosine_similarity(priority_embedding, embedding.embedding)
            
            if similarity > 0.2:  # Lower threshold for priority-based search
                search_results.append({
                    'id': entry.id,
                    'title': entry.title,
                    'content': entry.content[:500] + "..." if len(entry.content) > 500 else entry.content,
                    'entry_type': entry.entry_type,
                    'meeting_date': entry.meeting_date,
                    'similarity': round(similarity, 4),
                    'stakeholder_priority': priority_text
                })
        
        # Sort by similarity and limit results
        search_results.sort(key=lambda x: x['similarity'], reverse=True)
        search_results = search_results[:limit]
        
        return {
            'stakeholder_name': stakeholder.name,
            'stakeholder_priorities': priority_text,
            'results': search_results,
            'total_found': len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Stakeholder priority search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/hybrid")
def hybrid_search(
    query: str = Query(..., description="Search query"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    stakeholder_id: Optional[int] = Query(None, description="Filter by stakeholder ID"),
    limit: int = Query(5, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Perform hybrid search combining semantic and stakeholder priority matching
    """
    try:
        # Get semantic search results
        semantic_results = semantic_search(query, client_id, limit, 0.2, db)
        
        # Get stakeholder priority results if stakeholder specified
        priority_results = []
        if stakeholder_id:
            try:
                priority_response = search_by_stakeholder_priority(stakeholder_id, limit, db)
                priority_results = priority_response['results']
            except Exception as e:
                logger.warning(f"Failed to get priority results: {e}")
        
        # Combine and deduplicate results
        combined_results = {}
        
        # Add semantic results
        for result in semantic_results['results']:
            combined_results[result['id']] = {
                **result,
                'semantic_score': result['similarity'],
                'priority_score': 0.0
            }
        
        # Add priority results
        for result in priority_results:
            if result['id'] in combined_results:
                combined_results[result['id']]['priority_score'] = result['similarity']
            else:
                combined_results[result['id']] = {
                    **result,
                    'semantic_score': 0.0,
                    'priority_score': result['similarity']
                }
        
        # Calculate combined score (weighted average)
        for result in combined_results.values():
            result['combined_score'] = round(
                (result['semantic_score'] * 0.7) + (result['priority_score'] * 0.3), 4
            )
        
        # Sort by combined score
        final_results = list(combined_results.values())
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        final_results = final_results[:limit]
        
        return {
            'query': query,
            'stakeholder_id': stakeholder_id,
            'results': final_results,
            'total_found': len(final_results)
        }
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")