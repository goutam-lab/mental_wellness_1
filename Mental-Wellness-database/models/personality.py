# backend/models/personality.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Personality(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    personality_type: str
    introversion_score: int = 0
    extraversion_score: int = 0
    intuition_score: int = 0
    sensing_score: int = 0
    thinking_score: int = 0
    feeling_score: int = 0
    judging_score: int = 0
    perceiving_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True # Replaces 'allow_population_by_field_name'