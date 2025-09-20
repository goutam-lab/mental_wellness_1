import os
import sys
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task
from utils.db import get_db
from services.chat_service import chat_model
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)
db = get_db()

def _update_streak(user_id: str):
    """Handles the logic for updating a user's daily task streak."""
    try:
        user_obj_id = ObjectId(user_id)
        user = db.users.find_one({"_id": user_obj_id})
        if not user:
            return

        today = date.today()
        last_completion = user.get('last_task_completion_date')
        
        # Convert last_completion to date object if it's a datetime
        if last_completion and isinstance(last_completion, datetime):
            last_completion_date = last_completion.date()
        else:
            last_completion_date = None

        if last_completion_date == today:
            # Already completed a task today, no change in streak
            return

        current_streak = user.get('streak', 0)
        
        if last_completion_date == today - timedelta(days=1):
            # Completed a task yesterday, increment streak
            new_streak = current_streak + 1
        else:
            # Missed a day or first completion, reset streak to 1
            new_streak = 1
        
        db.users.update_one(
            {"_id": user_obj_id},
            {"$set": {"streak": new_streak, "last_task_completion_date": datetime.combine(today, datetime.min.time())}}
        )
        logger.info(f"Streak updated for user {user_id} to {new_streak}")

    except Exception as e:
        logger.error(f"Error updating streak for user {user_id}: {e}")

def get_ai_task_suggestion(user_id: str) -> dict:
    """Generates a new task suggestion based on existing tasks."""
    try:
        user_tasks = get_tasks_by_user(user_id)
        task_titles = [f"- {task.title} (Status: {task.status})" for task in user_tasks[:10]] # Get up to 10 tasks
        
        if not task_titles:
            return {
                "title": "Practice a 5-minute mindfulness exercise.",
                "description": "Sit quietly and focus on your breath. Notice the sensation of air entering and leaving your body."
            }

        conversation_text = "\n".join(task_titles)

        template = """
        Based on the user's current tasks, suggest a new, simple, and actionable mental wellness task.
        The suggestion should be encouraging and different from the existing tasks.
        Provide the response as a JSON object with "title" and "description" keys.
        
        Example response format:
        {{"title": "Mindful Moment", "description": "Take 60 seconds to notice your surroundings using all five senses."}}

        USER'S CURRENT TASKS:
        {tasks}

        NEW TASK SUGGESTION (JSON ONLY):
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | chat_model
        response = chain.invoke({"tasks": conversation_text})
        
        # The response should be a JSON string, so we parse it
        suggestion_json = json.loads(response.content)
        return suggestion_json
    except Exception as e:
        logger.error(f"Error generating AI task suggestion for user {user_id}: {e}")
        return {"title": "Reflect on a positive memory", "description": "Think about a time you felt happy and grateful. What made it special?"}


def create_task(data: dict) -> Task:
    # ... (create_task function remains the same)
    if not data or "title" not in data or "user_id" not in data:
        raise ValueError("Title and user_id are required")
    
    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"].replace('Z', '+00:00'))
        except ValueError:
            logger.warning(f"Invalid date format: {data['due_date']}")
    
    new_task = Task(
        user_id=data["user_id"],
        title=data["title"],
        description=data.get("description"),
        category=data.get("category"),
        due_date=due_date
    )
    
    db.tasks.insert_one(new_task.to_dict())
    logger.info(f"Task created for user {data['user_id']} with ID: {new_task.id}")
    return new_task

def get_tasks_by_user(user_id: str) -> List[Task]:
    # ... (get_tasks_by_user function remains the same)
    try:
        tasks_data = list(db.tasks.find({"user_id": user_id}))
        tasks = [Task.from_dict(task_data) for task_data in tasks_data]
        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks for user {user_id}: {e}")
        return []

def get_task_suggestion(user_id: str) -> str:
    # ... (get_task_suggestion function remains the same but you can remove it if you use the new AI one)
    # This one can be kept for other parts of the app if needed, or removed.
    # For the tasks page, we will use get_ai_task_suggestion
    try:
        # ... existing logic ...
        return "Your existing suggestion logic here"
    except Exception as e:
        # ... existing error handling ...
        return "Default suggestion"

def get_task_by_id(task_id: str) -> Optional[Task]:
    # ... (get_task_by_id function remains the same)
    task_data = db.tasks.find_one({"id": task_id})
    return Task.from_dict(task_data) if task_data else None

def update_task(task_id: str, user_id: str, data: dict) -> Optional[Task]:
    task_data = db.tasks.find_one({"id": task_id, "user_id": user_id})
    if not task_data:
        return None

    update_data = {k: v for k, v in data.items() if v is not None}
    
    if "due_date" in update_data and update_data["due_date"]:
         update_data["due_date"] = datetime.fromisoformat(update_data["due_date"].replace('Z', '+00:00')).isoformat()

    if not update_data:
        return Task.from_dict(task_data)
        
    db.tasks.update_one({"id": task_id}, {"$set": update_data})
    
    # If the task is being marked as completed, update the user's streak
    if update_data.get("status") == "completed":
        _update_streak(user_id)
    
    updated_task_data = db.tasks.find_one({"id": task_id})
    return Task.from_dict(updated_task_data)

def delete_task(task_id: str, user_id: str) -> bool:
    # ... (delete_task function remains the same)
    result = db.tasks.delete_one({"id": task_id, "user_id": user_id})
    return result.deleted_count > 0