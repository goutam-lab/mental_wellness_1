# services/embedding.py
import os
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

# --- CRITICAL FIX for AuthenticationError ---
# Explicitly pass the API key and required headers to the embeddings model constructor.
# This ensures it uses the correct key every time it's called.
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"), # Explicitly pass the key
    base_url="https://openrouter.ai/api/v1",
    default_headers={  # Add required headers for OpenRouter embeddings
        "HTTP-Referer": "http://localhost:3000", # Or your frontend URL
        "X-Title": "Mental Wellness App",
    }
)

# Initialize Pinecone
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")
    index = pc.Index(index_name)
    print("✅ Successfully connected to Pinecone.")
except Exception as e:
    print(f"Error connecting to Pinecone: {e}")
    index = None