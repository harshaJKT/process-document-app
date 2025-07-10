import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Simple configuration
DATABASE_URL = "postgresql://postgres:password@localhost:5432/assignment"
UPLOAD_DIR = "uploads"
