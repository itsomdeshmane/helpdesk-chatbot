import os
from dotenv import load_dotenv
load_dotenv()

# Set to "false" to temporarily disable Pinecone and use in-memory storage
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() == "true"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") if USE_PINECONE else None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# NOTE: Index must have 1536 dimensions for OpenAI text-embedding-ada-002
# If you get dimension mismatch error, create new index with 1536 dimensions
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "erp-helpdesk")

# OpenAI Model Configuration
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4.1")

# MySQL Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "helpdesk_db")
