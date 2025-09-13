import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# --- DATABASE CONNECTION ---
try:
    # Create a new client and connect to the server
    client = MongoClient(MONGO_URI)
    
    # Select your database (e.g., "eunoia_db").
    # The database will be created if it doesn't exist.
    db = client.get_database("eunoia")
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
    db = None

def get_db():
    """
    Returns the database instance.
    """
    if db is None:
        raise Exception("Database connection is not available.")
    return db