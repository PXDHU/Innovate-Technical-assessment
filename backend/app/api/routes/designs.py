"""
Designs API routes.
CRUD operations for cable designs.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.schemas import DesignCreate, DesignUpdate, DesignResponse
from app.models import Design
from typing import List

router = APIRouter(prefix="/api/designs", tags=["designs"])


@router.post("/", response_model=DesignResponse, status_code=201)
async def create_design(
    design: DesignCreate,
    db: Session = Depends(get_database)
):
    """Create a new cable design."""
    # Check if design ID already exists
    existing = db.query(Design).filter(Design.id == design.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Design ID already exists")
    
    db_design = Design(**design.model_dump())
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    
    return db_design


@router.get("/", response_model=List[DesignResponse])
async def list_designs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database)
):
    """List all cable designs."""
    designs = db.query(Design).offset(skip).limit(limit).all()
    return designs


@router.get("/{design_id}", response_model=DesignResponse)
async def get_design(
    design_id: str,
    db: Session = Depends(get_database)
):
    """Get a specific cable design by ID."""
    design = db.query(Design).filter(Design.id == design_id).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return design


@router.put("/{design_id}", response_model=DesignResponse)
async def update_design(
    design_id: str,
    design_update: DesignUpdate,
    db: Session = Depends(get_database)
):
    """Update a cable design."""
    design = db.query(Design).filter(Design.id == design_id).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    # Update fields
    update_data = design_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(design, field, value)
    
    db.commit()
    db.refresh(design)
    
    return design


@router.delete("/{design_id}", status_code=204)
async def delete_design(
    design_id: str,
    db: Session = Depends(get_database)
):
    """Delete a cable design."""
    design = db.query(Design).filter(Design.id == design_id).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    db.delete(design)
    db.commit()
    
    return None
