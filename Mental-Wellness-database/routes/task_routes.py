from flask import Blueprint, request, jsonify
from services import task_service  # Fixed import

task_bp = Blueprint("tasks", __name__)

# ------------------------
# Create a new task
# ------------------------
@task_bp.route("/tasks", methods=["POST"])
def create_task_route():
    try:
        data = request.get_json()
        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400
            
        task = task_service.create_task(data)  # Fixed call
        return jsonify({"task": task.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Get all tasks + suggestion
# ------------------------
@task_bp.route("/tasks", methods=["GET"])
def get_tasks_route():
    try:
        tasks = task_service.get_all_tasks()  # Fixed call
        task_dicts = [task.to_dict() for task in tasks]

        # Wellness suggestion logic
        suggestion = None
        if len(task_dicts) > 5:
            suggestion = "You've got a heavy workload. Take a 5-minute stretch break!"
        elif not task_dicts:
            suggestion = "No tasks today? Maybe do a quick mindfulness exercise."
        else:
            suggestion = "Great job staying on track! Stay hydrated."

        return jsonify({"tasks": task_dicts, "suggestion": suggestion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Get a single task by ID
# ------------------------
@task_bp.route("/tasks/<task_id>", methods=["GET"])
def get_task_route(task_id):
    try:
        task = task_service.get_task_by_id(task_id)  # Fixed call
        if not task:
            return jsonify({"message": "Task not found"}), 404
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Update a task
# ------------------------
@task_bp.route("/tasks/<task_id>", methods=["PUT"])
def update_task_route(task_id):
    try:
        data = request.get_json()
        task = task_service.update_task(task_id, data)  # Fixed call
        if not task:
            return jsonify({"message": "Task not found"}), 404
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Delete a task
# ------------------------
@task_bp.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task_route(task_id):
    try:
        success = task_service.delete_task(task_id)  # Fixed call
        if not success:
            return jsonify({"message": "Task not found"}), 404
        return jsonify({"message": "Task deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500