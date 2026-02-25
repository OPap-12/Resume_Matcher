# Backwards compatibility - use models.db
from models.db import SessionLocal, init_db, ResumeReview, get_db

__all__ = ["SessionLocal", "init_db", "ResumeReview", "get_db"]
