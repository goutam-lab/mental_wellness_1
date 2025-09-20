from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
# Remove the User model import from here, we will create a dict directly
from utils.db import get_db
from bson import ObjectId
import re
from datetime import datetime # Import datetime

auth_bp = Blueprint("auth", __name__)
db = get_db()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    if db.users.find_one({"email": data["email"]}):
        return jsonify({"error": "A user with this email already exists"}), 409

    hashed_password = generate_password_hash(data["password"], method='pbkdf2:sha256')
    
    # Create a dictionary for the new user instead of using the Pydantic model here
    new_user_data = {
        "username": data.get("email").split("@")[0],
        "email": data["email"],
        "password_hash": hashed_password,
        "full_name": f"{data.get('firstname', '')} {data.get('lastname', '')}".strip(),
        # Add default values for other fields
        "friends": [],
        "sent_friend_requests": [],
        "received_friend_requests": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.users.insert_one(new_user_data)

    return jsonify({
        "message": "User created successfully",
        "userId": str(result.inserted_id) # This is now a proper ObjectId
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = db.users.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "userId": str(user["_id"])
    }), 200

@auth_bp.route("/user/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    """Fetch a single user's profile by their ID."""
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
        if user:
            user["_id"] = str(user["_id"])
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/users/search", methods=["GET"])
def search_users():
    """Search for users by username or full_name"""
    query = request.args.get("q", "")
    if not query or len(query) < 2:
        return jsonify({"users": []})

    regex = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)
    
    users_cursor = db.users.find({
        "$or": [
            {"username": {"$regex": regex}},
            {"full_name": {"$regex": regex}}
        ]
    }).limit(10)

    users = []
    for user in users_cursor:
        users.append({
            "_id": str(user["_id"]),
            "username": user.get("username"),
            "full_name": user.get("full_name", ""),
            "avatar": user.get("avatar", "/placeholder-user.jpg")
        })
        
    return jsonify({"users": users})

