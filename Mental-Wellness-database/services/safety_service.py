# services/safety_service.py
from models.risk_event import RiskEvent

try:
    from utils.db import get_db
    
    def get_risk_events_collection():
        """Get the risk_events collection from MongoDB"""
        db = get_db()
        return db.risk_events

    def process_risk_event(event: RiskEvent):
        # Static recommendations
        recommended_contacts = {
            "helplines": [
                {"name": "KIRAN Mental Health Helpline", "phone": "1800-599-0019"},
                {"name": "Vandrevala Foundation Helpline", "phone": "1860-2662-345"}
            ],
            "emergency": "Dial 112 (India Emergency Services)"
        }

        # Store event in MongoDB
        risk_events_collection = get_risk_events_collection()
        event_dict = event.to_dict()
        result = risk_events_collection.insert_one(event_dict)
        event_dict['_id'] = str(result.inserted_id)

        return {
            "event": event_dict,
            "contacts": recommended_contacts
        }

except ImportError:
    # Fallback to in-memory storage if MongoDB utils not available
    risk_events_db = []
    
    def process_risk_event(event: RiskEvent):
        # Static recommendations
        recommended_contacts = {
            "helplines": [
                {"name": "KIRAN Mental Health Helpline", "phone": "1800-599-0019"},
                {"name": "Vandrevala Foundation Helpline", "phone": "1860-2662-345"}
            ],
            "emergency": "Dial 112 (India Emergency Services)"
        }

        # Store event in memory
        event_dict = event.to_dict()
        risk_events_db.append(event_dict)

        return {
            "event": event_dict,
            "contacts": recommended_contacts
        }