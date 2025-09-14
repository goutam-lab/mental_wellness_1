# backend/models/chat.py
from datetime import datetime
from bson import ObjectId
from typing import Optional, List

class Chat:
    def __init__(self, user_id, user_message, bot_response, conversation_id, timestamp=None, 
                 pinecone_id: Optional[str] = None, embedding: Optional[List[float]] = None):
        """
        Initialize Chat object
        """
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.user_message = user_message
        self.bot_response = bot_response
        self.conversation_id = conversation_id # New field
        self.timestamp = timestamp or datetime.utcnow()
        self.pinecone_id = pinecone_id
        self.embedding = embedding

    def to_dict(self):
        """
        Convert Chat object to dictionary for MongoDB insertion
        """
        chat_dict = {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id, # New field
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "timestamp": self.timestamp
        }
        
        if self.pinecone_id:
            chat_dict["pineconeId"] = self.pinecone_id
        if self.embedding:
            chat_dict["embedding"] = self.embedding
            
        return chat_dict