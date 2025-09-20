
from flask import Blueprint, request, jsonify
from services import task_service
# Remove the line below that's causing the error
# from models.task import TaskCreateRequest, TaskUpdateRequest 

task_bp = Blueprint("tasks", __name__)

@task_bp.route("/tasks/ai-suggestion/<user_id>", methods=["GET"])
def get_ai_suggestion_route(user_id):
    """New route to get an AI-powered task suggestion."""
    try:
        suggestion = task_service.get_ai_task_suggestion(user_id)
        return jsonify(suggestion), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks", methods=["POST"])
def create_task_route():
    try:
        data = request.get_json()
        if not data or "title" not in data or "user_id" not in data:
            return jsonify({"error": "Title and user_id are required"}), 400
        
        task = task_service.create_task(data)
        return jsonify(task.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ... the rest of the file remains exactly the same.
@task_bp.route("/tasks/user/<user_id>", methods=["GET"])
def get_tasks_for_user_route(user_id):
    try:
        tasks = task_service.get_tasks_by_user(user_id)
        # Add the suggestion to the response for the home page
        suggestion = task_service.get_task_suggestion(user_id)
        task_dicts = [task.to_dict() for task in tasks]
        return jsonify({"tasks": task_dicts, "suggestion": suggestion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<task_id>", methods=["GET"])
def get_task_route(task_id):
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            return jsonify({"message": "Task not found"}), 404
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<task_id>", methods=["PUT"])
def update_task_route(task_id):
    try:
        data = request.get_json()
        # No user_id is needed in the body for an update.
        # The service layer should handle authorization if necessary.
        task = task_service.update_task(task_id, data)
        if not task:
            return jsonify({"message": "Task not found"}), 404
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task_route(task_id):
    try:
        success = task_service.delete_task(task_id)
        if not success:
            return jsonify({"message": "Task not found"}), 404
        return jsonify({"message": "Task deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500