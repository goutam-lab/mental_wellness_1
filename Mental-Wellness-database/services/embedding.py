# services/embedding.py
import os
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

# 1. Initialize the embeddings model using OpenRouter
# Note: We are using a standard embedding model available on OpenRouter.
# You can replace "text-embedding-ada-002" with another model if you prefer.
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# 2. Initialize Pinecone
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")
    index = pc.Index(index_name)
    print("✅ Successfully connected to Pinecone.")
except Exception as e:
    print(f"Error connecting to Pinecone: {e}")
    index = None