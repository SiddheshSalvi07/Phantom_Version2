"""Lightweight DB models and helpers. Used for logging worker activity.

Note: minimal SQLAlchemy setup; in production expand migrations and session management.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()


class TaskLog(Base):
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True)
    task_id = Column(String(128), index=True)
    status = Column(String(50))
    payload = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
