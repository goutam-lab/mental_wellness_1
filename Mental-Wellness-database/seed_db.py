# Import the function that connects to your MongoDB
from backend.utils.db import get_db

# This is the personality questions data you provided
questions_data = [
  { "id": 1, "question": "Do you feel more energized after spending time alone than after social gatherings?", "dimension": ["I", "E"] },
  { "id": 2, "question": "Do you usually start conversations rather than waiting for others?", "dimension": ["I", "E"] },
  { "id": 3, "question": "Do you find long periods of social interaction draining?", "dimension": ["I", "E"] },
  { "id": 4, "question": "Do you enjoy being the center of attention in groups?", "dimension": ["I", "E"] },
  { "id": 5, "question": "Do you often prefer writing over speaking in face-to-face interactions?", "dimension": ["I", "E"] },
  { "id": 6, "question": "Do you usually act quickly in social situations rather than thinking first?", "dimension": ["I", "E"] },
  { "id": 7, "question": "Do you usually recharge by being around people instead of spending time alone?", "dimension": ["I", "E"] },

  { "id": 8, "question": "Do you focus more on future possibilities rather than present realities?", "dimension": ["N", "S"] },
  { "id": 9, "question": "Do you find yourself drawn to abstract theories rather than concrete facts?", "dimension": ["N", "S"] },
  { "id": 10, "question": "Do you often think about what could be rather than what is?", "dimension": ["N", "S"] },
  { "id": 11, "question": "Do you prefer practical examples over conceptual explanations?", "dimension": ["N", "S"] },
  { "id": 12, "question": "Do you rely more on gut feelings than step-by-step analysis?", "dimension": ["N", "S"] },
  { "id": 13, "question": "Do you prefer detailed instructions rather than broad overviews?", "dimension": ["N", "S"] },
  { "id": 14, "question": "Do you get excited imagining future scenarios more than focusing on present tasks?", "dimension": ["N", "S"] },

  { "id": 15, "question": "Do you usually base decisions on logic and consistency over emotions?", "dimension": ["T", "F"] },
  { "id": 16, "question": "Do you find it easier to point out flaws than to comfort others?", "dimension": ["T", "F"] },
  { "id": 17, "question": "Do you value objective truth over personal values when making decisions?", "dimension": ["T", "F"] },
  { "id": 18, "question": "Do you find yourself naturally empathetic in emotional situations?", "dimension": ["T", "F"] },
  { "id": 19, "question": "Do you prefer to remain impartial rather than getting emotionally involved?", "dimension": ["T", "F"] },
  { "id": 20, "question": "Do you often rely on fairness more than compassion in conflicts?", "dimension": ["T", "F"] },
  { "id": 21, "question": "Do you usually decide based on feelings rather than rational analysis?", "dimension": ["T", "F"] },

  { "id": 22, "question": "Do you prefer having a detailed plan before starting something?", "dimension": ["J", "P"] },
  { "id": 23, "question": "Do you feel uncomfortable when things are unstructured?", "dimension": ["J", "P"] },
  { "id": 24, "question": "Do you enjoy deadlines as motivation rather than open timelines?", "dimension": ["J", "P"] },
  { "id": 25, "question": "Do you prefer to keep your options open rather than committing early?", "dimension": ["J", "P"] },
  { "id": 26, "question": "Do you find spontaneity more enjoyable than sticking to a schedule?", "dimension": ["J", "P"] },
  { "id": 27, "question": "Do you often make to-do lists and stick to them?", "dimension": ["J", "P"] },
  { "id": 28, "question": "Do you handle last-minute changes with ease rather than frustration?", "dimension": ["J", "P"] }
]

def seed_questions():
    """
    Inserts the personality questions into the database if the collection is empty.
    """
    try:
        db = get_db()
        questions_collection = db.questions

        # Check if the collection is already populated to avoid duplicates
        if questions_collection.count_documents({}) == 0:
            print("Seeding personality questions into the database...")
            # Insert all the questions into the 'questions' collection
            questions_collection.insert_many(questions_data)
            print("✅ Questions seeded successfully.")
        else:
            print("Questions collection is already populated. No action needed.")
            
    except Exception as e:
        print(f"An error occurred while seeding the database: {e}")


if __name__ == "__main__":
    seed_questions()