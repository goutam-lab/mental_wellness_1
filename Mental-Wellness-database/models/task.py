from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import json

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str = "pending"  # pending | completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "60d5ec49f7b4e2a5a8c1d3b4",
                "title": "Complete API documentation",
                "description": "Write comprehensive docs for the Task API",
                "category": "development",
                "status": "pending",
                "created_at": "2023-12-01T10:00:00Z",
                "due_date": "2023-12-15T23:59:59Z"
            }
        }

    def to_dict(self):
        """Convert Task instance to dictionary with proper date handling"""
        data = self.model_dump()
        
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        
        if isinstance(data.get('due_date'), datetime):
            data['due_date'] = data['due_date'].isoformat()
            
        return data

    def to_json(self):
        """Convert Task instance to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict):
        """Create Task instance from dictionary with date parsing"""
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        if data.get('due_date') and isinstance(data['due_date'], str):
            data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            
        return cls(**data)
