"""SQLAlchemy database configuration and models."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Text, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


class User(Base):
    """Stores user accounts for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResumeReview(Base):
    """Stores resume review (strengths, weaknesses, suggestions)."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True) # Nullable for backward compatibility
    filename = Column(String)
    analysis = Column(JSON)  # { strengths, weaknesses, suggestions }
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Structured resume data for matching (Phase 2)
    parsed_resume = Column(JSON)  # { skills, education, experience }
    raw_text = Column(Text)  # Original extracted text


class JobMatch(Base):
    """Stores resume + job description match results."""

    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True) # Nullable for backward compatibility
    review_id = Column(Integer)  # FK to reviews.id (optional, for linked history)
    filename = Column(String)
    job_description = Column(Text)
    match_score = Column(Float)  # 0-100
    skill_gaps = Column(JSON)  # List of missing skills
    improvement_suggestions = Column(JSON)  # List of suggestions
    parsed_resume = Column(JSON)  # Snapshot for display
    timestamp = Column(DateTime, default=datetime.utcnow)
