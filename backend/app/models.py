"""Persistent DB models: User, Task, TaskLog.

TODO: Add migrations (Alembic) and indexing strategy; integrate vector embeddings later.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    task_uuid = Column(String(128), unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    status = Column(String(50), default="created")
    approved = Column(Integer, default=0)  # 0/1 bool
    plan = Column(Text)  # JSON serialized plan
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="tasks")


class TaskLog(Base):
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    status = Column(String(50))
    payload = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
    else:
        # Fallback for tests/dev if not provided
        engine = create_engine("sqlite:///./phantom_dev.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
