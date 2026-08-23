from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.core.config import settings

# Create SQLAlchemy engine with pre-ping to handle stale MySQL connections
engine = create_engine(
    settings.database_url,
    connect_args={
        "ssl": {
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }
    },
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# Session factory for DB interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy ORM models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Automatically closes the session after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
