"""API routes package."""
from app.api.routes.validation import router as validation_router
from app.api.routes.designs import router as designs_router

__all__ = ["validation_router", "designs_router"]
