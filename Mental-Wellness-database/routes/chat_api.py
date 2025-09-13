from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from services.chat_service import get_chat_response

router = APIRouter()

# Request schema
class ChatRequest(BaseModel):
    user_id: str
    user_message: str

# API endpoint
@router.post("/chat")
async def chat_with_bot(req: ChatRequest):
    try:
        # Convert user_id string to ObjectId if needed
        user_id = ObjectId(req.user_id)
        response = get_chat_response(user_id, req.user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))