# backend/models/post.py
from datetime import datetime
import uuid

class Post:
    def __init__(self, user_id, content, media_url=None, id=None, created_at=None, likes=0, comments=[]):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.content = content
        self.media_url = media_url
        self.likes = likes
        self.comments = comments
        self.created_at = created_at or datetime.utcnow()

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

    @staticmethod
    def from_dict(data):
        return Post(
            id=data.get('id'),
            user_id=data.get('user_id'),
            content=data.get('content'),
            media_url=data.get('media_url'),
            likes=data.get('likes', 0),
            comments=data.get('comments', []),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at')
        )