"""Common Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
