import json
import os
from flask import Blueprint, jsonify, request
from services.personality_service import save_or_update_personality

personality_bp = Blueprint("personality", __name__)

# Path to the JSON file
QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "questions", "personality_questions.json")

@personality_bp.route("/api/personality/questions", methods=["GET"])
def get_questions():
    """
    Serve the personality test questions from JSON.
    """
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
    return jsonify({"questions": questions})


@personality_bp.route("/api/personality/submit", methods=["POST"])
def submit_personality():
    """
    Accept quiz answers from the frontend, calculate personality, and save/update.
    Expected JSON: { "user_id": "some_id", "scores": { "I": 12, "E": 8, "N": 14, "S": 6, ... } }
    """
    data = request.json
    user_id = data.get("user_id")
    scores = data.get("scores")

    if not user_id or not scores:
        return jsonify({"error": "Missing user_id or scores"}), 400

    personality = save_or_update_personality(user_id, scores)

    return jsonify({"message": "Personality saved successfully", "personality": personality.dict(by_alias=True)})
