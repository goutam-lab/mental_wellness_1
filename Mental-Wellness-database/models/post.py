# backend/models/post.py
from datetime import datetime
import uuid

class Post:
    def __init__(self, user_id, content, media_url=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.content = content
        self.media_url = media_url
        self.likes = []  # Changed from number to a list of user IDs
        self.comments = []
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "media_url": self.media_url,
            "likes": self.likes,
            "comments": self.comments,
            "created_at": self.created_at.isoformat()
        }