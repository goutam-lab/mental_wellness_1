# services/community_service_fallback.py
from models.post import Post

# In-memory "database" for fallback
posts_db = {}

def create_post_fallback(user_id, content, media_url=None):
    post = Post(user_id, content, media_url)
    posts_db[post.id] = post
    return post.to_dict()

def get_all_posts_fallback():
    return [post.to_dict() for post in posts_db.values()]

def get_post_fallback(post_id):
    post = posts_db.get(post_id)
    return post.to_dict() if post else None

def like_post_fallback(post_id):
    post = posts_db.get(post_id)
    if post:
        post.likes += 1
        return post.to_dict()
    return None

def add_comment_fallback(post_id, comment_text, commenter_id):
    post = posts_db.get(post_id)
    if post:
        post.comments.append({"user_id": commenter_id, "text": comment_text})
        return post.to_dict()
    return None