# backend/routes/chat_routes.py
import traceback
import json
from flask import Blueprint, request, jsonify, Response
from services.chat_service import get_chat_response_stream
from utils.db import get_db
from bson import ObjectId, json_util
import uuid

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        message = data.get("message")
        conversation_id = data.get("conversation_id")

        if not user_id or not message:
            return jsonify({"error": "user_id and message are required"}), 400
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        user_id_obj = ObjectId(user_id)
        
        return Response(get_chat_response_stream(user_id_obj, message, conversation_id), mimetype='text/event-stream')

    except Exception as e:
        print(f"An error occurred in /chat: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred"}), 500

@chat_bp.route("/chat/history/<user_id>", methods=["GET"])
def get_history(user_id):
    try:
        db = get_db()
        # Query the new 'conversations' collection
        conversations_cursor = db.conversations.find(
            {"user_id": user_id}
        ).sort("updated_at", -1).limit(50)
        
        history = [
            {"conversation_id": convo["conversation_id"], "title": convo["title"]}
            for convo in conversations_cursor
        ]
        
        return jsonify({"history": history})

    except Exception as e:
        print(f"An error occurred in /chat/history: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred"}), 500

@chat_bp.route("/conversation/<conversation_id>", methods=["GET"])
def get_conversation_messages(conversation_id):
    try:
        db = get_db()
        messages_cursor = db.chats.find({"conversation_id": conversation_id}).sort("timestamp", 1)
        
        messages = json.loads(json_util.dumps(list(messages_cursor)))
        
        return jsonify({"messages": messages})

    except Exception as e:
        print(f"An error occurred in /conversation/<conversation_id>: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred"}), 500