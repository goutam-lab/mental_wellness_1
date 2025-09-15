from models.post import Post
from utils.db import get_db

def get_posts_collection():
    """Get the posts collection from MongoDB"""
    db = get_db()
    return db.posts

def create_post(user_id, content, media_url=None):
    try:
        post = Post(user_id, content, media_url)
        post_dict = post.to_dict()

        # Insert into MongoDB
        posts_collection = get_posts_collection()
        result = posts_collection.insert_one(post_dict)
        post_dict['_id'] = str(result.inserted_id)

        return post_dict
    except Exception as e:
        # Fallback to in-memory
        from services.community_service_fallback import create_post_fallback
        return create_post_fallback(user_id, content, media_url)

def get_all_posts():
    try:
        posts_collection = get_posts_collection()
        posts = list(posts_collection.find().sort("created_at", -1))  # Newest first

        # Convert ObjectId to string for JSON serialization
        for post in posts:
            post['_id'] = str(post['_id'])

        return posts
    except Exception as e:
        # Fallback to in-memory
        from services.community_service_fallback import get_all_posts_fallback
        return get_all_posts_fallback()

from bson.objectid import ObjectId

def get_post(post_id):
    try:
        posts_collection = get_posts_collection()
        try:
            oid = ObjectId(post_id)
        except Exception:
            return None
        post = posts_collection.find_one({"_id": oid})
        if post:
            post['_id'] = str(post['_id'])
        return post
    except Exception as e:
        # Fallback to in-memory
        from services.community_service_fallback import get_post_fallback
        return get_post_fallback(post_id)

def like_post(post_id):
    try:
        posts_collection = get_posts_collection()
        try:
            oid = ObjectId(post_id)
        except Exception:
            return None
        result = posts_collection.update_one(
            {"_id": oid},
            {"$inc": {"likes": 1}}
        )
        if result.modified_count == 0:
            return None
        post = posts_collection.find_one({"_id": oid})
        if post:
            post['_id'] = str(post['_id'])
        return post
    except Exception as e:
        # Fallback to in-memory
        from services.community_service_fallback import like_post_fallback
        return like_post_fallback(post_id)

def add_comment(post_id, comment_text, commenter_id):
    try:
        posts_collection = get_posts_collection()
        try:
            oid = ObjectId(post_id)
        except Exception:
            return None
        comment = {
            "user_id": commenter_id,
            "text": comment_text
        }
        result = posts_collection.update_one(
            {"_id": oid},
            {"$push": {"comments": comment}}
        )
        if result.modified_count == 0:
            return None
        post = posts_collection.find_one({"_id": oid})
        if post:
            post['_id'] = str(post['_id'])
        return post
    except Exception as e:
        # Fallback to in-memory
        from services.community_service_fallback import add_comment_fallback
        return add_comment_fallback(post_id, comment_text, commenter_id)