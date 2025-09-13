# backend/models/chat.py

from datetime import datetime
from bson import ObjectId
from typing import Optional, List

class Chat:
    def __init__(self, user_id, user_message, bot_response, timestamp=None, 
                 pinecone_id: Optional[str] = None, embedding: Optional[List[float]] = None):
        """
        Initialize Chat object - ALIGNED with chat_service.py
        
        Args:
            user_id: User's ObjectId or string ID
            user_message: User's input message (was 'message' - FIXED)
            bot_response: Chatbot's response (was 'response' - FIXED)
            timestamp: Optional timestamp
            pinecone_id: Optional Pinecone vector ID for RAG
            embedding: Optional embedding vector for RAG
        """
        # Handle user_id conversion
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        
        # FIXED: Use correct field names that match chat_service.py
        self.user_message = user_message  # Changed from 'message'
        self.bot_response = bot_response  # Changed from 'response'
        
        self.timestamp = timestamp or datetime.utcnow()
        
        # NEW: RAG-specific fields
        self.pinecone_id = pinecone_id
        self.embedding = embedding

    def to_dict(self):
        """
        Convert Chat object to dictionary for MongoDB insertion
        ALIGNED with chat_service.py expectations
        """
        chat_dict = {
            "user_id": self.user_id,
            "user_message": self.user_message,  # FIXED: Correct field name
            "bot_response": self.bot_response,  # FIXED: Correct field name
            "timestamp": self.timestamp
        }
        
        # Add RAG fields only if they exist
        if self.pinecone_id:
            chat_dict["pineconeId"] = self.pinecone_id
        if self.embedding:
            chat_dict["embedding"] = self.embedding
            
        return chat_dict
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        Create Chat object from MongoDB document
        """
        return cls(
            user_id=data.get('user_id'),
            user_message=data.get('user_message', ''),
            bot_response=data.get('bot_response', ''),
            timestamp=data.get('timestamp'),
            pinecone_id=data.get('pineconeId'),
            embedding=data.get('embedding')
        )
    
    def __str__(self):
        return f"Chat(user_id={self.user_id}, user_message='{self.user_message[:50]}...', timestamp={self.timestamp})"
    
    def __repr__(self):
        return self.__str__()