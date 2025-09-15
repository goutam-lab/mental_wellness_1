# routes/safety_routes.py
from flask import Blueprint, request, jsonify
from models.risk_event import RiskEvent
from services.safety_service import process_risk_event

safety_bp = Blueprint("safety", __name__)

@safety_bp.route("/risk-event", methods=["POST"])
def handle_risk_event():
    try:
        data = request.get_json()
        if not data or "user_id" not in data or "risk_level" not in data or "message" not in data:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        event = RiskEvent(
            user_id=data.get("user_id"),
            risk_level=data.get("risk_level"),
            message=data.get("message")
        )
        result = process_risk_event(event)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500