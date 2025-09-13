from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.db import get_db
from bson import ObjectId

auth_bp = Blueprint("auth", __name__)
db = get_db()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    # Check if user already exists
    if db.users.find_one({"email": data["email"]}):
        return jsonify({"error": "A user with this email already exists"}), 409

    hashed_password = generate_password_hash(data["password"], method='pbkdf2:sha256')

    new_user = User(
        username=data.get("email").split("@")[0], # or use a dedicated username field
        email=data["email"],
        password_hash=hashed_password,
        full_name=f"{data.get('firstname', '')} {data.get('lastname', '')}".strip()
    )
    
    # Pydantic's .dict() is now .model_dump()
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