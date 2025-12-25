"""
Validation models for storing validation results and HITL interactions.
"""
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4
from app.database import Base


class Validation(Base):
    """Main validation record."""
    
    __tablename__ = "validations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_input = Column(Text, nullable=False)
    route = Column(String(50), nullable=True)
    design_id = Column(String(50), ForeignKey("designs.id"), nullable=True)
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    hitl_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    results = relationship("ValidationResult", back_populates="validation", cascade="all, delete-orphan")
    hitl_interactions = relationship("HITLInteraction", back_populates="validation", cascade="all, delete-orphan")


class ValidationResult(Base):
    """Individual field validation result."""
    
    __tablename__ = "validation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    validation_id = Column(UUID(as_uuid=True), ForeignKey("validations.id", ondelete="CASCADE"), nullable=False)
    field = Column(String(50), nullable=False)
    status = Column(String(10), nullable=False)  # PASS, WARN, FAIL
    expected = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Relationship
    validation = relationship("Validation", back_populates="results")


class HITLInteraction(Base):
    """Human-in-the-loop interaction log."""
    
    __tablename__ = "hitl_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    validation_id = Column(UUID(as_uuid=True), ForeignKey("validations.id", ondelete="CASCADE"), nullable=False)
    field = Column(String(50), nullable=False)
    user_response = Column(String(200), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    validation = relationship("Validation", back_populates="hitl_interactions")
