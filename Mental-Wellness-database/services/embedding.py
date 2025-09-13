import os
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Initialize the embeddings model using your API Key
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 2. Initialize Pinecone
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")
    index = pc.Index(index_name)
except Exception as e:
    print(f"Error connecting to Pinecone: {e}")
    index = None