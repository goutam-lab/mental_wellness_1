import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = None
db = None

try:
    client = MongoClient(MONGO_URI)
    db = client.get_database("eunoia")
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

def get_db():
    if db is None:
        raise Exception("Database connection is not available.")
    return db