import os
import sys
import logging
from datetime import datetime
from typing import Optional, List

# FIX: Add the parent directory to Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import your modules
from models.task import Task
from utils.db import get_db

# Set up logging
logger = logging.getLogger(__name__)

def create_task(data: dict) -> Task:
    """
    Create a new task and save it to MongoDB
    """
    try:
        # Validate required fields
        if not data or "title" not in data:
            raise ValueError("Title is required")
        
        # Parse due_date if provided
        due_date = None
        if data.get("due_date"):
            try:
                due_date = datetime.fromisoformat(data["due_date"].replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid date format: {data['due_date']}")
                # Continue without due_date if format is invalid
        
        # Create new task
        new_task = Task(
            title=data.get("title"),
            description=data.get("description"),
            category=data.get("category"),
            due_date=due_date
        )
        
        # Save to MongoDB
        db = get_db()
        task_dict = new_task.to_dict()
        # Convert datetime objects to strings for MongoDB
        if task_dict.get('created_at'):
                if hasattr(task_dict['created_at'], 'isoformat'):
                    task_dict['created_at'] = task_dict['created_at'].isoformat()
        if task_dict.get('due_date'):
            if hasattr(task_dict['due_date'], 'isoformat'):
                task_dict['due_date'] = task_dict['due_date'].isoformat()
            
        result = db.tasks.insert_one(task_dict)
        logger.info(f"Task created with ID: {new_task.id}")
        return new_task
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise

def get_all_tasks() -> List[Task]:
    """
    Get all tasks from MongoDB
    """
    try:
        db = get_db()
        tasks_data = list(db.tasks.find())
        
        tasks = []
        for task_data in tasks_data:
            try:
                # Convert string dates back to datetime objects
                if task_data.get('created_at'):
                    task_data['created_at'] = datetime.fromisoformat(task_data['created_at'].replace('Z', '+00:00'))
                if task_data.get('due_date'):
                    task_data['due_date'] = datetime.fromisoformat(task_data['due_date'].replace('Z', '+00:00'))
                
                task = Task(**task_data)
                tasks.append(task)
            except Exception as e:
                logger.warning(f"Error parsing task data {task_data.get('id')}: {e}")
                continue
                
        logger.info(f"Retrieved {len(tasks)} tasks from database")
        return tasks
        
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}")
        return []  # Return empty list instead of crashing

def get_task_by_id(task_id: str) -> Optional[Task]:
    """
    Get a single task by ID from MongoDB
    """
    try:
        db = get_db()
        task_data = db.tasks.find_one({"id": task_id})
        
        if not task_data:
            logger.info(f"Task not found with ID: {task_id}")
            return None
        
        # Convert string dates back to datetime objects
        if task_data.get('created_at'):
            task_data['created_at'] = datetime.fromisoformat(task_data['created_at'].replace('Z', '+00:00'))
        if task_data.get('due_date'):
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date'].replace('Z', '+00:00'))
        
        task = Task(**task_data)
        logger.info(f"Task found with ID: {task_id}")
        return task
        
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        return None

def update_task(task_id: str, data: dict) -> Optional[Task]:
    """
    Update a task in MongoDB
    """
    try:
        db = get_db()
        task_data = db.tasks.find_one({"id": task_id})
        
        if not task_data:
            logger.warning(f"Task not found for update: {task_id}")
            return None

        # Prepare update data
        update_data = {}
        if "title" in data:
            update_data["title"] = data["title"]
        if "description" in data:
            update_data["description"] = data["description"]
        if "category" in data:
            update_data["category"] = data["category"]
        if "status" in data:
            update_data["status"] = data["status"]
        if "due_date" in data:
            try:
                update_data["due_date"] = datetime.fromisoformat(data["due_date"].replace('Z', '+00:00')).isoformat()
            except ValueError:
                logger.warning(f"Invalid date format for update: {data['due_date']}")
                # Skip due_date update if format is invalid

        # Update the task
        result = db.tasks.update_one({"id": task_id}, {"$set": update_data})
        
        if result.modified_count == 0:
            logger.warning(f"No changes made to task: {task_id}")
            # Still return the existing task
            return get_task_by_id(task_id)
        
        # Get the updated task
        updated_task_data = db.tasks.find_one({"id": task_id})
        
        # Convert string dates back to datetime objects
        if updated_task_data.get('created_at'):
            updated_task_data['created_at'] = datetime.fromisoformat(updated_task_data['created_at'].replace('Z', '+00:00'))
        if updated_task_data.get('due_date'):
            updated_task_data['due_date'] = datetime.fromisoformat(updated_task_data['due_date'].replace('Z', '+00:00'))
        
        updated_task = Task(**updated_task_data)
        logger.info(f"Task updated successfully: {task_id}")
        return updated_task
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return None

def delete_task(task_id: str) -> bool:
    """
    Delete a task from MongoDB
    """
    try:
        db = get_db()
        result = db.tasks.delete_one({"id": task_id})
        
        if result.deleted_count > 0:
            logger.info(f"Task deleted successfully: {task_id}")
            return True
        else:
            logger.warning(f"Task not found for deletion: {task_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return False

# Optional: Add some test data if collection is empty
def initialize_sample_tasks():
    """
    Initialize with sample tasks if the collection is empty
    """
    try:
        db = get_db()
        if db.tasks.count_documents({}) == 0:
            sample_tasks = [
                {
                    "title": "Complete API documentation",
                    "description": "Write comprehensive docs for the Task API",
                    "category": "development",
                    "status": "pending",
            "due_date": datetime(2023, 12, 20, 23, 59, 59)
                },
                {
                    "title": "Test Postman integration",
                    "description": "Test all endpoints using Postman",
                    "category": "testing",
                    "status": "completed",
                    "due_date": datetime(2023, 12, 15, 18, 0, 0)
                }
            ]
            
            for task_data in sample_tasks:
                task = Task(**task_data)
                task_dict = task.to_dict()
                if hasattr(task_dict['created_at'], 'isoformat'):
                    task_dict['created_at'] = task_dict['created_at'].isoformat()
                if task_dict.get('due_date') and hasattr(task_dict['due_date'], 'isoformat'):
                    task_dict['due_date'] = task_dict['due_date'].isoformat()
                db.tasks.insert_one(task_dict)
            
            logger.info("Sample tasks initialized")
            
    except Exception as e:
        logger.error(f"Error initializing sample tasks: {e}")

# Initialize sample tasks when this module is imported
try:
    initialize_sample_tasks()
except Exception as e:
    logger.error(f"Failed to initialize sample tasks: {e}")