"""Pydantic schemas for backend API requests and responses."""
from pydantic import BaseModel
from typing import Optional


class GoalCreate(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
