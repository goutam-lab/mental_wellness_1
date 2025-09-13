import os
import uuid
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.utils.db import get_db
from .embedding import embeddings, index

# 1. Load Documents from trusted sources
urls = [
    "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response",
    "https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions", 
    "https://www.helpguide.org/articles/anxiety/therapy-for-anxiety-disorders.htm",
    "https://www.mayoclinic.org/diseases-conditions/mental-illness/symptoms-causes/syc-20374968",
    "https://www.nimh.nih.gov/health/topics/anxiety-disorders"
    "https://www.kaggle.com/datasets/khushikyad001/mental-health-and-burnout-in-the-workplace"
]

docs = []
print("Loading documents from web sources...")

for url in urls:
    try:
        loader = WebBaseLoader(url)
        loaded_docs = loader.load()
        docs.extend(loaded_docs)
        print(f"✓ Loaded: {url}")
    except Exception as e:
        print(f"✗ Failed to load {url}: {e}")

# Optional: Load PDFs
# pdf_paths = ["path/to/cbt-techniques.pdf", "path/to/mental-health-guide.pdf"]
# for pdf_path in pdf_paths:
#     if os.path.exists(pdf_path):
#         loader = PyPDFLoader(pdf_path)
#         docs.extend(loader.load())
#         print(f"✓ Loaded PDF: {pdf_path}")

if not docs:
    print("❌ No documents loaded. Exiting.")
    exit()

# 2. Split Documents into chunks
print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, 
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = text_splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks")

# 3. Embed and upsert chunks into Pinecone
print("Adding documents to Pinecone knowledge base...")

vectors_to_upsert = []

for i, chunk in enumerate(chunks):
    try:
        # Create vector
        vector = embeddings.embed_query(chunk.page_content)
        
        # Create a unique ID
        vec_id = f"knowledge_{uuid.uuid4()}"
        
        # Prepare metadata - IMPORTANT: Include doc_type for filtering
        metadata = {
            "content": chunk.page_content,
            "source": chunk.metadata.get("source", "unknown"),
            "doc_type": "knowledge_base",  # This is crucial for filtering
            "chunk_index": i,
            "title": chunk.metadata.get("title", ""),
            "length": len(chunk.page_content)
        }
        
        vectors_to_upsert.append((vec_id, vector, metadata))
        
        # Batch upsert every 100 vectors for efficiency
        if len(vectors_to_upsert) >= 100:
            index.upsert(vectors_to_upsert, namespace="mental_wellness_knowledge")
            vectors_to_upsert = []
            print(f"Upserted batch ending at chunk {i}")
            
    except Exception as e:
        print(f"Error processing chunk {i}: {e}")

# Upsert remaining vectors
if vectors_to_upsert:
    index.upsert(vectors_to_upsert, namespace="mental_wellness_knowledge")

print(f"✅ Successfully ingested {len(chunks)} chunks of knowledge into Pinecone.")


# ==========================================
# ALIGNED: chat_service.py 
# ==========================================

