from typing import Dict
from datetime import datetime
from bson import ObjectId
from models.personality import Personality
from utils.db import db

# ---- Personality Calculation Logic ----
def calculate_personality_type(scores: Dict[str, int]) -> str:
    """
    Given raw scores for each dimension, return the MBTI type.
    Expected keys in scores: I, E, N, S, T, F, J, P
    """
    type_code = ""

    # I vs E
    type_code += "I" if scores.get("I", 0) >= scores.get("E", 0) else "E"

    # N vs S
    type_code += "N" if scores.get("N", 0) >= scores.get("S", 0) else "S"

    # T vs F
    type_code += "T" if scores.get("T", 0) >= scores.get("F", 0) else "F"

    # J vs P
    type_code += "J" if scores.get("J", 0) >= scores.get("P", 0) else "P"

    return type_code


# ---- Personality Service ----
def save_or_update_personality(user_id: str, scores: Dict[str, int]) -> Personality:
    """
    Save or update a user's personality test result in MongoDB.
    """
    collection = db["personalities"]

    # Calculate MBTI type
    personality_type = calculate_personality_type(scores)

    # Check if user already has a personality profile
    existing = collection.find_one({"user_id": user_id})

    if existing:
        # Update existing personality
        collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "personality_type": personality_type,
                "introversion_score": scores.get("I", 0),
                "extraversion_score": scores.get("E", 0),
                "intuition_score": scores.get("N", 0),
                "sensing_score": scores.get("S", 0),
                "thinking_score": scores.get("T", 0),
                "feeling_score": scores.get("F", 0),
                "judging_score": scores.get("J", 0),
                "perceiving_score": scores.get("P", 0),
                "updated_at": datetime.utcnow()
            }}
        )
        updated = collection.find_one({"user_id": user_id})
        return Personality(**updated)

    else:
        # Create a new personality document
        new_personality = Personality(
            user_id=user_id,
            personality_type=personality_type,
            introversion_score=scores.get("I", 0),
            extraversion_score=scores.get("E", 0),
            intuition_score=scores.get("N", 0),
            sensing_score=scores.get("S", 0),
            thinking_score=scores.get("T", 0),
            feeling_score=scores.get("F", 0),
            judging_score=scores.get("J", 0),
            perceiving_score=scores.get("P", 0),
            created_at=datetime.utcnow()
        )
        collection.insert_one(new_personality.dict(by_alias=True))
        return new_personality
