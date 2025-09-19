# backend/services/community_service.py
from models.post import Post
from utils.db import get_db
from bson.objectid import ObjectId
from datetime import datetime
import os

def get_posts_collection():
    """Get the posts collection from MongoDB"""
    db = get_db()
    return db.posts

def create_post(user_id, content, media_url=None, socketio=None):
    post = Post(user_id, content, media_url)
    post_dict = post.to_dict()
    # Ensure user_id is an ObjectId for aggregation
    post_dict['user_id'] = ObjectId(user_id)

    posts_collection = get_posts_collection()
    result = posts_collection.insert_one(post_dict)
    
    # Fetch the newly created post with populated user info to broadcast
    pipeline = [
        {"$match": {"_id": result.inserted_id}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_details"
        }},
        {"$unwind": "$user_details"},
        {"$addFields": {
            "user": {
                "_id": "$user_details._id",
                "username": "$user_details.username",
                "full_name": "$user_details.full_name",
                "avatar": "$user_details.avatar"
            }
        }},
        {"$project": { "user_details": 0, "user.password_hash": 0 }}
    ]
    new_post_agg = list(posts_collection.aggregate(pipeline))
    
    if new_post_agg:
        new_post = new_post_agg[0]
        # Convert ObjectIds to strings for JSON serialization
        new_post['_id'] = str(new_post['_id'])
        new_post['user_id'] = str(new_post['user_id'])
        new_post['user']['_id'] = str(new_post['user']['_id'])

        if socketio:
            socketio.emit('new_post', new_post)
        
        return new_post
    return None

def get_all_posts():
    posts_collection = get_posts_collection()
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_details"
        }},
        {"$unwind": "$user_details"},
        {"$addFields": {
            "user": {
                "_id": "$user_details._id",
                "username": "$user_details.username",
                "full_name": "$user_details.full_name",
                "avatar": "$user_details.avatar"
            }
        }},
        {"$project": { "user_details": 0, "user.password_hash": 0 }}
    ]
    posts = list(posts_collection.aggregate(pipeline))
    for post in posts:
        post['_id'] = str(post['_id'])
        post['user_id'] = str(post['user_id'])
        post['user']['_id'] = str(post['user']['_id'])
    return posts

def like_post(post_id, socketio=None):
    posts_collection = get_posts_collection()
    oid = ObjectId(post_id)
    
    result = posts_collection.update_one({"_id": oid}, {"$inc": {"likes": 1}})
    
    if result.modified_count > 0:
        updated_post = posts_collection.find_one({"_id": oid})
        if updated_post and socketio:
            socketio.emit('post_update', {
                "post_id": post_id, 
                "likes": updated_post.get('likes', 0)
            })
        return get_post(post_id) # Return full post
    return None

def add_comment(post_id, text, user_id, socketio=None):
    posts_collection = get_posts_collection()
    oid = ObjectId(post_id)
    
    comment = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id), 
        "text": text,
        "created_at": datetime.utcnow()
    }
    
    result = posts_collection.update_one({"_id": oid}, {"$push": {"comments": comment}})
    
    if result.modified_count > 0:
        # Fetch comment with user info
        user_info = get_db().users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
        if user_info:
            comment['user'] = {
                "_id": str(user_info["_id"]),
                "username": user_info.get("username"),
                "full_name": user_info.get("full_name"),
                "avatar": user_info.get("avatar")
            }
        comment['_id'] = str(comment['_id'])
        comment['user_id'] = str(comment['user_id'])

        if socketio:
            socketio.emit('comment_update', {"post_id": post_id, "comment": comment})
        
        return get_post(post_id) # Return full post
    return None

def get_post(post_id):
    # ... (keep existing get_post function, but add user population)
    pass

def delete_post(post_id: str, user_id: str, socketio=None):
    posts_collection = get_posts_collection()
    oid = ObjectId(post_id)
    
    post_to_delete = posts_collection.find_one({"_id": oid, "user_id": ObjectId(user_id)})
    
    if not post_to_delete:
        return False

    result = posts_collection.delete_one({"_id": oid})
    
    if result.deleted_count > 0:
        if post_to_delete.get("media_url"):
            try:
                UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
                filename = os.path.basename(post_to_delete["media_url"])
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file for post {post_id}: {e}")

        if socketio:
            socketio.emit('post_deleted', {'post_id': post_id})
        return True
    return False