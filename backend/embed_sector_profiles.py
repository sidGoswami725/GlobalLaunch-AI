import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from vertexai.preview.language_models import TextEmbeddingModel
import vertexai

# === Setup ===

# Load environment variables from .env file
load_dotenv()

# Initialize Vertex AI with the correct project and region
vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location="us-central1"
)

# Load Gemini embedding model
model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

# Connect to MongoDB and select the relevant collection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["country_semantics"]

# Field name to store embeddings (dynamic via env variable)
SEMANTIC_EMBEDDING = os.getenv("SEMANTIC_EMBEDDING")

# Number of documents to process in one batch
BATCH_SIZE = 10

# === Embedding Loop ===

# Keep embedding documents until all summaries are processed
while True:
    # Fetch a batch of documents that:
    # - have a non-empty "summary" field
    # - do NOT already have an embedding stored
    docs = list(collection.find(
        {
            "summary": {"$exists": True, "$ne": ""},
            SEMANTIC_EMBEDDING: {"$exists": False}
        }
    ).limit(BATCH_SIZE))

    # Exit if all relevant documents are already embedded
    if not docs:
        print("✅ All documents embedded.")
        break

    # Process each document in the current batch
    for doc in docs:
        try:
            summary = doc["summary"]
            
            # Generate embedding from summary text
            embedding = model.get_embeddings([summary])[0].values

            # Store the embedding in the document
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {SEMANTIC_EMBEDDING: embedding}}
            )

            print(f"Embedded {doc['country_code']} - {doc['sector']}")
            
            # Respect Vertex AI rate limit (~5 requests/min)
            time.sleep(12.5)

        except Exception as e:
            print(f"Failed {doc.get('country_code')} - {doc.get('sector')}: {e}")
