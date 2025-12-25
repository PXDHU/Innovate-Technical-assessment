"""
Design model representing cable design specifications.
"""
from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.database import Base


class Design(Base):
    """Cable design model matching the DESIGN_DATABASE from notebook."""
    
    __tablename__ = "designs"
    
    id = Column(String(50), primary_key=True)  # e.g., "DESIGN-001"
    standard = Column(String(100), nullable=True)
    voltage = Column(String(50), nullable=True)
    conductor_material = Column(String(20), nullable=True)
    conductor_class = Column(String(20), nullable=True)
    csa = Column(Float, nullable=True)
    insulation_material = Column(String(50), nullable=True)
    insulation_thickness = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary matching notebook format."""
        return {
            "standard": self.standard,
            "voltage": self.voltage,
            "conductor_material": self.conductor_material,
            "conductor_class": self.conductor_class,
            "csa": self.csa,
            "insulation_material": self.insulation_material,
            "insulation_thickness": self.insulation_thickness
        }
