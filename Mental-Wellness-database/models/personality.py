from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Personality(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str  # Reference to the User's ObjectId

    # MBTI result
    personality_type: str  # e.g. "INTP"

    # Optional raw scores for each dimension
    introversion_score: int = 0
    extraversion_score: int = 0
    intuition_score: int = 0
    sensing_score: int = 0
    thinking_score: int = 0
    feeling_score: int = 0
    judging_score: int = 0
    perceiving_score: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}