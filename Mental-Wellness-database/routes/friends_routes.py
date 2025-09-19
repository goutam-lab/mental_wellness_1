# backend/routes/friends_routes.py
from flask import Blueprint, request, jsonify
from services import friends_service

friends_bp = Blueprint("friends", __name__)

@friends_bp.route("/search", methods=["GET"])
def search_users():
    query = request.args.get("q", "")
    user_id = request.args.get("userId", "")
    if not query:
        return jsonify({"status": "error", "message": "Query parameter 'q' is required"}), 400
    try:
        users = friends_service.search_users(query, user_id)
        return jsonify({"status": "success", "users": users}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@friends_bp.route("/friend-request", methods=["POST"])
def send_friend_request():
    data = request.get_json()
    from_user_id = data.get("from_user_id")
    to_user_id = data.get("to_user_id")
    if not from_user_id or not to_user_id:
        return jsonify({"status": "error", "message": "Missing user IDs"}), 400
    try:
        if friends_service.send_friend_request(from_user_id, to_user_id):
            return jsonify({"status": "success", "message": "Friend request sent"}), 200
        else:
            return jsonify({"status": "error", "message": "Could not send friend request"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@friends_bp.route("/friend-request/respond", methods=["POST"])
def respond_to_friend_request():
    data = request.get_json()
    recipient_id = data.get("recipient_id") # The user who is responding
    sender_id = data.get("sender_id") # The user who sent the request
    action = data.get("action") # "accept" or "decline"

    if not all([recipient_id, sender_id, action]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    try:
        if friends_service.respond_to_friend_request(recipient_id, sender_id, action):
            return jsonify({"status": "success", "message": f"Friend request {action}ed"}), 200
        else:
            return jsonify({"status": "error", "message": "Could not respond to friend request"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@friends_bp.route("/friends/<user_id>", methods=["GET"])
def get_friends(user_id):
    try:
        friends = friends_service.get_friends(user_id)
        return jsonify({"status": "success", "friends": friends}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@friends_bp.route("/friend-requests/<user_id>", methods=["GET"])
def get_friend_requests(user_id):
    try:
        requests = friends_service.get_friend_requests(user_id)
        return jsonify({"status": "success", "requests": requests}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500