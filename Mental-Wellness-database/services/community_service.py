# backend/services/community_service.py
from models.post import Post
from utils.db import get_db
from bson.objectid import ObjectId
from datetime import datetime

def get_posts_collection():
    """Get the posts collection from MongoDB"""
    db = get_db()
    return db.posts

def create_post(user_id, content, media_url=None, socketio=None):
    post = Post(user_id, content, media_url)
    post_dict = post.to_dict()
    post_dict['user_id'] = ObjectId(user_id) # Ensure user_id is ObjectId for aggregation

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
        # Convert ObjectIds to strings for JSON serialization before emitting
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
    # Convert ObjectIds to strings for JSON
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
            # Emit an event with the post ID and new like count
            socketio.emit('post_update', {
                "post_id": post_id,
                "likes": updated_post.get('likes', 0)
            })
        return get_post(post_id)
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
        # Fetch comment with user info to emit
        user_info = get_db().users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
        if user_info:
            comment['user'] = {
                "_id": str(user_info["_id"]),
                "username": user_info.get("username"),
                "full_name": user_info.get("full_name"),
                "avatar": user_info.get("avatar")
            }
        
        # Convert IDs to strings for emission
        comment['_id'] = str(comment['_id'])
        comment['user_id'] = str(comment['user_id'])

        if socketio:
            updated_post = posts_collection.find_one({"_id": oid})
            socketio.emit('post_update', {
                "post_id": post_id,
                "comments": [c for c in updated_post.get('comments', [])] # Send all comments
            })

        return get_post(post_id)
    return None

def get_post(post_id):
    """ Helper to get a single post with populated user data """
    posts_collection = get_posts_collection()
    pipeline = [
        {"$match": {"_id": ObjectId(post_id)}},
        # ... (aggregation pipeline similar to get_all_posts) ...
    ]
    post_agg = list(posts_collection.aggregate(pipeline))
    if post_agg:
        post = post_agg[0]
        # Convert all ObjectIds to strings
        # ...
        return post
    return None