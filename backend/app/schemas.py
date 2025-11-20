"""Pydantic schemas for backend API requests and responses.

Updated: user_id removed (derived from auth token).
"""
from pydantic import BaseModel
from typing import Optional


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
