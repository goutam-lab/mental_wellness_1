# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.db import get_db
from bson import ObjectId
import re

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

    new_user = User(
        username=data.get("email").split("@")[0],
        email=data["email"],
        password_hash=hashed_password,
        full_name=f"{data.get('firstname', '')} {data.get('lastname', '')}".strip()
    )

    user_dict = new_user.model_dump(by_alias=True, exclude=["id"])
    result = db.users.insert_one(user_dict)

    return jsonify({
        "message": "User created successfully",
        "userId": str(result.inserted_id)
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

@auth_bp.route("/users/search", methods=["GET"])
def search_users():
    """Search for users by username or full_name"""
    query = request.args.get("q", "")
    if not query or len(query) < 2:
        return jsonify({"users": []})

    # Case-insensitive regex for broader matching
    regex = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)

    # Search in both username and full_name fields
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