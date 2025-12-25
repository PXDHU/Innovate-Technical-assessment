"""Design schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.common import TimestampMixin


class DesignBase(BaseModel):
    """Base design schema."""
    standard: Optional[str] = None
    voltage: Optional[str] = None
    conductor_material: Optional[str] = None
    conductor_class: Optional[str] = None
    csa: Optional[float] = None
    insulation_material: Optional[str] = None
    insulation_thickness: Optional[float] = None


class DesignCreate(DesignBase):
    """Schema for creating a design."""
    id: str = Field(..., description="Design ID (e.g., DESIGN-001)")


class DesignUpdate(DesignBase):
    """Schema for updating a design."""
    pass


class DesignResponse(DesignBase, TimestampMixin):
    """Schema for design response."""
    id: str

    class Config:
        from_attributes = True
