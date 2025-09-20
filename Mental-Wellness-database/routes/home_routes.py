from flask import Blueprint, Response
from utils.db import get_db
from bson import ObjectId, json_util
import logging
import json

home_bp = Blueprint("home", __name__)
logger = logging.getLogger(__name__)

@home_bp.route("/home/<user_id>", methods=["GET"])
def get_home_data(user_id):
    db = get_db()
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        return Response(json.dumps({"error": "Invalid user ID format"}), status=400, mimetype='application/json')

    try:
        user = db.users.find_one({"_id": user_obj_id}, {"password_hash": 0})
        
        if not user:
            return Response(json.dumps({"error": "User not found"}), status=404, mimetype='application/json')

        tasks_cursor = db.tasks.find(
            {"user_id": user_id, "status": "pending"}
        ).sort("created_at", -1).limit(3)
        
        tasks = list(tasks_cursor)

        # The 'user' document already contains the 'streak' field
        home_data = {
            "user": user,
            "pendingTasks": tasks
        }
        
        response_json = json_util.dumps(home_data)
        
        return Response(response_json, status=200, mimetype='application/json')

    except Exception as e:
        logger.error(f"Error fetching home data for user {user_id}: {e}", exc_info=True)
        return Response(json.dumps({"error": "An internal server error occurred"}), status=500, mimetype='application/json')