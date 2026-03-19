import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pipeline_db")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Test connections before using them
    echo=False,  # Set to True for SQL debug logging
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


def get_db_session():
    """Get a new database session."""
    return SessionLocal()


def create_all_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def close_db():
    """Close database connection."""
    engine.dispose()