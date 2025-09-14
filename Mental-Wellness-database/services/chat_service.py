# backend/services/chat_service.py
import os
import uuid
import traceback
import json
from bson import ObjectId
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from models.chat import Chat
from utils.db import get_db
from .embedding import embeddings, index
from datetime import datetime
from models.conversation import Conversation
import httpx
import certifi # Import certifi

# --- MODEL INITIALIZATION WITH THE DEFINITIVE SSL FIX ---
# We will use certifi.where() to get the correct, absolute path to the certificate bundle.
# This is the robust way to handle SSL verification.
chat_model = ChatOpenAI(
    model="mistralai/mistral-small-3.2-24b-instruct:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Mental Wellness App",
    },
    # Use httpx.Client with verify pointing to certifi's certificate bundle
    http_client=httpx.Client(verify=certifi.where())
)

def generate_title_for_conversation(first_message: str) -> str:
    """
    Generates a short, relevant title for a conversation.
    """
    try:
        template = "Summarize the following user query in 3-5 words to be used as a title for a chat conversation. Be concise. Do not use quotes. User Query: '{message}'"
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | chat_model
        response = chain.invoke({"message": first_message})
        title = response.content.strip().strip('"')
        return title
    except Exception as e:
        print(f"Error generating title: {e}")
        return "New Chat"

def get_chat_response_stream(user_id: ObjectId, user_message: str, conversation_id: str):
    """
    Generates a response using RAG and streams it to the client via SSE.
    """
    db = get_db()
    user = db.users.find_one({"_id": user_id})
    if not user:
        yield f"data: {json.dumps({'error': 'User not found'})}\n\n"
        return

    is_new_conversation = db.conversations.find_one({"conversation_id": conversation_id, "user_id": str(user_id)}) is None

    # --- RAG CONTEXT GATHERING ---
    personality_type = user.get("personality_type", "Unknown")
    knowledge_context = get_relevant_knowledge(user_message)
    conversation_history = get_conversation_history(str(user_id), user_message)
    recent_context = get_recent_conversation_context(user_id, conversation_id)

    # --- PROMPT TEMPLATE ---
    knowledge_section = "PROFESSIONAL MENTAL HEALTH KNOWLEDGE:\n" + "\n".join([f"- {c['content'][:300]}..." for c in knowledge_context]) + "\n" if knowledge_context else ""
    similar_conversations = "SIMILAR PAST DISCUSSIONS:\n" + "\n".join([f"- {item}" for item in conversation_history]) + "\n" if conversation_history else ""
    recent_conversation = "RECENT CONVERSATION CONTEXT:\n" + "\n".join([f"- {item}" for item in recent_context]) + "\n" if recent_context else ""

    template = """You are an empathetic mental wellness chatbot. Your goal is to be warm, supportive, and encouraging.
    User Profile:
    - Personality Type: {personality_type}
    {knowledge_section}
    {similar_conversations}
    {recent_conversation}
    Current User Message: {user_message}
    Response:"""

    try:
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | chat_model

        full_response = ""
        for chunk in chain.stream({
            "user_message": user_message,
            "personality_type": personality_type,
            "knowledge_section": knowledge_section,
            "similar_conversations": similar_conversations,
            "recent_conversation": recent_conversation
        }):
            content = chunk.content
            if content:
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"

        save_conversation(user_id, user_message, full_response, conversation_id)

        if is_new_conversation:
            title = generate_title_for_conversation(user_message)
            new_convo_meta = Conversation(
                conversation_id=conversation_id,
                user_id=str(user_id),
                title=title
            )
            db.conversations.insert_one(new_convo_meta.model_dump(by_alias=True))
        else:
             db.conversations.update_one(
                {"conversation_id": conversation_id},
                {"$set": {"updated_at": datetime.utcnow()}}
            )

        yield f"data: {json.dumps({'end': True, 'conversation_id': conversation_id})}\n\n"

    except Exception as e:
        print(f"Error in response stream: {e}")
        traceback.print_exc()
        yield f"data: {json.dumps({'error': 'I am sorry, I am having trouble generating a response. Please try again.'})}\n\n"

def save_conversation(user_id: ObjectId, user_message: str, response: str, conversation_id: str):
    try:
        db = get_db()
        chat_entry = Chat(user_id, user_message, response, conversation_id)
        result = db.chats.insert_one(chat_entry.to_dict())
        
        vector = embeddings.embed_query(user_message)
        if not isinstance(vector, list):
            print("Failed to generate embedding for conversation. Skipping Pinecone upsert.")
            return

        pinecone_id = str(uuid.uuid4())
        index.upsert(
            vectors=[{
                "id": pinecone_id,
                "values": vector,
                "metadata": {
                    "userId": str(user_id),
                    "content": user_message,
                    "response": response,
                    "doc_type": "conversation",
                    "timestamp": str(result.inserted_id)
                }
            }],
            namespace=str(user_id)
        )
        
        db.chats.update_one({"_id": result.inserted_id}, {"$set": {"pineconeId": pinecone_id}})
    except Exception as e:
        print(f"Error saving conversation: {e}")
        traceback.print_exc()

def get_relevant_knowledge(user_message, top_k=3):
    try:
        query_vector = embeddings.embed_query(user_message)
        if not isinstance(query_vector, list):
            return []
        search_results = index.query(
            vector=query_vector, top_k=top_k, include_metadata=True,
            namespace="mental_wellness_knowledge", filter={"doc_type": "knowledge_base"}
        )
        knowledge_chunks = []
        for match in search_results.get('matches', []):
            if match['score'] > 0.7:
                knowledge_chunks.append({
                    'content': match['metadata']['content'],
                    'source': match['metadata']['source'],
                })
        return knowledge_chunks
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        return []

def get_conversation_history(user_id, user_message, top_k=3):
    try:
        query_vector = embeddings.embed_query(user_message)
        if not isinstance(query_vector, list):
            return []
        search_results = index.query(
            vector=query_vector, top_k=top_k, include_metadata=True,
            namespace=str(user_id), filter={"doc_type": "conversation"}
        )
        history_items = []
        for match in search_results.get('matches', []):
            if match['score'] > 0.6 and 'content' in match['metadata'] and 'response' in match['metadata']:
                history_items.append(f"Previously: '{match['metadata']['content'][:100]}...' -> '{match['metadata']['response'][:100]}...'")
        return history_items
    except Exception as e:
        print(f"Error searching conversation history: {e}")
        return []

def get_recent_conversation_context(user_id, conversation_id, limit=3):
    try:
        db = get_db()
        recent_chats = list(db.chats.find({"user_id": user_id, "conversation_id": conversation_id}).sort("timestamp", -1).limit(limit))
        recent_context = []
        for chat in reversed(recent_chats):
            user_msg = chat.get('user_message', '')
            bot_msg = chat.get('bot_response', '')
            recent_context.append(f"Recent: '{user_msg[:80]}...' -> '{bot_msg[:80]}...'")
        return recent_context
    except Exception as e:
        print(f"Error getting recent context: {e}")
        return []