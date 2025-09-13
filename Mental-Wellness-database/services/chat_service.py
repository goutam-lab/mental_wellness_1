import os
import uuid
from bson import ObjectId
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from models.chat import Chat
from utils.db import get_db
from .embedding import embeddings, index

# Initialize Gemini model
chat_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

def get_chat_response(user_id, user_message):
    """
    RAG-powered chatbot that combines knowledge base + conversation history
    """
    db = get_db()
    
    # Fetch user
    user = db.users.find_one({"_id": user_id})
    if not user:
        return "User not found. Please re-login."
    
    personality_type = user.get("personality_type", "Unknown")
    
    # Step 1: Search knowledge base for relevant professional information
    knowledge_context = get_relevant_knowledge(user_message)
    
    # Step 2: Get relevant conversation history for personalization (RAG-based)
    conversation_history = get_conversation_history(user_id, user_message)
    
    # Step 3: Get recent conversation context (last few messages for continuity)
    recent_context = get_recent_conversation_context(user_id)
    
    # Step 4: Generate response using all contexts
    response = generate_response_with_rag(
        user_message, 
        personality_type, 
        knowledge_context, 
        conversation_history,
        recent_context
    )
    
    # Step 5: Save conversation
    save_conversation(user_id, user_message, response)
    
    return response

def get_relevant_knowledge(user_message, top_k=3):
    """Search the knowledge base for relevant professional information"""
    try:
        # Embed the user's message
        query_vector = embeddings.embed_query(user_message)
        
        # Search knowledge base namespace
        search_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace="mental_wellness_knowledge",
            filter={"doc_type": "knowledge_base"}  # Only get knowledge, not conversations
        )
        
        # Format knowledge context
        knowledge_chunks = []
        for match in search_results.get('matches', []):
            if match['score'] > 0.7:  # Only include high-relevance matches
                knowledge_chunks.append({
                    'content': match['metadata']['text'],
                    'source': match['metadata']['source'],
                    'score': match['score']
                })
        
        return knowledge_chunks
        
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        return []

def get_conversation_history(user_id, user_message, top_k=3):
    """Get semantically similar conversation history (RAG-based)"""
    try:
        # Embed the user's message
        query_vector = embeddings.embed_query(user_message)
        
        # Search user's conversation history for similar topics
        search_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace=str(user_id),  # User-specific namespace
            filter={"doc_type": "conversation"}  # Only get conversations
        )
        
        # Format relevant conversation history
        history_items = []
        for match in search_results.get('matches', []):
            if match['score'] > 0.6 and 'content' in match['metadata'] and 'response' in match['metadata']:
                past_message = match['metadata']['content']
                past_response = match['metadata']['response']
                history_items.append(f"Previously: '{past_message[:100]}...' → '{past_response[:100]}...'")
        
        return history_items
        
    except Exception as e:
        print(f"Error searching conversation history: {e}")
        return []

def get_recent_conversation_context(user_id, limit=3):
    """Get recent conversation context for continuity (chronological, not RAG)"""
    try:
        db = get_db()
        
        # Get last few conversations chronologically
        recent_chats = db.chats.find(
            {"user_id": user_id}
        ).sort("_id", -1).limit(limit)
        
        recent_context = []
        for chat in recent_chats:
            user_msg = chat.get('user_message', '')
            bot_msg = chat.get('bot_response', '')
            recent_context.append(f"Recent: '{user_msg[:80]}...' → '{bot_msg[:80]}...'")
        
        return list(reversed(recent_context))  # Reverse to chronological order
        
    except Exception as e:
        print(f"Error getting recent context: {e}")
        return []

def generate_response_with_rag(user_message, personality_type, knowledge_context, conversation_history, recent_context):
    """Generate response using comprehensive RAG approach"""
    
    # Format knowledge context from professional sources
    knowledge_section = ""
    sources = []
    
    if knowledge_context:
        knowledge_section = "PROFESSIONAL MENTAL HEALTH KNOWLEDGE:\n"
        for i, chunk in enumerate(knowledge_context):
            knowledge_section += f"• {chunk['content'][:300]}...\n"
            sources.append(chunk['source'])
        knowledge_section += "\n"
    
    # Format similar conversation history (RAG-retrieved)
    similar_conversations = ""
    if conversation_history:
        similar_conversations = "SIMILAR PAST DISCUSSIONS:\n"
        for item in conversation_history:
            similar_conversations += f"• {item}\n"
        similar_conversations += "\n"
    
    # Format recent conversation context (for continuity)
    recent_conversation = ""
    if recent_context:
        recent_conversation = "RECENT CONVERSATION CONTEXT:\n"
        for item in recent_context:
            recent_conversation += f"• {item}\n"
        recent_conversation += "\n"
    
    # Comprehensive RAG prompt template
    template = """You are an empathetic mental wellness chatbot with access to professional resources and complete conversation context.

User Profile:
- Personality Type: {personality_type}

{knowledge_section}

{similar_conversations}

{recent_conversation}

Current User Message: {user_message}

Instructions:
1. Use the professional knowledge above to provide evidence-based guidance
2. Reference recent conversations to maintain therapeutic continuity  
3. Use similar past discussions to understand recurring themes and progress
4. Adapt advice to user's personality type and conversation history
5. Be warm, supportive, and encouraging
6. If serious issues arise, gently suggest professional help
7. Keep response comprehensive but not overwhelming (2-3 paragraphs)

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
        
        # Add source attribution if knowledge was used
        if sources:
            unique_sources = list(set(sources))[:2]  # Limit to 2 sources
            response += f"\n\nSources: {', '.join(unique_sources)}"
        
        return response
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble generating a response right now. Please try again."

def save_conversation(user_id, user_message, response):
    """Save conversation to both MongoDB and Pinecone"""
    try:
        db = get_db()
        
        # Save to MongoDB
        chat_entry = Chat(user_id, user_message, response)
        result = db.chats.insert_one(chat_entry.to_dict())
        
        # Create embedding and save to Pinecone
        vector = embeddings.embed_query(user_message)
        pinecone_id = str(uuid.uuid4())
        
        # IMPORTANT: Include doc_type for proper filtering
        index.upsert([
            {
                "id": pinecone_id,
                "values": vector,
                "metadata": {
                    "userId": str(user_id),
                    "role": "user",
                    "content": user_message,
                    "response": response,
                    "doc_type": "conversation",  # This is crucial for filtering
                    "timestamp": str(result.inserted_id)
                }
            }
        ], namespace=str(user_id))  # Store in user-specific namespace
        
        # Update MongoDB with Pinecone reference
        db.chats.update_one(
            {"_id": result.inserted_id},
            {"$set": {"pineconeId": pinecone_id, "embedding": vector}}
        )
        
    except Exception as e:
        print(f"Error saving conversation: {e}")