"""API dependencies."""
from app.database import get_db
from sqlalchemy.orm import Session
from typing import Generator


def get_database() -> Generator[Session, None, None]:
    """Get database session dependency."""
    yield from get_db()
