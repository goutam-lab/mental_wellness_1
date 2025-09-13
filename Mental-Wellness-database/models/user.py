from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    
    # Basic user info
    username: str
    email: EmailStr
    password_hash: str  # hashed password
    
    # Extra attributes
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    
    # Link to personality profile
    personality_id: Optional[str] = None  # Reference to Personality._id
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
