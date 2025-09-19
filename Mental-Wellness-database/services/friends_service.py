# backend/services/friends_service.py
from utils.db import get_db
from bson.objectid import ObjectId

def get_users_collection():
    db = get_db()
    return db.users

def search_users(query, current_user_id):
    users_collection = get_users_collection()
    query_filter = {
        "username": {"$regex": query, "$options": "i"},
        "_id": {"$ne": ObjectId(current_user_id)}
    }
    users = list(users_collection.find(query_filter, {"password_hash": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
    return users

def send_friend_request(from_user_id, to_user_id):
    users_collection = get_users_collection()
    from_user_oid = ObjectId(from_user_id)
    to_user_oid = ObjectId(to_user_id)

    user_to = users_collection.find_one({"_id": to_user_oid})
    if from_user_oid in user_to.get("friends", []) or from_user_oid in user_to.get("received_friend_requests", []):
        return False

    users_collection.update_one({"_id": from_user_oid}, {"$addToSet": {"sent_friend_requests": to_user_oid}})
    users_collection.update_one({"_id": to_user_oid}, {"$addToSet": {"received_friend_requests": from_user_oid}})
    return True

def respond_to_friend_request(recipient_id, sender_id, action):
    users_collection = get_users_collection()
    recipient_oid = ObjectId(recipient_id)
    sender_oid = ObjectId(sender_id)

    users_collection.update_one(
        {"_id": recipient_oid},
        {"$pull": {"received_friend_requests": sender_oid}}
    )
    users_collection.update_one(
        {"_id": sender_oid},
        {"$pull": {"sent_friend_requests": recipient_oid}}
    )

    if action == "accept":
        users_collection.update_one(
            {"_id": recipient_oid},
            {"$addToSet": {"friends": sender_oid}}
        )
        users_collection.update_one(
            {"_id": sender_oid},
            {"$addToSet": {"friends": recipient_oid}}
        )
    
    return True

def get_friends(user_id):
    users_collection = get_users_collection()
    user_oid = ObjectId(user_id)
    user = users_collection.find_one({"_id": user_oid}, {"friends": 1})
    if user and "friends" in user:
        friend_ids = user["friends"]
        friends = list(users_collection.find({"_id": {"$in": friend_ids}}, {"password_hash": 0}))
        for friend in friends:
            friend["_id"] = str(friend["_id"])
        return friends
    return []

def get_friend_requests(user_id):
    users_collection = get_users_collection()
    user_oid = ObjectId(user_id)
    user = users_collection.find_one({"_id": user_oid}, {"received_friend_requests": 1})
    if user and "received_friend_requests" in user:
        request_ids = user["received_friend_requests"]
        requests = list(users_collection.find({"_id": {"$in": request_ids}}, {"password_hash": 0}))
        for req in requests:
            req["_id"] = str(req["_id"])
        return requests
    return []