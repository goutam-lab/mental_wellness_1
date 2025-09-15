# models/risk_event.py
from datetime import datetime

class RiskEvent:
    def __init__(self, user_id, risk_level, message):
        self.user_id = user_id
        self.risk_level = risk_level
        self.message = message
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "risk_level": self.risk_level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }