"""
User model for future auth. Enable when implementing JWT auth.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

# Uncomment and add to models/db.py init_db when ready:
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)
