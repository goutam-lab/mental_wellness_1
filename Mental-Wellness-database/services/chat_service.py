# services/chat_service.py
import os
import uuid
from bson import ObjectId
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from models.chat import Chat
from utils.db import get_db
from .embedding import embeddings, index

# Initialize Chat Model via OpenRouter
chat_model = ChatOpenAI(
    model="google/gemini-flash-1.5",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Mental Wellness App",
    }
)

def get_chat_response(user_id, user_message):
    db = get_db()
    user = db.users.find_one({"_id": user_id})
    if not user:
        return "User not found. Please re-login."
    
    personality_type = user.get("personality_type", "Unknown")
    
    knowledge_context = get_relevant_knowledge(user_message)
    conversation_history = get_conversation_history(user_id, user_message)
    recent_context = get_recent_conversation_context(user_id)
    
    response = generate_response_with_rag(
        user_message, 
        personality_type, 
        knowledge_context, 
        conversation_history,
        recent_context
    )
    
    save_conversation(user_id, user_message, response)
    
    return response

def get_relevant_knowledge(user_message, top_k=3):
    try:
        query_vector = embeddings.embed_query(user_message)
        
        # Ensure query_vector is a list of floats before proceeding
        if not isinstance(query_vector, list):
            print(f"Failed to generate a valid embedding for the message: {user_message}")
            return []

        search_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace="mental_wellness_knowledge",
            filter={"doc_type": "knowledge_base"}
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
            print(f"Failed to generate a valid embedding for conversation history search: {user_message}")
            return []

        search_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace=str(user_id),
            filter={"doc_type": "conversation"}
        )
        
        history_items = []
        for match in search_results.get('matches', []):
            if match['score'] > 0.6 and 'content' in match['metadata'] and 'response' in match['metadata']:
                history_items.append(f"Previously: '{match['metadata']['content'][:100]}...' → '{match['metadata']['response'][:100]}...'")
        return history_items
    except Exception as e:
        print(f"Error searching conversation history: {e}")
        return []

def get_recent_conversation_context(user_id, limit=3):
    try:
        db = get_db()
        recent_chats = list(db.chats.find({"user_id": user_id}).sort("_id", -1).limit(limit))
        
        recent_context = []
        for chat in recent_chats:
            user_msg = chat.get('user_message', '')
            bot_msg = chat.get('bot_response', '')
            recent_context.append(f"Recent: '{user_msg[:80]}...' → '{bot_msg[:80]}...'")
        
        return list(reversed(recent_context))
    except Exception as e:
        print(f"Error getting recent context: {e}")
        return []

def generate_response_with_rag(user_message, personality_type, knowledge_context, conversation_history, recent_context):
    knowledge_section = ""
    if knowledge_context:
        knowledge_section = "PROFESSIONAL MENTAL HEALTH KNOWLEDGE:\n" + "\n".join([f"• {c['content'][:300]}..." for c in knowledge_context]) + "\n"
    
    similar_conversations = ""
    if conversation_history:
        similar_conversations = "SIMILAR PAST DISCUSSIONS:\n" + "\n".join([f"• {item}" for item in conversation_history]) + "\n"

    recent_conversation = ""
    if recent_context:
        recent_conversation = "RECENT CONVERSATION CONTEXT:\n" + "\n".join([f"• {item}" for item in recent_context]) + "\n"
    
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
        
        response = chain.invoke({
            "user_message": user_message,
            "personality_type": personality_type,
            "knowledge_section": knowledge_section,
            "similar_conversations": similar_conversations,
            "recent_conversation": recent_conversation
        }).content
        
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble generating a response. Please try again."

def save_conversation(user_id, user_message, response):
    try:
        db = get_db()
        chat_entry = Chat(user_id, user_message, response)
        result = db.chats.insert_one(chat_entry.to_dict())
        
        vector = embeddings.embed_query(user_message)
        if not isinstance(vector, list):
            print(f"Failed to generate embedding for saving conversation. Skipping Pinecone upsert.")
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