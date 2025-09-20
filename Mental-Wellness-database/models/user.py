# backend/models/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str
    email: EmailStr
    password_hash: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    personality_id: Optional[str] = None
    friends: List[str] = []
    sent_friend_requests: List[str] = []
    received_friend_requests: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 👇 New fields for the streak feature
    streak: int = 0
    last_task_completion_date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True