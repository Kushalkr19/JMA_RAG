from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.stakeholder import Stakeholder
from app.schemas.stakeholder import StakeholderCreate, StakeholderUpdate, Stakeholder as StakeholderSchema

router = APIRouter()

@router.get("/", response_model=List[StakeholderSchema])
def get_stakeholders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stakeholders"""
    stakeholders = db.query(Stakeholder).offset(skip).limit(limit).all()
    return stakeholders

@router.get("/client/{client_id}", response_model=List[StakeholderSchema])
def get_stakeholders_by_client(client_id: int, db: Session = Depends(get_db)):
    """Get all stakeholders for a specific client"""
    stakeholders = db.query(Stakeholder).filter(Stakeholder.client_id == client_id).all()
    return stakeholders

@router.get("/{stakeholder_id}", response_model=StakeholderSchema)
def get_stakeholder(stakeholder_id: int, db: Session = Depends(get_db)):
    """Get a specific stakeholder"""
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if stakeholder is None:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    return stakeholder

@router.post("/", response_model=StakeholderSchema)
def create_stakeholder(stakeholder: StakeholderCreate, db: Session = Depends(get_db)):
    """Create a new stakeholder"""
    db_stakeholder = Stakeholder(**stakeholder.dict())
    db.add(db_stakeholder)
    db.commit()
    db.refresh(db_stakeholder)
    return db_stakeholder

@router.put("/{stakeholder_id}", response_model=StakeholderSchema)
def update_stakeholder(stakeholder_id: int, stakeholder: StakeholderUpdate, db: Session = Depends(get_db)):
    """Update a stakeholder"""
    db_stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if db_stakeholder is None:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    update_data = stakeholder.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stakeholder, field, value)
    
    db.commit()
    db.refresh(db_stakeholder)
    return db_stakeholder

@router.delete("/{stakeholder_id}")
def delete_stakeholder(stakeholder_id: int, db: Session = Depends(get_db)):
    """Delete a stakeholder"""
    db_stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if db_stakeholder is None:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    db.delete(db_stakeholder)
    db.commit()
    return {"message": "Stakeholder deleted successfully"}