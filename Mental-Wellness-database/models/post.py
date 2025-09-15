from datetime import datetime
import uuid

class Post:
    def __init__(self, user_id, content, media_url=None):
        self.id = str(uuid.uuid4())  # unique post ID
        self.user_id = user_id       # who made the post
        self.content = content       # text of the post
        self.media_url = media_url   # optional image/video
        self.likes = 0               # like counter
        self.comments = []           # list of comments
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