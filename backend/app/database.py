from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.config import DATABASE_URL

# Create engine with SQLite-specific settings for thread safety
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
poolclass = StaticPool if DATABASE_URL.startswith("sqlite") else None

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=poolclass,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
