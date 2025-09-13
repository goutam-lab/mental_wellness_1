# backend/routes/chat_routes.py
from flask import Blueprint, request, jsonify
from services.chat_service import get_chat_response
from bson import ObjectId

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        user_id = data.get("user_id")
        message = data.get("message")

        if not user_id or not message:
            return jsonify({"error": "user_id and message are required"}), 400

        # Validate user_id format
        try:
            user_id_obj = ObjectId(user_id)
        except:
            return jsonify({"error": "Invalid user_id format"}), 400

        response = get_chat_response(user_id_obj, message)
        return jsonify({
            "response": response,
            "user_id": user_id,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a health check endpoint
@chat_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "chat"})