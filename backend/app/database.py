from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.config import settings

from pathlib import Path

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if db_url.startswith("sqlite:///./"):
        rel_path = db_url.replace("sqlite:///./", "")
        backend_dir = Path(__file__).resolve().parent.parent
        candidate = backend_dir / rel_path
        if candidate.exists():
            db_url = f"sqlite:///{candidate.as_posix()}"

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=(settings.ENVIRONMENT == "development_debug"),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 ORM models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
